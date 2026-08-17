#!/usr/bin/env sh
set -eu

credential_file=/srv/xkjy-secrets/xkjy-admin-basic-password.txt
expected_ip=103.96.149.219
failures=0

check_status() {
  label=$1
  expected=$2
  shift 2
  actual=$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' "$@") || actual=curl-error
  if [ "$actual" = "$expected" ]; then
    printf 'PASS %-42s %s\n' "$label" "$actual"
  else
    printf 'FAIL %-42s expected=%s actual=%s\n' "$label" "$expected" "$actual" >&2
    failures=$((failures + 1))
  fi
}

for domain in \
  xkjy-api.orbexa.cc \
  xkjy-admin.orbexa.cc \
  xkjy-h5.orbexa.cc \
  xkjy-yq.orbexa.cc \
  xkjy-download.orbexa.cc \
  xkjy-assets.orbexa.cc
do
  resolved_ip=$(getent ahostsv4 "$domain" | awk 'NR == 1 { print $1 }')
  if [ "$resolved_ip" = "$expected_ip" ]; then
    printf 'PASS %-42s %s\n' "DNS $domain" "$resolved_ip"
  else
    printf 'FAIL %-42s expected=%s actual=%s\n' "DNS $domain" "$expected_ip" "${resolved_ip:-none}" >&2
    failures=$((failures + 1))
  fi

  check_status "HTTP status $domain" 301 "http://$domain/gateway-check"
  redirect_url=$(curl --silent --show-error --output /dev/null --write-out '%{redirect_url}' "http://$domain/gateway-check") || redirect_url=curl-error
  if [ "$redirect_url" = "https://$domain/gateway-check" ]; then
    printf 'PASS %-42s %s\n' "HTTP redirect $domain" "$redirect_url"
  else
    printf 'FAIL %-42s expected=%s actual=%s\n' "HTTP redirect $domain" "https://$domain/gateway-check" "$redirect_url" >&2
    failures=$((failures + 1))
  fi

  if printf '\n' | openssl s_client -connect "$domain:443" -servername "$domain" -verify_hostname "$domain" -verify_return_error >/dev/null 2>&1; then
    printf 'PASS %-42s verified\n' "TLS hostname $domain"
  else
    printf 'FAIL %-42s verification failed\n' "TLS hostname $domain" >&2
    failures=$((failures + 1))
  fi
done

check_status 'API /healthz' 200 https://xkjy-api.orbexa.cc/healthz
check_status 'API /api/healthz' 200 https://xkjy-api.orbexa.cc/api/healthz
check_status 'API /api/readyz' 200 https://xkjy-api.orbexa.cc/api/readyz
check_status 'API /api/v1/baseline' 200 https://xkjy-api.orbexa.cc/api/v1/baseline
check_status 'API unknown path boundary' 404 https://xkjy-api.orbexa.cc/not-implemented

check_status 'Admin unauthenticated boundary' 401 https://xkjy-admin.orbexa.cc/
admin_password=$(sed -n 's/^password=//p' "$credential_file")
if [ -z "$admin_password" ]; then
  printf 'FAIL %-42s missing password\n' 'Admin credential file' >&2
  failures=$((failures + 1))
else
  admin_status=$(
    printf 'user = "xkjy-admin:%s"\n' "$admin_password" | \
      curl --config - --silent --show-error --output /dev/null --write-out '%{http_code}' \
        https://xkjy-admin.orbexa.cc/
  ) || admin_status=curl-error
  if [ "$admin_status" = 200 ]; then
    printf 'PASS %-42s %s\n' 'Admin authenticated route' "$admin_status"
  else
    printf 'FAIL %-42s expected=200 actual=%s\n' 'Admin authenticated route' "$admin_status" >&2
    failures=$((failures + 1))
  fi
fi
unset admin_password

check_status 'H5 unpublished boundary' 404 https://xkjy-h5.orbexa.cc/not-implemented
check_status 'Invite unpublished boundary' 404 https://xkjy-yq.orbexa.cc/not-implemented
check_status 'Download unpublished boundary' 404 https://xkjy-download.orbexa.cc/not-implemented
check_status 'Assets unpublished boundary' 404 https://xkjy-assets.orbexa.cc/not-implemented

if [ "$failures" -ne 0 ]; then
  printf '%s\n' "Domain verification failed: $failures check(s)." >&2
  exit 1
fi

printf '%s\n' 'All XKJY domain checks passed.'
