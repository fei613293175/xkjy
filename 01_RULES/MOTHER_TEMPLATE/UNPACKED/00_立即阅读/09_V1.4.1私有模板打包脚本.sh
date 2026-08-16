#!/usr/bin/env bash
set -Eeuo pipefail

# Run only on the designated server after the private template is extracted.
root="$(cd "$1" && pwd)"
out_dir="$(cd "$2" && pwd)"
template_name="$(basename "$root")"
manifest="$root/MANIFEST_SHA256.txt"
zip_path="$out_dir/template-v141-private.zip"
sha_path="$out_dir/template-v141-private.sha256"

[[ -f "$root/TEMPLATE_STATUS.yaml" ]] || { echo "template root is invalid" >&2; exit 1; }
[[ ! -e "$zip_path" && ! -e "$sha_path" ]] || { echo "refusing to overwrite an existing package output" >&2; exit 1; }

python3 - "$root" <<'PY'
import hashlib
import os
import pathlib
import sys
import tempfile

root = pathlib.Path(sys.argv[1])
manifest = root / "MANIFEST_SHA256.txt"
paths = sorted(
    (path for path in root.rglob("*") if path.is_file() and path != manifest),
    key=lambda path: path.relative_to(root).as_posix(),
)
content = "".join(
    "%s  %s\n" % (
        hashlib.sha256(path.read_bytes()).hexdigest(),
        path.relative_to(root).as_posix(),
    )
    for path in paths
)
fd, temp_name = tempfile.mkstemp(prefix=".manifest-", dir=root)
try:
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_name, manifest)
except BaseException:
    try:
        os.unlink(temp_name)
    except FileNotFoundError:
        pass
    raise
print("MANIFEST_GENERATED entries=%d" % len(paths))
PY

python3 - "$root" <<'PY'
import hashlib
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
lines = (root / "MANIFEST_SHA256.txt").read_text(encoding="utf-8").splitlines()
if not lines:
    raise SystemExit("manifest is empty")
for line in lines:
    digest, relative = line.split("  ", 1)
    path = root / relative
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit("manifest verification failed: " + relative)
print("MANIFEST_VERIFY_PASS entries=%d" % len(lines))
PY

(
  cd "$(dirname "$root")"
  zip -q -r "$zip_path" "$template_name"
)
sha256sum "$zip_path" > "$sha_path"
unzip -tqq "$zip_path"

python3 - "$zip_path" <<'PY'
import pathlib
import sys
import zipfile

archive = zipfile.ZipFile(sys.argv[1])
names = archive.namelist()
if len(names) != len(set(names)):
    raise SystemExit("zip contains duplicate paths")
for name in names:
    path = pathlib.PurePosixPath(name)
    if name.startswith("/") or ".." in path.parts:
        raise SystemExit("zip contains dangerous path: " + name)
if not any(name.endswith("/MANIFEST_SHA256.txt") for name in names):
    raise SystemExit("zip does not contain manifest")
historical = {
    "实名认证接口截图_01.png",
    "实名认证接口截图_02.png",
    "输出内容(3)_原始资料.txt",
}
for filename in historical:
    if not any(name.endswith("/12_原始参考资料/" + filename) for name in names):
        raise SystemExit("zip is missing retained V1.3.0 baseline reference: " + filename)
if not any(name.endswith("/12_原始参考资料/来源说明.md") for name in names):
    raise SystemExit("zip is missing historical material isolation note")
print("ZIP_VALIDATE_PASS entries=%d duplicates=0 dangerous_paths=0 baseline_references=3" % len(names))
PY

printf "ZIP_OUTPUT bytes=%s\n" "$(stat -c '%s' "$zip_path")"
cat "$sha_path"
