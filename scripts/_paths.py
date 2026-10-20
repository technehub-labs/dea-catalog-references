"""_paths.py -- generate and validate the /dea/<path> redirect shims layer.

Used by:
- scripts/build-html.py to emit data/paths.tsv + dea/* redirect shims
- scripts/validate-data.py to assert the shims + paths.tsv are consistent
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class PathRow:
    path: str        # e.g. 'application/json' or 'https'
    target: str      # e.g. '/media-types/application/json' or '/uri-schemes/https'


def load_mirror_rows() -> list[PathRow]:
    """Walk the canonical mirrors and emit one row per canonical path."""
    rows: list[PathRow] = []
    mt = json.loads((ROOT / "data/media-types/iana-media-types.json").read_text())
    for r in mt["records"]:
        rows.append(PathRow(f"{r['type']}/{r['subtype']}",
                            f"/media-types/{r['type']}/{r['subtype']}"))
    us = json.loads((ROOT / "data/uri-schemes/iana-uri-schemes.json").read_text())
    for r in us["records"]:
        rows.append(PathRow(r["name"], f"/uri-schemes/{r['name']}"))
    return rows


def write_paths_tsv(rows: list[PathRow], dest: Path) -> int:
    """Write the canonical path catalogue (sorted, deduped)."""
    seen: set[str] = set()
    out: list[PathRow] = []
    for row in rows:
        if row.path in seen:
            continue
        seen.add(row.path)
        out.append(row)
    out.sort(key=lambda r: r.path.lower())

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w") as f:
        for row in out:
            f.write(f"{row.path}\t{row.target}\n")
    return len(out)


def load_paths_tsv(src: Path) -> list[PathRow]:
    rows: list[PathRow] = []
    for line in src.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        p, t = line.split("\t", 1)
        rows.append(PathRow(p, t))
    return rows


# Path -> file path on disk (extension .html; nested preserved as dir/file.html)
def shim_path_for(path: str) -> Path:
    if "/" in path:
        return ROOT / "dea" / (path.replace("/", "/") + ".html")
        # 'application/json' -> ROOT/dea/application/json.html
    return ROOT / "dea" / f"{path}.html"


_REDIRECT_TPL = """<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=https://lists.technehub.com{target}">
<link rel="canonical" href="https://lists.technehub.com{target}">
<title>Redirecting to {target}</title>
<meta name="robots" content="noindex">
<style>body{{font-family:ui-sans-serif,system-ui,sans-serif;max-width:32rem;margin:3rem auto;padding:0 1rem;line-height:1.5;color:#555;}}a{{color:inherit;}}</style>
</head><body>
<p>Redirecting to <a href="https://lists.technehub.com{target}"><code>{target}</code></a>.</p>
</body></html>
"""


def emit_shim(row: PathRow) -> Path:
    body = _REDIRECT_TPL.format(target=row.target)
    target = shim_path_for(row.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)
    return target


# ---- validator-side helpers -------------------------------------------------

def target_html_target(target: str) -> Path:
    """Map a redirect target like /media-types/application/json to its on-disk HTML.

    Notes
    -----
    The build-html writer appends `.html` to the *clean subtype*. For a normal
    subtype (e.g. `json`) the file is `<json>.html` and the URL `/json` resolves
    to it (GitHub Pages serves a literal `<name>.html` for the extensionless
    request /<name>).

    Edge cases the writer must handle:

    * Structured-syntax subtypes (`+xml`, `.cap+xml`): the writer produces
      `<subtype-with-+xml>.html`. No special handling needed here; the URL
      `/<subtype-with-+xml>` matches the on-disk file at the same name +.html.

    * Subtypes that *literally* end in `.html` (e.g.
      `vnd.sealedmedia.softseal.html`). The writer produces a double-extension
      file (`<subtype-without-dothtml>.html.html` -- i.e. the file is
      `vnd.sealedmedia.softseal.html.html`). The canonical URL `/<subtype-with-.html>`
      is served by GitHub Pages because the existing rule serves a file whose
      literal name minus trailing `.html` matches the request path. In other
      words `/foo.html` resolves to file `foo.html.html` -- Pages strips ONE
      `.html` from the filename to get the request, finds the file, serves it.
    """
    parts = target.lstrip("/").split("/")
    last = parts[-1]
    if last.endswith(".html"):
        # The writer appended .html on top of an already-html-terminated subtype.
        # Re-attach it to the LAST segment only.
        new_last = last + ".html"
        return ROOT.joinpath(*parts[:-1], new_last)
    return ROOT.joinpath(*parts[:-1], last + ".html")


def target_html_exists(target: str) -> bool:
    return target_html_target(target).exists()


def shim_content_is_valid(path: Path) -> tuple[bool, str]:
    """Return (ok, why-not). The shim body should meta-refresh to lists.technehub.com/<target>."""
    body = path.read_text()
    if "noindex" not in body:
        return False, "missing noindex meta"
    m = re.search(r'http-equiv="refresh"[^>]+url=(https://lists\.technehub\.com(/[^\"]+))', body)
    if not m:
        return False, "missing meta http-equiv refresh to lists.technehub.com"
    return True, m.group(2)
