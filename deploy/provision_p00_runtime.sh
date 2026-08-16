#!/usr/bin/env sh
set -eu

# Runs only on the connected server. It writes generated P00 secrets outside Git.
secret_dir=/srv/xkjy-secrets
if [ "$#" -gt 0 ]; then secret_dir="$1"; fi
runtime_file="$secret_dir/runtime.env"
signing_file="$secret_dir/android-signing.env"
keystore_file="$secret_dir/xkjy-p00-release.jks"

umask 077
install -d -m 700 "$secret_dir"

if [ ! -f "$runtime_file" ]; then
  db_password="$(openssl rand -hex 24)"
  {
    printf "%s\n" "APP_ENV=production"
    printf "%s\n" "HTTP_ADDR=:8080"
    printf "%s\n" "REQUIRE_DEPENDENCIES=true"
    printf "%s\n" "POSTGRES_DB=xkjy"
    printf "%s\n" "POSTGRES_USER=xkjy"
    printf "POSTGRES_PASSWORD=%s\n" "$db_password"
    printf "DATABASE_URL=postgres://xkjy:%s@postgres:5432/xkjy?sslmode=disable\n" "$db_password"
    printf "%s\n" "REDIS_URL=redis://redis:6379/0"
  } > "$runtime_file"
  chmod 600 "$runtime_file"
fi

if [ ! -f "$signing_file" ]; then
  store_password="$(openssl rand -hex 24)"
  key_password="$(openssl rand -hex 24)"
  keytool -genkeypair -v -keystore "$keystore_file" -storetype JKS -storepass "$store_password" -keypass "$key_password" -alias xkjy-p00 -keyalg RSA -keysize 4096 -validity 3650 -dname "CN=XKJY P00, OU=Engineering, O=Orbexa, C=CN" >/dev/null
  {
    printf "%s\n" "ANDROID_KEYSTORE_FILE=/secrets/xkjy-p00-release.jks"
    printf "ANDROID_KEYSTORE_PASSWORD=%s\n" "$store_password"
    printf "%s\n" "ANDROID_KEY_ALIAS=xkjy-p00"
    printf "ANDROID_KEY_PASSWORD=%s\n" "$key_password"
  } > "$signing_file"
  chmod 600 "$signing_file" "$keystore_file"
fi

test "$(stat -c "%a" "$secret_dir")" = 700
test "$(stat -c "%a" "$runtime_file")" = 600
test "$(stat -c "%a" "$signing_file")" = 600
test "$(stat -c "%a" "$keystore_file")" = 600
printf "%s\n" "P00 server runtime provisioned at $secret_dir"
