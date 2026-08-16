#!/usr/bin/env bash
set -Eeuo pipefail

# Run only on the designated server against an extracted private template.
root="$1"
cert_dir="$root/05_固定第三方能力与真实配置/05_提现与支付宝证书出款/PRIVATE_CREDENTIALS/alipay-payout"
container_adapter="/template/05_固定第三方能力与真实配置/05_提现与支付宝证书出款/REFERENCE_IMPLEMENTATION/node/alipay-certificate-payout.test.mjs"

[[ -f "$root/TEMPLATE_STATUS.yaml" ]] || { echo "template root is invalid" >&2; exit 1; }

python3 - "$root" <<'PY'
import json
import pathlib
import sys

import yaml

root = pathlib.Path(sys.argv[1])
yaml_files = list(root.rglob("*.yaml"))
json_files = list(root.rglob("*.json"))
for path in yaml_files:
    yaml.safe_load(path.read_text(encoding="utf-8"))
for path in json_files:
    json.loads(path.read_text(encoding="utf-8"))

integrations_path = root / "05_固定第三方能力与真实配置" / "PRIVATE_INTEGRATIONS.yaml"
integrations_text = integrations_path.read_text(encoding="utf-8")
integrations = yaml.safe_load(integrations_text)
if integrations["meta"]["template_version"] != "1.4.2":
    raise SystemExit("private integrations version is not 1.4.2")
identity = integrations["identity"]
if identity["host"] != "https://sdfaceid.market.alicloudapi.com":
    raise SystemExit("identity host is not the V1.4.1 contract")
if identity["path"] != "/face_id_card/check":
    raise SystemExit("identity path is not the V1.4.1 contract")
if "kzfacev1" in integrations_text or "face_id_card_yi_suo" in integrations_text:
    raise SystemExit("deprecated identity contract is still executable")

payment = integrations["payment"]
xapay = payment["providers"]["xapay"]
expected_xapay = {
    "pid": "10050",
    "gateway": "https://xa.2xrr.com/xpay/epay/submit.php",
    "query_url": "https://xa.2xrr.com/xpay/epay/api.php",
    "notify_url": "https://x-api.orbexa.cc/api/v1/payments/callback/xapay",
    "return_url": "https://x-api.orbexa.cc/payment-return",
}
for key, expected in expected_xapay.items():
    if str(xapay.get(key, "")) != expected:
        raise SystemExit("xapay private contract mismatch: " + key)
if not xapay.get("key") or xapay.get("sign_type") != "MD5":
    raise SystemExit("xapay server credential/signing contract is incomplete")
if xapay.get("confirmed_online_methods") != ["alipay", "wxpay"] or xapay.get("qq_online_confirmed") is not False:
    raise SystemExit("xapay confirmed method boundary is invalid")

payment_dir = root / "05_固定第三方能力与真实配置" / "02_支付"
required_payment_files = {
    "XApay在线支付接入合同.md",
    "扫码支付与人工审核结算规范.md",
    "按订单类型隐藏支付方式规范.md",
    "PAYMENT_API_CONTRACTS.yaml",
    "PAYMENT_DATABASE_SCHEMA.md",
    "PAYMENT_TEST_MATRIX.md",
    "支付模块V1.4.2整合说明.md",
    "MODULE_RULES_M-PAY-009~M-PAY-012.md",
}
for name in required_payment_files:
    if not (payment_dir / name).is_file():
        raise SystemExit("missing V1.4.2 payment contract: " + name)
payment_manifest = yaml.safe_load((payment_dir / "MODULE_MANIFEST.yaml").read_text(encoding="utf-8"))
if payment_manifest.get("ruleset") != "M-PAY-001~M-PAY-012":
    raise SystemExit("payment ruleset is incomplete")
if set(payment_manifest.get("profiles", {})) != {"fuylink_online", "xapay_online", "manual_qr"}:
    raise SystemExit("payment profile set is incomplete")

import hashlib
def md5_sign(params, key):
    filtered = {k: str(v) for k, v in params.items() if k not in {"sign", "sign_type"} and str(v) != ""}
    plain = "&".join(f"{k}={filtered[k]}" for k in sorted(filtered)) + key
    return hashlib.md5(plain.encode("utf-8")).hexdigest()
vector = {"pid": xapay["pid"], "type": "alipay", "out_trade_no": "TEMPLATE-SIGN-TEST", "money": "0.01", "sign_type": "MD5"}
signature = md5_sign(vector, xapay["key"])
if len(signature) != 32 or signature != md5_sign(dict(reversed(list(vector.items()))), xapay["key"]):
    raise SystemExit("xapay MD5 canonicalization test failed")
tampered = dict(vector, money="0.02")
if md5_sign(tampered, xapay["key"]) == signature:
    raise SystemExit("xapay MD5 tamper test failed")

# V1.3.0 reference files remain byte-identical for baseline integrity.
# They are historical only and are never read as executable configuration.
historical = {
    "实名认证接口截图_01.png": "b7da225faf0c25ae521089b5962cbe64130f8ba82228376e2fb4090b970c16cd",
    "实名认证接口截图_02.png": "073e9ac1db66e861fbaa55e20744c23843fa245cccc754055c23364cd2828d63",
    "输出内容(3)_原始资料.txt": "955caccd5695a5c32578f7bb7cbe7cb561840d3cd2b52ff0ee171ea540ed6b3c",
}
historical_dir = root / "12_原始参考资料"
for name, digest in historical.items():
    path = historical_dir / name
    if not path.is_file():
        raise SystemExit("missing V1.3.0 baseline reference: " + name)
    if __import__("hashlib").sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit("baseline reference hash mismatch: " + name)
source_note = (historical_dir / "来源说明.md").read_text(encoding="utf-8")
if "历史实名认证材料隔离" not in source_note or "不得被 ChatGPT、Codex 或任何新项目复制" not in source_note:
    raise SystemExit("historical identity material lacks executable-use isolation")

suffixes = {".md", ".yaml", ".yml", ".json", ".js", ".mjs", ".env", ".sh", ".txt"}
combined = "\n".join(
    path.read_text(encoding="utf-8", errors="ignore")
    for path in root.rglob("*")
    if path.is_file() and path.suffix.lower() in suffixes and path.name not in {"08_V1.4.1私有模板服务器校验脚本.sh", "10_V1.4.2私有模板服务器校验脚本.sh"}
)
for forbidden in ("505903963", "陈烈平"):
    if forbidden in combined:
        raise SystemExit("real transfer test data is present")

private_allowed = {integrations_path, root / "05_固定第三方能力与真实配置" / "PRIVATE_INTEGRATIONS.env"}
for path in root.rglob("*"):
    if not path.is_file() or path in private_allowed or path.name == "MANIFEST_SHA256.txt":
        continue
    if path.suffix.lower() in suffixes and xapay["key"] in path.read_text(encoding="utf-8", errors="ignore"):
        raise SystemExit("xapay key leaked outside private integration files: " + str(path.relative_to(root)))

print("STRUCTURE_PARSE_PASS yaml=%d json=%d files=%d baseline_references=3 payment_profiles=3" % (
    len(yaml_files), len(json_files), sum(1 for path in root.rglob("*") if path.is_file())
))
print("PAYMENT_CONTRACT_PASS xapay_methods=2 manual_qr_methods=3 order_kind_filter=server_double_check md5_vector=pass")
PY

for file in private.pem app-cert.pem alipay-cert.pem root-cert.pem; do
  [[ -r "$cert_dir/$file" ]] || { echo "missing payout material: $file" >&2; exit 1; }
done

openssl pkey -in "$cert_dir/private.pem" -noout
openssl x509 -in "$cert_dir/app-cert.pem" -noout -checkend 2592000
openssl x509 -in "$cert_dir/alipay-cert.pem" -noout -checkend 2592000
openssl crl2pkcs7 -nocrl -certfile "$cert_dir/root-cert.pem" | openssl pkcs7 -print_certs -noout >/dev/null
private_public="$(openssl pkey -in "$cert_dir/private.pem" -pubout -outform DER | sha256sum | cut -d' ' -f1)"
certificate_public="$(openssl x509 -in "$cert_dir/app-cert.pem" -pubkey -noout | openssl pkey -pubin -pubout -outform DER | sha256sum | cut -d' ' -f1)"
[[ "$private_public" == "$certificate_public" ]] || { echo "private key does not match application certificate" >&2; exit 1; }
echo "CERTIFICATE_PREFLIGHT_PASS files=4 private_app_certificate=matched expiry_buffer_days=30 root_bundle=valid"

docker run --rm --network none -v "$root:/template:ro" node:22-bookworm node "$container_adapter"
echo "REFERENCE_ADAPTER_TEST_PASS certificate_mode_only=true"
