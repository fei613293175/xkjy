import crypto from "node:crypto";
import fs from "node:fs/promises";

const clean = (value, limit = 500) => String(value ?? "").trim().slice(0, limit);
const enabled = (value) => String(value || "").toLowerCase() === "true";
const alipayTimestamp = (date = new Date()) => {
  const values = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
  }).formatToParts(date).reduce((result, part) => ({ ...result, [part.type]: part.value }), {});
  return `${values.year}-${values.month}-${values.day} ${values.hour}:${values.minute}:${values.second}`;
};
const canonical = (params) => Object.entries(params)
  .filter(([, value]) => value !== undefined && value !== null && value !== "")
  .sort(([left], [right]) => left.localeCompare(right))
  .map(([key, value]) => `${key}=${value}`).join("&");
const readPem = async (path) => {
  const target = clean(path, 1000);
  if (!target || !target.startsWith("/run/secrets/")) throw new Error("payout_secret_path_invalid");
  const value = await fs.readFile(target, "utf8");
  if (!value.includes("-----BEGIN")) throw new Error("payout_secret_pem_invalid");
  return value;
};
const publicKeyFingerprint = (key) => (key?.type === "public" ? key : crypto.createPublicKey(key))
  .export({ type: "spki", format: "der" }).toString("base64");
const skipWhitespace = (text, index) => {
  let cursor = index;
  while (/\s/.test(text[cursor] || "")) cursor += 1;
  return cursor;
};
const jsonStringEnd = (text, start) => {
  if (text[start] !== '"') return -1;
  let cursor = start + 1;
  while (cursor < text.length) {
    if (text[cursor] === "\\") { cursor += 2; continue; }
    if (text[cursor] === '"') return cursor + 1;
    cursor += 1;
  }
  return -1;
};
const jsonValueEnd = (text, start) => {
  const first = text[start];
  if (first === '"') return jsonStringEnd(text, start);
  if (first !== "{" && first !== "[") {
    let cursor = start;
    while (cursor < text.length && !/[\s,}\]]/.test(text[cursor])) cursor += 1;
    return cursor;
  }
  const closing = first === "{" ? "}" : "]";
  let depth = 0;
  let cursor = start;
  while (cursor < text.length) {
    if (text[cursor] === '"') {
      cursor = jsonStringEnd(text, cursor);
      if (cursor < 0) return -1;
      continue;
    }
    if (text[cursor] === first) depth += 1;
    if (text[cursor] === closing) {
      depth -= 1;
      if (depth === 0) return cursor + 1;
    }
    cursor += 1;
  }
  return -1;
};
// Alipay signs the original JSON representation of the response object. Do not
// re-serialize parsed JSON, and do not assume that `sign` follows the response.
const responsePayload = (raw, key) => {
  let cursor = skipWhitespace(raw, 0);
  if (raw[cursor] !== "{") return "";
  cursor += 1;
  while (cursor < raw.length) {
    cursor = skipWhitespace(raw, cursor);
    if (raw[cursor] === "}") return "";
    const keyStart = cursor;
    const keyEnd = jsonStringEnd(raw, keyStart);
    if (keyEnd < 0) return "";
    let property;
    try { property = JSON.parse(raw.slice(keyStart, keyEnd)); } catch { return ""; }
    cursor = skipWhitespace(raw, keyEnd);
    if (raw[cursor] !== ":") return "";
    const valueStart = skipWhitespace(raw, cursor + 1);
    const valueEnd = jsonValueEnd(raw, valueStart);
    if (valueEnd < 0) return "";
    if (property === key) return raw.slice(valueStart, valueEnd);
    cursor = skipWhitespace(raw, valueEnd);
    if (raw[cursor] !== ",") return "";
    cursor += 1;
  }
  return "";
};

export function createAlipayPayoutProvider(options = {}) {
  const gateway = clean(options.gateway ?? process.env.ALIPAY_PAYOUT_GATEWAY ?? "https://openapi.alipay.com/gateway.do", 1000);
  const appId = clean(options.appId ?? process.env.ALIPAY_PAYOUT_APP_ID, 100);
  const privateKeyPath = clean(options.privateKeyPath ?? process.env.ALIPAY_PAYOUT_PRIVATE_KEY_PATH, 1000);
  const appCertificatePath = clean(options.appCertificatePath ?? process.env.ALIPAY_PAYOUT_APP_CERT_PATH, 1000);
  const alipayCertificatePath = clean(options.alipayCertificatePath ?? process.env.ALIPAY_PAYOUT_ALIPAY_CERT_PATH, 1000);
  const rootCertificatePath = clean(options.rootCertificatePath ?? process.env.ALIPAY_PAYOUT_ROOT_CERT_PATH, 1000);
  const appCertificateSn = clean(options.appCertificateSn ?? process.env.ALIPAY_PAYOUT_APP_CERT_SN, 100);
  const rootCertificateSn = clean(options.rootCertificateSn ?? process.env.ALIPAY_PAYOUT_ROOT_CERT_SN, 500);
  const isEnabled = options.enabled ?? enabled(process.env.ALIPAY_PAYOUT_ENABLED);
  const allowInsecureGateway = options.allowInsecureGateway ?? process.env.NODE_ENV === "test";
  const loadPem = options.readPem || readPem;
  const request = options.fetch || fetch;
  const certificatePathsComplete = Boolean(appCertificatePath && alipayCertificatePath && rootCertificatePath);
  const certificateSerialsComplete = Boolean(appCertificateSn && rootCertificateSn);
  let loaded;
  let materialState = { checked: false, ready: false, errorCode: null };

  const configured = () => Boolean(
    isEnabled && appId && privateKeyPath && certificatePathsComplete && certificateSerialsComplete
    && (allowInsecureGateway || /^https:\/\//.test(gateway)),
  );
  const status = () => ({
    enabled: isEnabled,
    configured: configured(),
    ready: Boolean(isEnabled && materialState.ready),
    errorCode: materialState.errorCode,
    gateway: gateway.replace(/^https:\/\//, "").split("/")[0] || null,
    mode: "CERTIFICATE",
  });
  const initialize = async () => {
    if (!isEnabled) return status();
    if (!configured()) {
      materialState = { checked: true, ready: false, errorCode: "ALIPAY_PAYOUT_NOT_CONFIGURED" };
      return status();
    }
    if (!loaded) {
      loaded = Promise.all([loadPem(privateKeyPath), loadPem(appCertificatePath), loadPem(alipayCertificatePath), loadPem(rootCertificatePath)])
          .then(([privatePem, appCertificate, alipayCertificate, rootCertificate]) => {
            const privateKey = crypto.createPrivateKey(privatePem);
            const appPublicKey = crypto.createPublicKey(appCertificate);
            if (publicKeyFingerprint(privateKey) !== publicKeyFingerprint(appPublicKey)) {
              const error = new Error("ALIPAY_PAYOUT_APP_CERT_KEY_MISMATCH");
              error.code = "ALIPAY_PAYOUT_APP_CERT_KEY_MISMATCH";
              throw error;
            }
            // The serials are generated by Alipay's official SDK and supplied as
            // protected deployment configuration, avoiding provider-specific X.509
            // issuer formatting differences between runtimes.
            if (!String(rootCertificate).includes("-----BEGIN CERTIFICATE-----")) {
              const error = new Error("ALIPAY_PAYOUT_ROOT_CERT_INVALID");
              error.code = "ALIPAY_PAYOUT_ROOT_CERT_INVALID";
              throw error;
            }
            return { privateKey, publicKey: crypto.createPublicKey(alipayCertificate), appCertificateSn, rootCertificateSn };
          });
    }
    try {
      await loaded;
      materialState = { checked: true, ready: true, errorCode: null };
    } catch (error) {
      loaded = undefined;
      materialState = { checked: true, ready: false, errorCode: error?.code || "ALIPAY_PAYOUT_CERT_INVALID" };
    }
    return status();
  };
  const material = async () => {
    await initialize();
    if (!materialState.ready || !loaded) {
      const error = new Error(materialState.errorCode || "ALIPAY_PAYOUT_NOT_READY");
      error.code = materialState.errorCode || "ALIPAY_PAYOUT_NOT_READY";
      throw error;
    }
    return loaded;
  };
  const call = async (method, bizContent) => {
    const keys = await material();
    const params = {
      app_id: appId, charset: "utf-8", format: "JSON", method, sign_type: "RSA2",
      timestamp: alipayTimestamp(), version: "1.0", biz_content: JSON.stringify(bizContent),
    };
    params.app_cert_sn = keys.appCertificateSn;
    params.alipay_root_cert_sn = keys.rootCertificateSn;
    params.sign = crypto.sign("RSA-SHA256", Buffer.from(canonical(params), "utf8"), keys.privateKey).toString("base64");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    let raw;
    try {
      const response = await request(gateway, {
        method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded; charset=utf-8" },
        body: new URLSearchParams(params).toString(), signal: controller.signal,
      });
      raw = await response.text();
      if (!response.ok) {
        const error = new Error("ALIPAY_PAYOUT_HTTP_ERROR");
        error.code = "ALIPAY_PAYOUT_HTTP_ERROR";
        throw error;
      }
    } catch (error) {
      if (!error.code) error.code = error.name === "AbortError" ? "ALIPAY_PAYOUT_TIMEOUT" : "ALIPAY_PAYOUT_NETWORK_ERROR";
      throw error;
    } finally { clearTimeout(timeout); }
    let parsed;
    try { parsed = JSON.parse(raw); } catch {
      const error = new Error("ALIPAY_PAYOUT_RESPONSE_INVALID"); error.code = "ALIPAY_PAYOUT_RESPONSE_INVALID"; throw error;
    }
    const responseKey = method.replaceAll(".", "_") + "_response";
    const payload = parsed[responseKey];
    const signature = clean(parsed.sign, 5000);
    const signedPayload = responsePayload(raw, responseKey);
    if (!payload || !signature || !signedPayload || !crypto.verify("RSA-SHA256", Buffer.from(signedPayload, "utf8"), keys.publicKey, Buffer.from(signature, "base64"))) {
      const error = new Error("ALIPAY_PAYOUT_SIGNATURE_INVALID"); error.code = "ALIPAY_PAYOUT_SIGNATURE_INVALID"; throw error;
    }
    return payload;
  };

  return {
    status,
    initialize,
    transfer: async ({ outBizNo, amount, account, name, remark, title }) => {
      const parsedAmount = Number(amount);
      if (!Number.isFinite(parsedAmount) || parsedAmount <= 0) {
        const error = new Error("ALIPAY_PAYOUT_AMOUNT_INVALID"); error.code = "ALIPAY_PAYOUT_AMOUNT_INVALID"; throw error;
      }
      const result = await call("alipay.fund.trans.uni.transfer", {
        out_biz_no: clean(outBizNo, 64), trans_amount: parsedAmount.toFixed(2), product_code: "TRANS_ACCOUNT_NO_PWD",
        biz_scene: "DIRECT_TRANSFER", order_title: clean(title || "用户提现", 100), remark: clean(remark, 200),
        // The payer alias is maintained and reviewed by Alipay. This flag asks
        // Alipay to show that approved merchant name instead of the legal entity.
        business_params: JSON.stringify({ payer_show_name_use_alias: "true" }),
        payee_info: { identity: clean(account, 100), identity_type: "ALIPAY_LOGON_ID", name: clean(name, 40) },
      });
      const transferStatus = clean(result.status, 40).toUpperCase();
      return { success: result.code === "10000" && transferStatus === "SUCCESS" && Boolean(result.order_id),
        pending: result.code === "10000" && ["DEALING", "WAIT_PAY"].includes(transferStatus),
        terminalFailure: result.code === "10000" && ["FAIL", "CLOSED", "REFUND"].includes(transferStatus),
        code: clean(result.code, 40), message: clean(result.sub_msg || result.msg, 500),
        reference: clean(result.order_id, 200), rawStatus: transferStatus };
    },
    query: async ({ outBizNo }) => {
      const result = await call("alipay.fund.trans.common.query", {
        product_code: "TRANS_ACCOUNT_NO_PWD", biz_scene: "DIRECT_TRANSFER", out_biz_no: clean(outBizNo, 64),
      });
      const orderStatus = clean(result.status, 40).toUpperCase();
      const subCode = clean(result.sub_code, 80);
      return { found: result.code === "10000", missing: result.code === "40004" && /NOT_EXIST|NOT_FOUND/i.test(subCode),
        successful: result.code === "10000" && orderStatus === "SUCCESS",
        terminalFailure: result.code === "10000" && ["FAIL", "CLOSED"].includes(orderStatus), code: clean(result.code, 40),
        message: clean(result.sub_msg || result.msg, 500), reference: clean(result.order_id, 200), status: orderStatus };
    },
  };
}
