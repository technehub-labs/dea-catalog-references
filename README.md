# dea-catalog-references

OpenDEA reference registry. Mirrors of authoritative external registries plus the Enterprise Concept Framework (ECF) coordinate enumeration, served as a public surface at <https://lists.technehub.com>.

## Scope

This catalog holds **reference mirrors**, not OpenDEA catalog entries. The three data sets are:

1. **IANA media types** (RFC 6838): mirror of the IANA Media Types registry.
2. **IANA URI schemes** (RFC 3986, RFC 7595): mirror of the IANA URI Schemes registry.
3. **ECF 7 x 7 coordinates** (dea-metaframework): the 49-cell cartesian product of seven Domains and seven Stages.

The mirrors are deterministic, hash-audited, and reproducible from the source XMLs via the build script. The registry data is **not** itself an OpenDEA entity record; OpenDEA catalog entries that need to reference a media type or URI scheme point at this mirror (or a downstream consumer of this mirror), not at a record here.

## What this catalog is not

- **Not a substitute for the authoritative registries.** IANA is the canonical source. This mirror is for static lookups and offline-friendly consumption; if IANA disagrees with this mirror, IANA wins.
- **Not an OpenDEA catalog entry repository.** Per the methodology-first rule on `technehub-labs/dea-catalog-*` repos, catalog entity entries (PC/PG/BP/L4+ records) are gated on a CR (e.g. CR-DEA-REF-01). This repo does not carry such entries in this slice.
- **Not a dereferencing API.** Path A first cut is a static mirror via GitHub Pages. Dynamic dereferencing (`/dea/{path}` lookups) lands as Path B, layered on once Path A is stable.

## Status

- **Slice 0 (2026-10-16, sealed PR #5)**: scaffold + data + static landing pages (list-level).
- **Slice 1 (this PR)**: per-record landing pages. The mirror's data model is corrected to canonical `name = type/subtype` (was: bare subtype suffix; lost 61 records), annotations (`OBSOLETE` / `OBSOLETED` / `DEPRECATED`) are split into their own field, `<xref>` text is fully expanded in names and descriptions, the `template` field is now populated, and 17 records carry an explicit `superseded_by` link. Result: 2,366 media-type per-record pages + 10 per-type listings + 451 URI-scheme per-record pages, served extensionless under `/media-types/<type>/<subtype>` and `/uri-schemes/<scheme>`. Also: CI gate upgraded from JSON-shape-only to a real invariant suite (`scripts/validate-data.py`).
- **Slice 2 (deferred)**: AAAA records for `lists.technehub.com` (tracked on Kanboard card #411, deferred).
- **Slice 3 (deferred)**: Path B dereferencing API (Cloudflare Workers + R2 + NS migration; tracked on parent card #377, deferred until Path A is stable/table).

## Entity Definition table

| Field | Value |
|---|---|
| Catalog type | Reference registry (mirror) |
| Layer | L0 (Reference mirrors; not an OpenDEA L1-L4 catalog layer) |
| Building block | TBD (allocation in `dea-architecture-framework`; fan-out pending) |
| Alias | `references`, `dea-catalog-refs` |
| Entity id prefix | `dea:reference-iana-media-type-<name>`, `dea:reference-iana-uri-scheme-<name>`, `dea:reference-ecf-coord-<domain-token>.<stage-token>` (schema proposals, not yet admission-gated) |
| Model version | OpenDEAM v0.4.0 |
| License | MIT |
| Visibility | public |

The `metamodel-pointer.yaml` for this repo is **to be generated** by the `dea-architecture-framework` root-model fan-out. Until that lands, the README is the source of truth for the allocation; do not hand-edit a `metamodel-pointer.yaml` (the file is auto-generated and regenerated only via the framework fan-out per the cardinal author rules).

## Key tenets

- **Mirrors are read-only artifacts.** No mutable state, no version chain beyond the snapshot date.
- **Mirrors are hash-audited.** Every published snapshot has a `data/SHA256SUMS` row for the three JSON files; CI verifies the hash on every PR.
- **Mirrors are reproducible.** `scripts/build.sh` regenerates every artifact from the source XMLs; the only variable inputs are the IANA snapshot date and the upstream XML content.
- **No silent schema extensions.** Schema changes land via CR-DEA-REF-* (forthcoming).

## Framework relationship

This catalog sits **below** the L1 OpenDEA catalogs and **adjacent to** the ECF metaframework. ECF coordinates enumerated here are the canonical 7 x 7 enumeration from `technehub-labs/dea-metaframework/framework/matrix.md` (the framework's center of gravity). When an OpenDEA catalog entry carries an `ecfConformance` block, the coordinate string here is the lookup target.

## Repository structure (current reality)

```
.
+- README.md                      This file.
+- LICENSE                        MIT (canonical text).
+- NOTICE                         Org-wide attribution notice.
+- CNAME                          Single line: lists.technehub.com
+- .gitignore                     Standard GitHub Pages + Python excludes.
+- .nojekyll                      Disables Jekyll processing on Pages.
+- index.html                     Landing page at https://lists.technehub.com/
+- healthz.html                   Static healthcheck at /healthz.
| +- data/
| |  +- media-types/
| |  |  +- iana-media-types.json    Mirror of IANA Media Types registry (2,366 records).
| |  +- uri-schemes/
| |  |  +- iana-uri-schemes.json    Mirror of IANA URI Schemes registry (451 records).
| |  +- ecf-coordinates/
| |  |  +- coordinates.json         49-cell ECF matrix from dea-metaframework.
| |  +- SHA256SUMS                  Audit hashes for the three JSON files.
| +- media-types/
| |  +- index.html                  List page of all 2,366 media types, grouped by top-level type.
| |  +- by-type/<type>.html         Per-type listing (10 files: application, audio, font, haptics, image, message, model, multipart, text, video).
| |  +- <type>/<subtype>.html       Per-record HTML page (2,366 files; extensionless URL: /media-types/<type>/<subtype>).
| +- uri-schemes/
| |  +- index.html                  List page of all 451 URI schemes.
| |  +- <scheme>.html               Per-record HTML page (451 files; extensionless URL: /uri-schemes/<scheme>).
| +- ecf/
| |  +- index.html                  List page of all 49 ECF cells.
| |  +- <domain-token>/<stage-token>.html  One per cell (49 files).
| +- scripts/
| |  +- fetch-iana.sh               Re-fetch IANA XML sources.
| |  +- build.sh                    Generate JSON mirrors + static landing pages + validate.
| |  +- parse-iana.py               Parse IANA XML to JSON (canonical name, xref expansion, annotation split).
| |  +- parse-ecf.py                Extract ECF matrix from dea-metaframework matrix.md.
| |  +- build-html.py               Generate per-record + index landing pages from JSON mirrors.
| |  +- validate-data.py            Assert data invariants + per-record page coverage + SHA256SUMS match.
| +- docs/
| |  +- FOUNDATIONS.md              Methodology-first tenets + decision-points register.
| |  +- DATA-PROVENANCE.md          Provenance + record-schema doc for each mirror.
| +- .github/
|    +- workflows/
|       +- pages-build-deploy.yml   GitHub Pages deploy on push to main.
|       +- validate-data.yml        CI gate: schema-shape + SHA256SUMS + per-record coverage (JSON-form).
```

## Change control

| Slice | Date | Change | Carrier |
|---|---|---|---|
| Slice 0 | 2026-10-16 | Scaffold + data + list-level landing pages | Kanban card #377 |
| Slice 1 | 2026-10-20 | Per-record landing pages + IANA data model correctness fix (canonical `name`, annotation split, xref expansion, template populated, superseded_by link). 2,366 + 451 + 49 + 10 + 1 + 1 = 2,878 HTML files. | Kanban card #524 (TBD) |

## Public surface

- Landing: <https://lists.technehub.com/>
- Healthcheck: <https://lists.technehub.com/healthz>
- Media types index: <https://lists.technehub.com/media-types/>
- Media types per-type: <https://lists.technehub.com/media-types/by-type/{type}>
- Media type per-record: <https://lists.technehub.com/media-types/{type}/{subtype}> (e.g. `/media-types/application/json`)
- URI schemes index: <https://lists.technehub.com/uri-schemes/>
- URI scheme per-record: <https://lists.technehub.com/uri-schemes/{scheme}> (e.g. `/uri-schemes/https`)
- ECF cells index: <https://lists.technehub.com/ecf/>
- Per-cell pages: <https://lists.technehub.com/ecf/{domain-token}/{stage-token}.html>