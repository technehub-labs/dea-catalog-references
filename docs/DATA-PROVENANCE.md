# Data provenance

Every mirror in this repo traces back to an authoritative external source. This document records the source URL, the standard reference, and the snapshot date for each mirror.

## IANA media types (`data/media-types/iana-media-types.json`)

- **Source URL**: <https://www.iana.org/assignments/media-types/media-types.xml>
- **Standard**: RFC 6838 (Media Type Specifications and Registration Procedures)
- **Snapshot date**: 2026-10-16
- **Record count**: 2,305 unique media type names
- **Reproducible via**: `scripts/fetch-iana.sh` (re-fetch) + `scripts/parse-iana.py` (re-parse). The build is deterministic; only the snapshot date changes per fetch.
- **Audit hash**: see `data/SHA256SUMS` row 1

## IANA URI schemes (`data/uri-schemes/iana-uri-schemes.json`)

- **Source URL**: <https://www.iana.org/assignments/uri-schemes/uri-schemes.xml>
- **Sub-registry**: `uri-schemes-1` ("Uniform Resource Identifier (URI) Schemes"). The XML also contains three sibling sub-registries under `ipn-scheme-uri-*` (Ipn Scheme URI Allocator Identifiers, Default Allocator Node Numbers, Well-Known Service Numbers for BPv7); those are NOT mirrored here and would land as a separate slice if needed.
- **Standard**: RFC 3986 (URI Generic Syntax) + RFC 7595 (URI Scheme Registration Procedures)
- **Snapshot date**: 2026-10-16
- **Record count**: 451 unique URI scheme names (99 Permanent, 334 Provisional, 18 Historical)
- **Reproducible via**: `scripts/fetch-iana.sh` + `scripts/parse-iana.py`
- **Audit hash**: see `data/SHA256SUMS` row 2

## ECF 7 x 7 coordinates (`data/ecf-coordinates/coordinates.json`)

- **Source**: <https://github.com/technehub-labs/dea-metaframework/blob/main/framework/matrix.md> (file path `framework/matrix.md`)
- **Standard**: ECF (Enterprise Concept Framework), defined by the dea-metaframework repo. The matrix `M = D x S` is the framework's center of gravity; 49 coordinates = 7 Domains x 7 Stages.
- **Snapshot date**: 2026-10-16
- **Coordinate count**: 49 (7 domains x 7 stages)
- **Reproducible via**: `scripts/fetch-iana.sh` (also fetches the matrix.md) + `scripts/parse-ecf.py`
- **Audit hash**: see `data/SHA256SUMS` row 3

## Authority precedence

If any of the mirrors disagrees with its upstream source, the upstream source wins and the mirror is regenerated. Manual edits to the JSON mirrors are forbidden; the build script regenerates them from the source.

If a consumer of this mirror needs canonical authority, point at the upstream source URL above, not at this mirror.