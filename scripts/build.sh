#!/usr/bin/env bash
# build.sh -- regenerate JSON mirrors + static landing pages for dea-catalog-references
#
# Usage:  ./scripts/build.sh           # rebuild from cached /tmp/*.xml sources
#         ./scripts/build.sh --fetch   # re-fetch IANA sources before rebuild
#
# Outputs (all under repo root):
#   data/media-types/iana-media-types.json
#   data/uri-schemes/iana-uri-schemes.json
#   data/ecf-coordinates/coordinates.json
#   data/SHA256SUMS
#   media-types/index.html                          master listing (2,366 records)
#   media-types/by-type/<type>.html                 per-type listing (10 files)
#   media-types/<type>/<subtype>.html               per-record page (2,366 files)
#   uri-schemes/index.html                          master listing (451 records)
#   uri-schemes/<scheme>.html                       per-record page (451 files)
#   ecf/index.html
#   ecf/<domain>/<stage>.html                       per-cell page (49 files)

set -euo pipefail
cd "$(dirname "$0")/.."

DO_FETCH=0
if [ "$#" -gt 0 ]; then
  for arg in "$@"; do
    case "$arg" in
      --fetch) DO_FETCH=1 ;;
      *) echo "Unknown arg: $arg" >&2; exit 2 ;;
    esac
  done
fi

mkdir -p data/media-types data/uri-schemes data/ecf-coordinates media-types/by-type uri-schemes ecf

if [ "$DO_FETCH" = "1" ]; then
  bash scripts/fetch-iana.sh
fi

python3 scripts/parse-iana.py
python3 scripts/parse-ecf.py
python3 scripts/build-html.py

( cd data && sha256sum media-types/iana-media-types.json uri-schemes/iana-uri-schemes.json ecf-coordinates/coordinates.json ) > data/SHA256SUMS

python3 scripts/validate-data.py 2>&1 | grep -v "^  warn:" || true  # warnings are upstream data oddities
python3 scripts/validate-data.py >/dev/null  # the gate

echo "build complete; SHA256SUMS:"
cat data/SHA256SUMS