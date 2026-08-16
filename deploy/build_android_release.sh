#!/usr/bin/env sh
set -eu

repository_dir=/srv/xkjy
secret_dir=/srv/xkjy-secrets
if [ "$#" -gt 0 ]; then repository_dir="$1"; fi
if [ "$#" -gt 1 ]; then secret_dir="$2"; fi
test -f "$secret_dir/android-signing.env"
test -f "$secret_dir/xkjy-p00-release.jks"

docker run --rm \
  --entrypoint gradle \
  --volume "$repository_dir:/src" \
  --volume "$secret_dir:/secrets:ro" \
  --workdir /src/android-app \
  --env-file "$secret_dir/android-signing.env" \
  hhy2-android-builder:latest \
  --no-daemon :app:testDebugUnitTest :app:assembleRelease
