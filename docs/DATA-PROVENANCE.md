# Data provenance

Every mirror in this repo traces back to an authoritative external source. This document records the source URL, the standard reference, the snapshot date, and the **canonical record schema** for each mirror.

## IANA media types (`data/media-types/iana-media-types.json`)

- **Source URL**: <https://www.iana.org/assignments/media-types/media-types.xml>
- **Standard**: RFC 6838 (Media Type Specifications and Registration Procedures)
- **Snapshot date**: 2026-10-16
- **Record count**: 2,366 canonical media types (one per `{type}/{clean-subtype}` pair)
- **Per-top-level-type counts**: `application` 1,812 / `audio` 165 / `font` 6 / `haptics` 3 / `image` 88 / `message` 27 / `model` 44 / `multipart` 17 / `text` 107 / `video` 97 (sum: 2,366)
- **Status counts**: `registered` 2,334 / `obsoleted` 18 / `deprecated` 8 / `obsolete` 6 (sum: 2,366)
- **Reproducible via**: `scripts/fetch-iana.sh` (re-fetch) + `scripts/parse-iana.py` (re-parse). The build is deterministic; only the snapshot date changes per fetch.
- **Audit hash**: see `data/SHA256SUMS` row 1

### Record schema (per `records[]` entry)

| field          | type   | description |
|----------------|--------|-------------|
| `registry`     | string | Always `"media-types"`. Lets downstream consumers distinguish from the URI-schemes registry without conflating the `type` semantics. |
| `name`         | string | Canonical RFC 6838 form: `{type}/{subtype}` (e.g. `application/json`). |
| `type`         | string | IANA top-level type (`application`, `audio`, `font`, `haptics`, `image`, `message`, `model`, `multipart`, `text`, `video`). |
| `subtype`      | string | Clean subtype suffix. IANA's ` - DEPRECATED ...` / ` (OBSOLETED ...)` annotation is stripped into a separate `annotation` field; the clean subtype is what appears in the per-record URL. |
| `status`       | string | One of `registered` / `deprecated` / `obsoleted` / `obsolete`. Derived from the IANA annotation when present, else `registered`. |
| `annotation`   | string? | IANA's raw annotation text (e.g. `OBSOLETED in favor of text/javascript`). Present only when `status != "registered"`. |
| `superseded_by`| string? | Canonical replacement when the annotation says `in favor of X`. Sometimes IANA writes the replacement without the leading `type/`; consumers should resolve against the source record's top-level type when not canonical. 17 records carry this field. |
| `template`     | string? | The template content-type string from `<file type="template">`. Used in `Content-Type` headers when a subtype is a structured family with multiple variants; populated for **all 2,366** records that IANA lists with a template file. |
| `references`   | array? | List of `{type, data}` pairs extracted from `<xref>` elements (rfc / person / draft / uri / registry). |

### Notable schema corrections in Slice 1

The pre-Slice-1 mirror conflated the subtype suffix with the canonical media type (stored as `name = "json"` for `application/json`) and silently dropped 61 records whose subtype crossed multiple top-level types (the IANA `*/*example` placeholder exists under eight top-level types). The current schema fixes this; the count goes from 2,305 to 2,366.

The pre-Slice-1 mirror also truncated 2 media-type names where IANA's `<name>` element nested an `<xref>` (e.g. `vnd.geo+json (OBSOLETED by rfc7946 in favor of application/geo+json)`); xref expansion now recovers the full text.

## IANA URI schemes (`data/uri-schemes/iana-uri-schemes.json`)

- **Source URL**: <https://www.iana.org/assignments/uri-schemes/uri-schemes.xml>
- **Sub-registry**: `uri-schemes-1` ("Uniform Resource Identifier (URI) Schemes"). The XML also contains three sibling sub-registries under `ipn-scheme-uri-*` (Ipn Scheme URI Allocator Identifiers, Default Allocator Node Numbers, Well-Known Service Numbers for BPv7); those are NOT mirrored here and would land as a separate slice if needed.
- **Standard**: RFC 3986 (URI Generic Syntax) + RFC 7595 (URI Scheme Registration Procedures)
- **Snapshot date**: 2026-10-16
- **Record count**: 451 unique URI scheme names (Permanent 98 / Provisional 334 / Historical 18 / obsolete 1)
- **Reproducible via**: `scripts/fetch-iana.sh` + `scripts/parse-iana.py`
- **Audit hash**: see `data/SHA256SUMS` row 2

### Record schema (per `records[]` entry)

| field          | type   | description |
|----------------|--------|-------------|
| `registry`     | string | Always `"uri-schemes"`. |
| `name`         | string | Canonical URI scheme name (preserves IANA-listed case). |
| `status`       | string | IANA `<status>` value (`Permanent` / `Provisional` / `Historical`); overridden by `obsolete` if the scheme carries a `(OBSOLETE)` annotation. |
| `annotation`   | string? | Raw IANA annotation when present. |
| `superseded_by`| string? | Replacement when IANA wrote an `in favor of ...` clause. |
| `description`  | string? | IANA's prose description with `<xref>` text expanded to `[label]` placeholders. |
| `references`   | array? | List of `{type, data}` pairs from `<xref>` elements (rfc / person / draft / uri / registry). |

### Notable schema corrections in Slice 1

The pre-Slice-1 mirror truncated 12 URI-scheme descriptions where IANA's `<description>` element nested an `<xref>` (most often a `see [expert-notes]` reference); xref expansion now recovers the full text.

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

## Invariants enforced by CI

`scripts/validate-data.py` (run by `bash scripts/build.sh` and by the GitHub Actions `validate-data` workflow) asserts:

1. The IANA media-types count equals 2,366.
2. The IANA URI-schemes count equals 451.
3. The ECF cells count equals 49.
4. There are no case-insensitive duplicate canonical names.
5. Every non-`registered` record carries an `annotation` field.
6. Every record has a corresponding per-record HTML file.
7. `data/SHA256SUMS` matches the on-disk JSON bytes.

Any non-`registered` record whose `superseded_by` cannot be resolved to a canonical `type/subtype` is logged as a warning (raw IANA text is preserved); this catches IANA's own annotation typos without rejecting the mirror.
