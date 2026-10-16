# Foundations

This document captures the methodology-first tenets for the `dea-catalog-references` repo and the decision-points that have framed prior CRs.

## Methodology-first tenets

1. **No entity records in this slice.** This repo holds *reference mirrors*, not OpenDEA catalog entries. The introduction of catalog entity records (PC / PG / BP / L4+ for IANA-typed or URI-scheme-typed artefacts) is gated on the first CR (CR-DEA-REF-01, forthcoming).
2. **No silent schema extensions.** Any new schema property lands via a CR; existing schemas gain only additive optional properties.
3. **Mirrors are deterministic and hash-audited.** Every snapshot is reproducible from the upstream XML / Markdown source via `scripts/build.sh`. Every PR must include the regenerated `data/SHA256SUMS` row.
4. **IANA is the canonical source.** This mirror is for static-lookup convenience. If IANA and this mirror disagree, IANA wins; the mirror is regenerated, not edited by hand.
5. **ECF source of truth is `dea-metaframework`.** The 7 x 7 matrix is owned by that repo. This repo reads from it, never edits it.

## Decision-points register

| # | Decision | Rationale | Carrier |
|---|---|---|---|
| D1 | Repo name `dea-catalog-references` | Aligns with the `dea-catalog-*` family; absorbs IANA mirrors + OpenDEA reference dereferencing. | This repo bring-up (kanban #377). |
| D2 | Path A first cut: GitHub Pages + custom domain CNAME | Fastest time-to-live; CDN-fast; zero ops. Fits the read-mostly mirror pattern. | Kanban #377. |
| D3 | AAAA records deferred as sub-task | supremedns.com panel did not publish AAAA on the 2026-10-16 attempt; defer to a sub-task (#411) rather than block Path A. | Kanban #411. |
| D4 | Catalog schema additions are additive only | Per methodology-first; no destructive migrations in adjacent catalogs while this slice lands. | Kanban #377. |
| D5 | Path B (Cloudflare Workers + R2, NS migration to Cloudflare) deferred until Path A is stable/table | Path B unlocks `/dea/{path}` dereferencing but requires NS migration (structural change). Sequencing keeps the cutover simple. | Kanban #377. |

## Slice history

| Slice | Date | Change | PR / card |
|---|---|---|---|
| 0 | 2026-10-16 | Scaffold + 3 JSON mirrors + 51 HTML pages + 2 GitHub Actions workflows | Kanban #377 |
| 0a | 2026-10-16 | AAAA sub-task deferred | Kanban #411 |