#!/usr/bin/env python3
"""build-html.py -- generate static landing pages from the JSON mirrors.

Generates:
  media-types/index.html    -- list of all 2,305 media types
  uri-schemes/index.html    -- list of all 451 URI schemes
  ecf/<domain>/<stage>.html -- one per ECF cell (49 files)

Per-record HTML for media types and URI schemes is deferred to a follow-on
slice; the JSON mirrors are the durable artifact for now.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render_index_html(
    title: str, description: str, json_relpath: str, rows: list[str]
) -> str:
    body_rows = "\n".join(rows)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="alternate" type="application/json" href="{html.escape(json_relpath)}">
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: ui-sans-serif, system-ui, -apple-system, sans-serif; max-width: 80rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; font-size: 0.85rem; }}
  th, td {{ padding: 0.3rem 0.5rem; border-bottom: 1px solid #eee; text-align: left; vertical-align: top; }}
  th {{ background: #f8f8f8; font-weight: 600; position: sticky; top: 0; }}
  td.name {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  footer {{ margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee; color: #666; font-size: 0.85rem; }}
  code {{ background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 0.2em; font-size: 0.9em; }}
</style>
</head>
<body>
<header>
<h1>{html.escape(title)}</h1>
<p>{html.escape(description)}</p>
</header>
<table>
<thead><tr><th>Name</th><th>Status</th><th>Template / URI</th><th>Description / References</th></tr></thead>
<tbody>
{body_rows}
</tbody>
</table>
<footer>
<p>Snapshot date: 2026-10-16. Mirror JSON: <a href="{html.escape(json_relpath)}"><code>{html.escape(json_relpath)}</code></a>.</p>
<p>Hosted at <a href="https://lists.technehub.com/">lists.technehub.com</a>. License: MIT.</p>
</footer>
</body>
</html>
"""


def media_types_html() -> str:
    data = json.loads((ROOT / "data/media-types/iana-media-types.json").read_text())
    rows = []
    for r in data["records"]:
        name = html.escape(r.get("name", ""))
        status = html.escape(r.get("status", ""))
        template = html.escape(r.get("template") or "")
        refs = r.get("references") or []
        ref_text = "<br>".join(
            f"{html.escape(x.get('type',''))}: {html.escape(x.get('data',''))}"
            for x in refs
        )
        rows.append(f"<tr><td class='name'>{name}</td><td>{status}</td><td>{template}</td><td>{ref_text}</td></tr>")
    return render_index_html(
        "IANA Media Types",
        f"RFC 6838. Mirror of the IANA Media Types registry. {data['count']} records in the 2026-10-16 snapshot.",
        "/data/media-types/iana-media-types.json",
        rows,
    )


def uri_schemes_html() -> str:
    data = json.loads((ROOT / "data/uri-schemes/iana-uri-schemes.json").read_text())
    rows = []
    for r in data["records"]:
        name = html.escape(r.get("name", ""))
        status = html.escape(r.get("status", ""))
        desc = html.escape(r.get("description") or "")
        refs = r.get("references") or []
        ref_text = "<br>".join(
            f"{html.escape(x.get('type',''))}: {html.escape(x.get('data',''))}"
            for x in refs
        )
        rows.append(
            f"<tr><td class='name'>{name}</td><td>{status}</td><td>--</td><td>{desc}<br>{ref_text}</td></tr>"
        )
    return render_index_html(
        "IANA URI Schemes",
        f"RFC 3986, RFC 7595. Mirror of the IANA URI Schemes registry (uri-schemes-1). {data['count']} records in the 2026-10-16 snapshot.",
        "/data/uri-schemes/iana-uri-schemes.json",
        rows,
    )


def ecf_cell_html(coord: dict) -> str:
    d = html.escape(coord["domain"])
    s = html.escape(coord["stage"])
    tw = html.escape(coord["typical_work"])
    cid = html.escape(coord["id"])
    dt = html.escape(coord["domain_token"])
    st = html.escape(coord["stage_token"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{cid} - OpenDEA Reference Registry</title>
<meta name="description" content="ECF coordinate {cid}. Domain: {d}. Stage: {s}. Typical work: {tw}.">
<link rel="alternate" type="application/json" href="/data/ecf-coordinates/coordinates.json">
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: ui-sans-serif, system-ui, -apple-system, sans-serif; max-width: 50rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
  dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 0.4rem 1rem; }}
  dt {{ font-weight: 600; }}
  code {{ background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 0.2em; font-size: 0.95em; }}
  footer {{ margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee; color: #666; font-size: 0.85rem; }}
</style>
</head>
<body>
<header>
<h1>{cid}</h1>
<p>ECF coordinate at the intersection of <strong>{d}</strong> (domain) and <strong>{s}</strong> (stage).</p>
</header>
<dl>
<dt>Coordinate id</dt><dd><code>{cid}</code></dd>
<dt>Domain</dt><dd>{d}</dd>
<dt>Stage</dt><dd>{s}</dd>
<dt>Typical work</dt><dd>{tw}</dd>
<dt>Domain token</dt><dd><code>{dt}</code></dd>
<dt>Stage token</dt><dd><code>{st}</code></dd>
<dt>Matrix source</dt><dd><a href="{html.escape(coord['matrix_url'])}">{html.escape(coord['matrix_url'])}</a></dd>
</dl>
<footer>
<p>Hosted at <a href="https://lists.technehub.com/">lists.technehub.com</a>. License: MIT. Mirror JSON: <a href="/data/ecf-coordinates/coordinates.json"><code>data/ecf-coordinates/coordinates.json</code></a>.</p>
<p><a href="/ecf/">Back to the 49-cell index</a></p>
</footer>
</body>
</html>
"""


def main() -> None:
    (ROOT / "media-types/index.html").write_text(media_types_html())
    print("wrote media-types/index.html")

    (ROOT / "uri-schemes/index.html").write_text(uri_schemes_html())
    print("wrote uri-schemes/index.html")

    coords = json.loads((ROOT / "data/ecf-coordinates/coordinates.json").read_text())
    for c in coords["coordinates"]:
        d_token = c["domain_token"]
        s_token = c["stage_token"]
        out_dir = ROOT / "ecf" / d_token
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{s_token}.html").write_text(ecf_cell_html(c))
    print(f"wrote {len(coords['coordinates'])} ECF cell pages")


if __name__ == "__main__":
    main()