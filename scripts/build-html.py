#!/usr/bin/env python3
"""build-html.py -- generate static landing pages from the JSON mirrors.

Generates:
  media-types/index.html                        -- list of all 2,366 media types
  media-types/<type>/index.html                 -- per-type list (10 files)
  media-types/<type>/<subtype>.html             -- per-record page (2,366 files)
  uri-schemes/index.html                        -- list of all 451 URI schemes
  uri-schemes/<scheme>.html                     -- per-record page (451 files)
  ecf/<domain>/<stage>.html                     -- per-cell page (49 files)

Per-record HTML is the human surface; the bulk JSON mirrors remain the
authoritative machine surface and are linked via <link rel="alternate"
type="application/json">.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- shared style for all generated pages -----------------------------------

SHARED_STYLE = """
  :root { color-scheme: light dark; }
  body { font-family: ui-sans-serif, system-ui, -apple-system, sans-serif; max-width: 56rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
  nav.breadcrumb { font-size: 0.85rem; color: #666; margin-bottom: 0.5rem; }
  nav.breadcrumb a { color: inherit; text-decoration: underline; }
  h1 { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 1.6rem; word-break: break-all; }
  table { border-collapse: collapse; width: 100%; margin-top: 1rem; font-size: 0.85rem; }
  th, td { padding: 0.3rem 0.5rem; border-bottom: 1px solid #eee; text-align: left; vertical-align: top; }
  th { background: #f8f8f8; font-weight: 600; position: sticky; top: 0; }
  td.name { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  td.name a { color: inherit; text-decoration: underline; }
  dl { display: grid; grid-template-columns: max-content 1fr; gap: 0.4rem 1rem; margin-top: 1rem; }
  dt { font-weight: 600; }
  dl dd code { background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 0.2em; font-size: 0.95em; }
  code { background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 0.2em; font-size: 0.95em; }
  footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee; color: #666; font-size: 0.85rem; }
  .badges { margin: 0.5rem 0; display: flex; gap: 0.4rem; flex-wrap: wrap; }
  .badge { display: inline-block; padding: 0.1em 0.5em; border-radius: 999px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.02em; }
  .badge-registered { background: #e6f4ea; color: #1e6b3a; }
  .badge-obsolete, .badge-obsoleted, .badge-deprecated { background: #fde7ea; color: #8a2230; }
  .badge-historical { background: #f1ecf9; color: #5e3a98; }
  .badge-permanent { background: #e6f4ea; color: #1e6b3a; }
  .badge-provisional { background: #fdf3df; color: #855a17; }
  ul.refs { padding-left: 1.2rem; }
  ul.refs li { margin: 0.2rem 0; }
"""


def _html_doc(title: str, description: str, json_relpath: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="alternate" type="application/json" href="{html.escape(json_relpath)}">
<style>{SHARED_STYLE}</style>
</head>
<body>
{body}
</body>
</html>
"""


def _footer() -> str:
    return """<footer>
<p>Hosted at <a href="https://lists.technehub.com/">lists.technehub.com</a>. License: MIT.</p>
<p>Snapshot 2026-10-16 of the IANA registry.</p>
</footer>"""


# --- media-type per-record ---------------------------------------------------

def media_type_per_record(rec: dict) -> str:
    nm = html.escape(rec["name"])
    top = html.escape(rec["type"])
    sub = html.escape(rec["subtype"])
    status = rec.get("status", "registered")
    status_cls = f"badge-{html.escape(status)}"
    annot = rec.get("annotation") or ""
    supersedes = rec.get("superseded_by") or ""
    template = rec.get("template") or ""
    description = (
        f"RFC 6838 media type {rec['name']}. Status: {status}."
    )

    rows = [
        ("Canonical name", f"<code>{nm}</code>"),
        ("Top-level type", f"<a href=\"/media-types/{top}/\">{top}</a>"),
        ("Subtype", f"<code>{sub}</code>"),
        ("Status", f"<span class=\"badge {status_cls}\">{html.escape(status)}</span>"),
    ]
    if template:
        rows.append(("Template", f"<code>{html.escape(template)}</code>"))
    rows.append(("Standard", "RFC 6838"))
    if annot:
        rows.append(("Annotation", f"<code>{html.escape(annot)}</code>"))
    if supersedes:
        # Render as a link if the target is a known record; otherwise as plain text
        url = f"/media-types/{supersedes.split('/', 1)[0]}/{supersedes.split('/', 1)[1]}.html" if "/" in supersedes else None
        link = (
            f"<a href=\"{html.escape(url)}\"><code>{html.escape(supersedes)}</code></a>"
            if url else f"<code>{html.escape(supersedes)}</code>"
        )
        rows.append(("Superseded by", link))

    refs_html = ""
    refs = rec.get("references") or []
    if refs:
        items = []
        for x in refs:
            t = html.escape(x.get("type", ""))
            d = html.escape(x.get("data", ""))
            items.append(f"<li><code>{t}</code> {d}</li>")
        refs_html = f"<h2>References</h2><ul class=\"refs\">{''.join(items)}</ul>"

    dl = "\n".join(
        f"<dt>{html.escape(k)}</dt><dd>{v}</dd>" for k, v in rows
    )
    breadcrumb = (
        "<nav class=\"breadcrumb\"><a href=\"/\">Home</a> / "
        f"<a href=\"/media-types/\">Media Types</a> / "
        f"<a href=\"/media-types/{top}/\">{top}</a> / "
        f"{sub}</nav>"
    )
    body = (
        f"{breadcrumb}"
        f"<header><h1>{nm}</h1>"
        f"<p class=\"badges\"><span class=\"badge {status_cls}\">{html.escape(status)}</span></p>"
        f"</header>"
        f"<dl>{dl}</dl>"
        f"{refs_html}"
        f"{_footer()}"
    )
    return _html_doc(
        f"{rec['name']} - OpenDEA Reference Registry",
        description,
        f"/media-types/{top}/{sub}.json",
        body,
    )


# --- URI-scheme per-record ----------------------------------------------------

def uri_scheme_per_record(rec: dict) -> str:
    nm = rec["name"]
    nm_e = html.escape(nm)
    status = rec.get("status", "Provisional")
    status_cls = f"badge-{html.escape(status.lower())}"
    desc = rec.get("description") or ""
    desc_html = f"<p>{html.escape(desc)}</p>" if desc else ""

    rows = [
        ("Canonical name", f"<code>{nm_e}</code>"),
        ("Status", f"<span class=\"badge {status_cls}\">{html.escape(status)}</span>"),
        ("Standard", "RFC 3986 / RFC 7595"),
    ]
    annot = rec.get("annotation") or ""
    if annot:
        rows.append(("Annotation", f"<code>{html.escape(annot)}</code>"))

    refs_html = ""
    refs = rec.get("references") or []
    if refs:
        items = []
        for x in refs:
            t = html.escape(x.get("type", ""))
            d = html.escape(x.get("data", ""))
            items.append(f"<li><code>{t}</code> {d}</li>")
        refs_html = f"<h2>References</h2><ul class=\"refs\">{''.join(items)}</ul>"

    dl = "\n".join(f"<dt>{html.escape(k)}</dt><dd>{v}</dd>" for k, v in rows)
    breadcrumb = (
        "<nav class=\"breadcrumb\"><a href=\"/\">Home</a> / "
        f"<a href=\"/uri-schemes/\">URI Schemes</a> / {nm_e}</nav>"
    )
    description = f"URI scheme {nm}. Status: {status}." + (
        f" {desc[:200]}" if desc else ""
    )
    body = (
        f"{breadcrumb}"
        f"<header><h1>{nm_e}</h1>"
        f"<p class=\"badges\"><span class=\"badge {status_cls}\">{html.escape(status)}</span></p>"
        f"</header>"
        f"<dl>{dl}</dl>"
        f"{desc_html}"
        f"{refs_html}"
        f"{_footer()}"
    )
    return _html_doc(
        f"{nm} - OpenDEA Reference Registry",
        description,
        f"/uri-schemes/{nm}.json",
        body,
    )


# --- per-type index page (media types) ---------------------------------------

def media_type_index_for_type(top: str, recs: list[dict]) -> str:
    rows = []
    for r in sorted(recs, key=lambda r: r["subtype"].lower()):
        sub = html.escape(r["subtype"])
        status = html.escape(r.get("status", "registered"))
        status_cls = f"badge-{r.get('status', 'registered')}"
        link = f"/media-types/{html.escape(top)}/{sub}.html"
        annot = html.escape(r.get("annotation") or "")
        rows.append(
            f"<tr><td class=\"name\"><a href=\"{link}\"><code>{sub}</code></a></td>"
            f"<td><span class=\"badge {status_cls}\">{status}</span></td>"
            f"<td>{annot}</td></tr>"
        )
    breadcrumb = (
        "<nav class=\"breadcrumb\"><a href=\"/\">Home</a> / "
        "<a href=\"/media-types/\">Media Types</a> / "
        f"{html.escape(top)}</nav>"
    )
    body = (
        f"{breadcrumb}"
        f"<header><h1>{html.escape(top)}/*</h1>"
        f"<p>{len(recs)} subtypes in the {html.escape(top)} top-level type (RFC 6838).</p>"
        f"</header>"
        f"<table><thead><tr><th>Subtype</th><th>Status</th><th>Annotation</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        f"{_footer()}"
    )
    return _html_doc(
        f"{top} - OpenDEA Reference Registry",
        f"Media types in the {top} top-level type (RFC 6838). {len(recs)} records in the 2026-10-16 snapshot.",
        "/data/media-types/iana-media-types.json",
        body,
    )


# --- media-types master index page --------------------------------------------

def media_types_html() -> str:
    data = json.loads((ROOT / "data/media-types/iana-media-types.json").read_text())
    by_type: dict[str, list[dict]] = {}
    for r in data["records"]:
        by_type.setdefault(r["type"], []).append(r)

    sections = []
    for t in sorted(by_type):
        section_rows = []
        for r in sorted(by_type[t], key=lambda r: r["subtype"].lower()):
            sub = html.escape(r["subtype"])
            status = html.escape(r.get("status", "registered"))
            status_cls = f"badge-{r.get('status', 'registered')}"
            annot = html.escape(r.get("annotation") or "")
            link = f"/media-types/{html.escape(t)}/{sub}.html"
            section_rows.append(
                f"<tr><td class=\"name\"><a href=\"{link}\"><code>{sub}</code></a></td>"
                f"<td><span class=\"badge {status_cls}\">{status}</span></td>"
                f"<td>{annot}</td></tr>"
            )
        sections.append(
            f"<h2 id=\"{html.escape(t)}\">{html.escape(t)} "
            f"<small>({len(by_type[t])})</small></h2>"
            f"<table><thead><tr><th>Subtype</th><th>Status</th><th>Annotation</th></tr></thead>"
            f"<tbody>{''.join(section_rows)}</tbody></table>"
        )

    body = (
        "<nav class=\"breadcrumb\"><a href=\"/\">Home</a> / Media Types</nav>"
        f"<header><h1>IANA Media Types</h1>"
        f"<p>RFC 6838. Mirror of the IANA Media Types registry. {data['count']} records in the 2026-10-16 snapshot.</p>"
        f"</header>"
        f"{''.join(sections)}"
        f"{_footer()}"
    )
    return _html_doc(
        "IANA Media Types - OpenDEA Reference Registry",
        f"IANA Media Types registry (RFC 6838). {data['count']} records in the 2026-10-16 snapshot.",
        "/data/media-types/iana-media-types.json",
        body,
    )


# --- uri-schemes master index page --------------------------------------------

def uri_schemes_html() -> str:
    data = json.loads((ROOT / "data/uri-schemes/iana-uri-schemes.json").read_text())
    rows = []
    for r in sorted(data["records"], key=lambda r: r["name"].lower()):
        nm = html.escape(r["name"])
        status = html.escape(r.get("status", "Provisional"))
        status_cls = f"badge-{r.get('status', 'Provisional').lower()}"
        desc = html.escape((r.get("description") or "")[:200])
        annot = html.escape(r.get("annotation") or "")
        link = f"/uri-schemes/{nm}.html"
        rows.append(
            f"<tr><td class=\"name\"><a href=\"{link}\"><code>{nm}</code></a></td>"
            f"<td><span class=\"badge {status_cls}\">{status}</span></td>"
            f"<td>{desc}</td>"
            f"<td>{annot}</td></tr>"
        )
    body = (
        "<nav class=\"breadcrumb\"><a href=\"/\">Home</a> / URI Schemes</nav>"
        f"<header><h1>IANA URI Schemes</h1>"
        f"<p>RFC 3986 / RFC 7595. Mirror of the IANA URI Schemes registry (uri-schemes-1). {data['count']} records in the 2026-10-16 snapshot.</p>"
        f"</header>"
        f"<table><thead><tr><th>Name</th><th>Status</th><th>Description</th><th>Annotation</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        f"{_footer()}"
    )
    return _html_doc(
        "IANA URI Schemes - OpenDEA Reference Registry",
        f"IANA URI Schemes registry (RFC 3986, RFC 7595). {data['count']} records in the 2026-10-16 snapshot.",
        "/data/uri-schemes/iana-uri-schemes.json",
        body,
    )


# --- per-cell ECF page (unchanged behaviour) ---------------------------------

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
<style>{SHARED_STYLE}</style>
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
    # Master indices
    (ROOT / "media-types/index.html").write_text(media_types_html())
    print("wrote media-types/index.html")

    (ROOT / "uri-schemes/index.html").write_text(uri_schemes_html())
    print("wrote uri-schemes/index.html")

    # Per-record media type pages. Per-type listings live in a separate
    # by-type/ namespace to avoid overwriting the rare record whose clean
    # subtype is exactly "index" (e.g. application/index).
    mt_data = json.loads((ROOT / "data/media-types/iana-media-types.json").read_text())
    by_type: dict[str, list[dict]] = {}
    for r in mt_data["records"]:
        by_type.setdefault(r["type"], []).append(r)

    total_mt_records = 0
    for top, recs in by_type.items():
        top_dir = ROOT / "media-types" / top
        top_dir.mkdir(parents=True, exist_ok=True)
        for rec in recs:
            (top_dir / f"{rec['subtype']}.html").write_text(media_type_per_record(rec))
            total_mt_records += 1

    by_type_dir = ROOT / "media-types" / "by-type"
    by_type_dir.mkdir(parents=True, exist_ok=True)
    for top, recs in by_type.items():
        (by_type_dir / f"{top}.html").write_text(media_type_index_for_type(top, recs))
    print(
        f"wrote {total_mt_records} per-record media-type pages "
        f"({len(by_type)} per-type indices at /media-types/by-type/)"
    )

    # Per-record URI-scheme pages
    us_data = json.loads((ROOT / "data/uri-schemes/iana-uri-schemes.json").read_text())
    total_us_records = 0
    for rec in us_data["records"]:
        (ROOT / "uri-schemes" / f"{rec['name']}.html").write_text(uri_scheme_per_record(rec))
        total_us_records += 1
    print(f"wrote {total_us_records} per-record URI-scheme pages")

    # ECF cells (unchanged)
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
