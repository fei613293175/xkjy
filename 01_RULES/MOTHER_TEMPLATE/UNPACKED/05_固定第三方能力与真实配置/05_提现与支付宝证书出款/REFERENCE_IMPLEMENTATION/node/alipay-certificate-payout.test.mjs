import assert from "node:assert/strict";
import crypto from "node:crypto";
import { createAlipayPayoutProvider } from "./alipay-certificate-payout.js";

const { privateKey, publicKey } = crypto.generateKeyPairSync("rsa", { modulusLength: 2048 });
const canonical = (params) => Object.entries(params).filter(([, value]) => value !== "")
  .sort(([left], [right]) => left.localeCompare(right)).map(([key, value]) => `${key}=${value}`).join("&");
const response = (key, payload, validSignature = true) => {
  const json = JSON.stringify(payload);
  const sign = validSignature
    ? crypto.sign("RSA-SHA256", Buffer.from(json, "utf8"), privateKey).toString("base64")
    : "invalid";
  return new Response(`{\"${key}\":${json},\"sign\":\"${sign}\"}`, { status: 200 });
};
const provider = (fetch) => createAlipayPayoutProvider({
  enabled: true,
  appId: "2026000000000000",
  gateway: "https://gateway.example.test/gateway.do",
  privateKeyPath: "/run/secrets/alipay-payout/private.pem",
  appCertificatePath: "/run/secrets/alipay-payout/app-cert.pem",
  alipayCertificatePath: "/run/secrets/alipay-payout/alipay-cert.pem",
  rootCertificatePath: "/run/secrets/alipay-payout/root-cert.pem",
  appCertificateSn: "app-cert-sn-test",
  rootCertificateSn: "root-cert-sn-test",
  readPem: async (path) => {
    if (path.endsWith("private.pem")) return privateKey.export({ type: "pkcs8", format: "pem" });
    if (path.endsWith("root-cert.pem")) return "-----BEGIN CERTIFICATE-----\ntest-root-certificate\n-----END CERTIFICATE-----";
    return publicKey.export({ type: "spki", format: "pem" });
  },
  fetch,
});

const verifiedFetch = async (_url, options) => {
  const params = Object.fromEntries(new URLSearchParams(options.body));
  const signature = Buffer.from(params.sign, "base64");
  delete params.sign;
  assert.equal(params.app_cert_sn, "app-cert-sn-test");
  assert.equal(params.alipay_root_cert_sn, "root-cert-sn-test");
  assert.equal(crypto.verify("RSA-SHA256", Buffer.from(canonical(params), "utf8"), publicKey, signature), true);
  if (params.method === "alipay.fund.trans.uni.transfer") {
    const content = JSON.parse(params.biz_content);
    assert.equal(content.out_biz_no, "TEST-WITHDRAWAL-P1");
    assert.equal(content.trans_amount, "0.30");
    assert.equal(content.payee_info.identity, "payout-user@example.test");
    assert.equal(content.payee_info.name, "测试用户");
    assert.deepEqual(JSON.parse(content.business_params), { payer_show_name_use_alias: "true" });
    return response("alipay_fund_trans_uni_transfer_response", { code: "10000", msg: "Success", order_id: "test-provider-order", status: "SUCCESS" });
  }
  return response("alipay_fund_trans_common_query_response", { code: "10000", msg: "Success", order_id: "test-provider-order", status: "SUCCESS" });
};

const service = provider(verifiedFetch);
await service.initialize();
assert.deepEqual(service.status(), { enabled: true, configured: true, ready: true, errorCode: null, gateway: "gateway.example.test", mode: "CERTIFICATE" });
const paid = await service.transfer({ outBizNo: "TEST-WITHDRAWAL-P1", amount: "0.30", account: "payout-user@example.test", name: "测试用户", remark: "测试备注", title: "测试提现" });
assert.equal(paid.success, true);
assert.equal((await service.query({ outBizNo: "TEST-WITHDRAWAL-P1" })).successful, true);
await assert.rejects(
  () => provider(async () => response("alipay_fund_trans_uni_transfer_response", { code: "10000", status: "SUCCESS" }, false))
    .transfer({ outBizNo: "BAD-SIGNATURE", amount: "0.30", account: "payout-user@example.test", name: "测试用户" }),
  (error) => error.code === "ALIPAY_PAYOUT_SIGNATURE_INVALID",
);
const processing = await provider(async () => response("alipay_fund_trans_uni_transfer_response", { code: "10000", order_id: "processing", status: "DEALING" }))
  .transfer({ outBizNo: "PROCESSING", amount: "0.30", account: "payout-user@example.test", name: "测试用户" });
assert.equal(processing.pending, true);
console.log(JSON.stringify({ ok: true, certificateModeOnly: true, requestSignature: true, responseSignature: true, invalidSignatureRejected: true }));
