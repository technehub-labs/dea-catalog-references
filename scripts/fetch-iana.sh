#!/usr/bin/env bash
# fetch-iana.sh -- re-fetch IANA XML sources and the dea-metaframework matrix.md
#
# Outputs (all to /tmp):
#   iana-media-types.xml
#   iana-uri-schemes.xml
#   ecf-matrix.md

set -euo pipefail

fetch() {
  local url="$1"
  local out="$2"
  echo "fetching $url -> $out"
  curl -sSfL --retry 3 --retry-delay 2 -o "$out" "$url"
}

fetch https://www.iana.org/assignments/media-types/media-types.xml   /tmp/iana-media-types.xml
fetch https://www.iana.org/assignments/uri-schemes/uri-schemes.xml   /tmp/iana-uri-schemes.xml
fetch https://raw.githubusercontent.com/technehub-labs/dea-metaframework/main/framework/matrix.md /tmp/ecf-matrix.md

echo "fetch complete"