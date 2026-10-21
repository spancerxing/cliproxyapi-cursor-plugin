#!/usr/bin/env bash
set -euo pipefail

# Run inside the native-architecture manylinux2014 container with GOROOT mounted.
export PATH="/usr/local/go/bin:$PATH"
CGO_ENABLED=1 go build -buildvcs=false -trimpath -buildmode=c-shared \
  -o dist/spancerxing-cursor.so .

python3 - <<'PY'
import re
import subprocess

output = subprocess.check_output(
    ["readelf", "--version-info", "dist/spancerxing-cursor.so"], text=True
)
versions = [tuple(map(int, version)) for version in re.findall(r"GLIBC_(\d+)\.(\d+)", output)]
assert versions and max(versions) <= (2, 17), "glibc baseline exceeded"
print("Linux library requires glibc <= 2.17")
PY
