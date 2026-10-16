#!/usr/bin/env python3
"""parse-ecf.py -- extract the ECF 7x7 matrix from dea-metaframework/framework/matrix.md.

Input:   /tmp/ecf-matrix.md
Output:  data/ecf-coordinates/coordinates.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOMAIN_RE = re.compile(r"^\|\s*([0-9]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
STAGE_RE = re.compile(r"^\|\s*([0-9]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")


def parse(md_path: str = "/tmp/ecf-matrix.md") -> dict:
    md = Path(md_path).read_text()

    domain_section = md.split("### Domains (Rows): Scope of Operations")[1].split(
        "### Stages"
    )[0]
    domains: list[str] = []
    for line in domain_section.split("\n"):
        m = DOMAIN_RE.match(line)
        if m and "---" not in line:
            domains.append(m.group(2).strip())

    stage_section = md.split("### Stages (Columns): Value Stream Stages")[1].split(
        "## Foundation Matrix Content"
    )[0]
    stages: list[str] = []
    for line in stage_section.split("\n"):
        m = STAGE_RE.match(line)
        if m and "---" not in line:
            stages.append(m.group(2).strip())

    mat_section = md.split("## Foundation Matrix Content")[1].split("## Patterns")[0]
    matrix_rows: dict[str, dict[str, str]] = {}
    for line in mat_section.split("\n"):
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 8 or "**" not in cells[0]:
            continue
        domain_label = re.sub(r"\*\*", "", cells[0]).strip()
        row: dict[str, str] = {}
        for i, stage in enumerate(stages):
            if i + 1 < len(cells):
                row[stage] = cells[i + 1]
        matrix_rows[domain_label] = row

    coordinates = []
    for domain in domains:
        d_token = re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")
        for stage in stages:
            s_token = stage.lower()
            coordinates.append(
                {
                    "id": f"ecf:{d_token}.{s_token}",
                    "domain": domain,
                    "stage": stage,
                    "domain_token": d_token,
                    "stage_token": s_token,
                    "typical_work": matrix_rows.get(domain, {}).get(stage, ""),
                    "matrix_url": "https://github.com/technehub-labs/dea-metaframework/blob/main/framework/matrix.md",
                }
            )

    return {
        "source": "technehub-labs/dea-metaframework/framework/matrix.md",
        "standard": "ECF (Enterprise Concept Framework)",
        "snapshot_date": "2026-10-16",
        "domains": domains,
        "stages": stages,
        "count": len(coordinates),
        "coordinates": coordinates,
    }


def main() -> None:
    out = parse()
    (ROOT / "data/ecf-coordinates/coordinates.json").write_text(json.dumps(out, indent=2))
    print(
        f"wrote {out['count']} coordinates across {len(out['domains'])} domains x {len(out['stages'])} stages"
    )


if __name__ == "__main__":
    main()