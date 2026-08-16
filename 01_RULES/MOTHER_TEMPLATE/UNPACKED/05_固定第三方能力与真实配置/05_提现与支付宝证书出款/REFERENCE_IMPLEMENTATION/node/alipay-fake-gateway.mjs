import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";

const port = Number(process.env.PORT || 8080);
const privateKey = crypto.createPrivateKey(fs.readFileSync(process.env.GATEWAY_PRIVATE_KEY, "utf8"));
let transferCount = 0;
const response = (method, payload) => {
  const key = method.replaceAll(".", "_") + "_response";
  const body = JSON.stringify(payload);
  const sign = crypto.sign("RSA-SHA256", Buffer.from(body), privateKey).toString("base64");
  return JSON.stringify({ sign, trace_id: "fake-r20", [key]: payload });
};
const server = http.createServer((request, result) => {
  const chunks = [];
  request.on("data", (chunk) => chunks.push(chunk));
  request.on("end", () => {
    const params = new URLSearchParams(Buffer.concat(chunks).toString("utf8"));
    const method = params.get("method");
    let payload;
    if (method === "alipay.fund.trans.uni.transfer") {
      transferCount += 1;
      const content = JSON.parse(params.get("biz_content") || "{}");
      payload = transferCount === 2
        ? { code: "10000", msg: "Success", order_id: `FAKE-${transferCount}`, out_biz_no: content.out_biz_no, status: "DEALING" }
        : { code: "10000", msg: "Success", order_id: `FAKE-${transferCount}`, out_biz_no: content.out_biz_no, status: "SUCCESS" };
    } else {
      payload = { code: "10000", msg: "Success", order_id: "FAKE-2", status: "DEALING" };
    }
    result.writeHead(200, { "Content-Type": "application/json" });
    result.end(response(method, payload));
  });
});
server.listen(port, "0.0.0.0", () => console.log(`fake_gateway_ready:${port}`));
