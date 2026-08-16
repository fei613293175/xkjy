#!/usr/bin/env bash
set -Eeuo pipefail

# This script installs the four private certificate-mode files from an already
# extracted private project package. It never reads legacy plugin directories.
source_dir="${ALIPAY_PAYOUT_SOURCE_DIR:?set ALIPAY_PAYOUT_SOURCE_DIR to the extracted private credential directory}"
target_dir="${ALIPAY_PAYOUT_SECRET_DIR:-/opt/project/secrets/alipay-payout}"

[[ -d "$source_dir" ]] || { echo "private credential directory is unavailable" >&2; exit 1; }
for file in private.pem app-cert.pem alipay-cert.pem root-cert.pem; do
  [[ -r "$source_dir/$file" ]] || { echo "required certificate material is unavailable: $file" >&2; exit 1; }
done

stage="$(mktemp -d "${TMPDIR:-/tmp}/alipay-payout.XXXXXX")
cleanup() { rm -rf -- "$stage"; }
trap cleanup EXIT

for file in private.pem app-cert.pem alipay-cert.pem root-cert.pem; do
  install -m 0600 "$source_dir/$file" "$stage/$file"
done

openssl pkey -in "$stage/private.pem" -noout >/dev/null
openssl x509 -in "$stage/app-cert.pem" -noout >/dev/null
openssl x509 -in "$stage/alipay-cert.pem" -noout >/dev/null
openssl crl2pkcs7 -nocrl -certfile "$stage/root-cert.pem" | openssl pkcs7 -print_certs -noout >/dev/null

private_public="$(openssl pkey -in "$stage/private.pem" -pubout -outform DER | sha256sum | cut -d' ' -f1)"
certificate_public="$(openssl x509 -in "$stage/app-cert.pem" -pubkey -noout | openssl pkey -pubin -pubout -outform DER | sha256sum | cut -d' ' -f1)"
[[ "$private_public" == "$certificate_public" ]] || { echo "private key does not match app certificate" >&2; exit 1; }

install -d -m 0700 "$target_dir"
for file in private.pem app-cert.pem alipay-cert.pem root-cert.pem; do
  install -m 0600 "$stage/$file" "$target_dir/$file"
done

echo "ALIPAY_PAYOUT_CERTIFICATES_INSTALLED mode=certificate files=4"
