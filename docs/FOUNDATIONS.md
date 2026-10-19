# Foundations

This document captures the methodology-first tenets for the `dea-catalog-references` repo and the decision-points that have framed prior CRs.

## Methodology-first tenets

1. **No entity records in this slice.** This repo holds *reference mirrors*, not OpenDEA catalog entries. The introduction of catalog entity records (PC / PG / BP / L4+ for IANA-typed or URI-scheme-typed artefacts) is gated on the first CR (CR-DEA-REF-01, forthcoming).
2. **No silent schema extensions.** Any new schema property lands via a CR; existing schemas gain only additive optional properties. **The Slice 1 change to `name = type/subtype` is the one named exception:** the pre-Slice-1 schema conflated the subtype suffix with the canonical media type and silently dropped 61 records whose subtype crossed multiple top-level types; the data shape was not yet under load, so the fix landed with this PR rather than waiting for a CR cycle. Future shape changes follow CR-DEA-REF-*.
3. **Mirrors are deterministic and hash-audited.** Every snapshot is reproducible from the upstream XML / Markdown source via `scripts/build.sh`. Every PR must include the regenerated `data/SHA256SUMS` row.
4. **IANA is the canonical source.** This mirror is for static-lookup convenience. If IANA and this mirror disagree, IANA wins; the mirror is regenerated, not edited by hand.
5. **ECF source of truth is `dea-metaframework`.** The 7 x 7 matrix is owned by that repo. This repo reads from it, never edits it.
6. **CI gates the invariants.** `scripts/validate-data.py` asserts record counts, canonical-name uniqueness, per-record HTML coverage, and SHA256SUMS match. Any PR that breaks an invariant is blocked.

## Decision-points register

| #   | Decision                                                       | Rationale                                                                                                                                  | Carrier                |
|-----|----------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|------------------------|
| D1  | Repo name `dea-catalog-references`                             | Aligns with the `dea-catalog-*` family; absorbs IANA mirrors + OpenDEA reference dereferencing.                                             | Kanban #377            |
| D2  | Path A first cut: GitHub Pages + custom domain CNAME           | Fastest time-to-live; CDN-fast; zero ops. Fits the read-mostly mirror pattern.                                                              | Kanban #377            |
| D3  | AAAA records deferred as sub-task                              | supremedns.com panel did not publish AAAA on the 2026-10-16 attempt; defer to a sub-task (#411) rather than block Path A.                 | Kanban #411            |
| D4  | Catalog schema additions are additive only                     | Per methodology-first; no destructive migrations in adjacent catalogs while this slice lands.                                              | Kanban #377            |
| D5  | Path B (Cloudflare Workers + R2, NS migration to Cloudflare) deferred until Path A is stable/table | Path B unlocks `/dea/{path}` dereferencing but requires NS migration (structural change). Sequencing keeps the cutover simple. | Kanban #377            |
| D6  | `name = type/subtype` (canonical form)                         | The RFC 6838 identifier IS the slashed form; storing it as the registry's identifier lets consumers resolve a media type by what IANA publishes. Resolves the 61-record drop bug from the pre-Slice-1 schema. | Slice 1 PR (kanban TBD) |
| D7  | Per-record HTML pages, extensionless URL `/media-types/<type>/<subtype>` | Stable, citable per-record URLs that match the canonical identifier. 2,366 + 451 pages. No Jekyll resolution needed (extensionless → `.html` is how GitHub Pages serves it). | Slice 1 PR             |
| D8  | Per-type listings at `/media-types/by-type/<type>.html` (NOT `/media-types/<type>/index.html`) | The record `application/index` is a registered media type; placing an `index.html` inside `media-types/application/` would shadow it. The `_type` namespace puts the listing alongside, not inside. | Slice 1 PR             |
| D9  | Annotations (`OBSOLETE` / `OBSOLETED` / `DEPRECATED`) split into their own field, `status` derived | IANA mixes the lifecycle signal into the name itself ("`ecmascript (OBSOLETED in favor of text/javascript)`"); splitting gives consumers machine-readable status AND preserves the upstream human text in `annotation`. | Slice 1 PR             |
| D10 | 17 records carry `superseded_by`; one IANA annotation (`vnd.afpc.afplinedata`) cannot be resolved canonically and is preserved verbatim | IANA's annotation text is not always canonical; the validator warns (does not fail) on unresolved targets. We mirror upstream faithfully; we do not invent canonical replacements IANA did not publish. | Slice 1 PR             |

## Slice history

| Slice | Date       | Change                                                                                                                                                                                                                              | PR / card |
|-------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| 0     | 2026-10-16 | Scaffold + 3 JSON mirrors + 51 HTML pages + 2 GitHub Actions workflows                                                                                                                                                              | Kanban #377 |
| 0a    | 2026-10-16 | AAAA sub-task deferred                                                                                                                                                                                                              | Kanban #411 |
| 1     | 2026-10-20 | Correct the IANA data model (canonical `name`, annotation split, xref expansion, template populated, superseded_by link) + per-record landing pages (2,366 media types + 10 per-type listings + 451 URI schemes) + CI invariant gate | Kanban #524 |
