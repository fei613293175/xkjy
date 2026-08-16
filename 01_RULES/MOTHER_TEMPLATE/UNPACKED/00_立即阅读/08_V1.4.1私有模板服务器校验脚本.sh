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
identity = yaml.safe_load(integrations_text)["identity"]
if identity["host"] != "https://sdfaceid.market.alicloudapi.com":
    raise SystemExit("identity host is not the V1.4.1 contract")
if identity["path"] != "/face_id_card/check":
    raise SystemExit("identity path is not the V1.4.1 contract")
if "kzfacev1" in integrations_text or "face_id_card_yi_suo" in integrations_text:
    raise SystemExit("deprecated identity contract is still executable")

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
    if path.is_file() and path.suffix.lower() in suffixes and path.name != "08_V1.4.1私有模板服务器校验脚本.sh"
)
for forbidden in ("505903963", "陈烈平"):
    if forbidden in combined:
        raise SystemExit("real transfer test data is present")

print("STRUCTURE_PARSE_PASS yaml=%d json=%d files=%d baseline_references=3" % (
    len(yaml_files), len(json_files), sum(1 for path in root.rglob("*") if path.is_file())
))
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
