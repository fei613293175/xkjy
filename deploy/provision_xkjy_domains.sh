#!/usr/bin/env sh
set -eu

# Run as root on the connected deployment server. No project build runs here.
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
nginx_config_source=${1:-"$script_dir/nginx/xkjy-domains.conf"}
proxy_params_source=${2:-"$script_dir/nginx/xkjy-proxy-params.inc"}
nginx_config=/www/server/panel/vhost/nginx/xkjy-domains.conf
proxy_params=/www/server/panel/vhost/nginx/xkjy-proxy-params.inc
cert_dir=/www/server/panel/vhost/cert/xkjy.orbexa.cc_ecc
acme_cert_dir=/root/.acme.sh/xkjy-api.orbexa.cc_ecc
auth_dir=/www/server/nginx/conf/auth
auth_file=$auth_dir/xkjy-admin.htpasswd
secret_dir=/srv/xkjy-secrets
credential_file=$secret_dir/xkjy-admin-basic-password.txt
acme_sh=/root/.acme.sh/acme.sh
webroot=/www/server/nginx/html

if [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "This script must run as root." >&2
  exit 1
fi

for required_file in "$nginx_config_source" "$proxy_params_source" "$acme_sh"; do
  if [ ! -f "$required_file" ]; then
    printf 'Required file not found: %s\n' "$required_file" >&2
    exit 1
  fi
done

if ! getent group www >/dev/null 2>&1; then
  printf '%s\n' "Required Nginx worker group 'www' was not found." >&2
  exit 1
fi

umask 077
install -d -o root -g root -m 700 "$secret_dir"
install -d -o root -g www -m 750 "$auth_dir"
install -d -o root -g root -m 700 "$cert_dir"

work_dir=$(mktemp -d /tmp/xkjy-domains.XXXXXX)
trap 'rm -rf -- "$work_dir"' EXIT HUP INT TERM

if [ ! -f "$auth_file" ] || [ ! -f "$credential_file" ]; then
  admin_password=$(openssl rand -hex 24)
  password_hash=$(printf '%s\n' "$admin_password" | openssl passwd -6 -stdin)
  printf 'xkjy-admin:%s\n' "$password_hash" > "$work_dir/xkjy-admin.htpasswd"
  {
    printf '%s\n' 'username=xkjy-admin'
    printf 'password=%s\n' "$admin_password"
  } > "$work_dir/xkjy-admin-basic-password.txt"
  install -o root -g www -m 640 "$work_dir/xkjy-admin.htpasswd" "$auth_file"
  install -o root -g root -m 600 "$work_dir/xkjy-admin-basic-password.txt" "$credential_file"
fi

if [ ! -f "$acme_cert_dir/fullchain.cer" ] || [ ! -f "$acme_cert_dir/xkjy-api.orbexa.cc.key" ]; then
  "$acme_sh" --issue --server letsencrypt --ecc --keylength ec-256 \
    -w "$webroot" \
    -d xkjy-api.orbexa.cc \
    -d xkjy-admin.orbexa.cc \
    -d xkjy-h5.orbexa.cc \
    -d xkjy-yq.orbexa.cc \
    -d xkjy-download.orbexa.cc \
    -d xkjy-assets.orbexa.cc
fi

"$acme_sh" --install-cert --ecc -d xkjy-api.orbexa.cc \
  --key-file "$cert_dir/privkey.pem" \
  --fullchain-file "$cert_dir/fullchain.pem" \
  --reloadcmd "nginx -t && nginx -s reload"
chmod 600 "$cert_dir/privkey.pem" "$cert_dir/fullchain.pem"

nginx_config_existed=false
proxy_params_existed=false
if [ -f "$nginx_config" ]; then
  nginx_config_existed=true
  cp -p "$nginx_config" "$work_dir/xkjy-domains.conf.backup"
fi
if [ -f "$proxy_params" ]; then
  proxy_params_existed=true
  cp -p "$proxy_params" "$work_dir/xkjy-proxy-params.inc.backup"
fi
install -o root -g root -m 644 "$nginx_config_source" "$nginx_config"
install -o root -g root -m 644 "$proxy_params_source" "$proxy_params"

if ! nginx -t; then
  if [ "$nginx_config_existed" = true ]; then
    install -o root -g root -m 644 "$work_dir/xkjy-domains.conf.backup" "$nginx_config"
  else
    rm -f -- "$nginx_config"
  fi
  if [ "$proxy_params_existed" = true ]; then
    install -o root -g root -m 644 "$work_dir/xkjy-proxy-params.inc.backup" "$proxy_params"
  else
    rm -f -- "$proxy_params"
  fi
  nginx -t
  printf '%s\n' 'New Nginx configuration was rejected; the previous configuration was restored.' >&2
  exit 1
fi
nginx -s reload

test "$(stat -c '%a' "$credential_file")" = 600
test "$(stat -c '%a' "$auth_file")" = 640
printf '%s\n' "XKJY domain gateway provisioned. Admin credentials remain in $credential_file"
