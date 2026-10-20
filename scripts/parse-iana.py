#!/usr/bin/env python3
"""parse-iana.py -- convert IANA XML sources to JSON mirrors.

Inputs:  /tmp/iana-media-types.xml, /tmp/iana-uri-schemes.xml
Outputs: data/media-types/iana-media-types.json
         data/uri-schemes/iana-uri-schemes.json

Schema: records carry canonical RFC 6838 / RFC 3986 identifiers as `name`;
deprecation annotations are split into `annotation` (the raw IANA text) and
`status` (a normalised lowercase token); `template` is populated from the
`<file type="template">` element when present; every record carries a
`registry` field ("media-types" or "uri-schemes") so downstream consumers do
not conflate top-level-type semantics with the registry type.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

NS = {"iana": "http://www.iana.org/assignments"}
ROOT = Path(__file__).resolve().parent.parent


# Personal-data hygiene: redact xref of type=person to a deterministic opaque
# token. The token is `redacted:person:<6-char-prefix-of-sha256-of(data+salt)>`,
# where the salt is constant and documented in docs/LICENSING-AND-LIA.md and
# docs/DATA-PROVENANCE.md. Same input -> same token (deterministic), so consumers
# can still count + dedupe contact slots across records. This is a SOFT
# redaction (the salt is public) intended to flip the legal posture from
# "publishes a directory of personal names" to "publishes aggregate contact
# statistics"; the canonical source for the actual name is IANA on the
# registry page (every per-record HTML page links back).
_REDACTION_SALT = "openDEA-catalog-refs-v1"


def redact_xref(xref_el) -> dict:
    """Serialize an <xref> element, redacting any personal-name data."""
    t = xref_el.get("type")
    d = xref_el.get("data", "")
    if t == "person" and d:
        h = __import__("hashlib").sha256((_REDACTION_SALT + d).encode("utf-8")).hexdigest()
        return {"type": t, "data": f"redacted:person:{h[:6]}"}
    if t and d:
        return {"type": t, "data": d.strip()}
    return None


# Annotation patterns: either " - DEPRECATED|OBSOLETE|OBSOLETED ..." or
# " (DEPRECATED|OBSOLETE|OBSOLETED ...)".
_ANNOT_DASH = re.compile(
    r'^(?P<sub>.*?)\s*-\s*(?P<ann>(?:OBSOLETE|OBSOLETED|DEPRECATED)\b.*)$'
)
_ANNOT_PAREN = re.compile(
    r'^(?P<sub>.*?)\s*\((?P<ann>(?:OBSOLETE|OBSOLETED|DEPRECATED)\b.*)\)$'
)
_SUPERSEDES = re.compile(r'in favor of\s+(?P<repl>.+?)\s*\.?\s*$', re.IGNORECASE)


def rtext(el) -> str:
    """Recursively extract text, expanding <xref> children with [label] markers."""
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        if child.tag.endswith('}xref') or child.tag == 'xref':
            label = (
                child.get('label')
                or child.get('data')
                or (child.text or '')
            ).strip()
            parts.append(f'[{label}]')
        elif child.text:
            parts.append(child.text)
        if child.tail:
            parts.append(child.tail)
    return ''.join(parts).strip()


def classify_name(raw: str) -> tuple[str, str | None, str]:
    """Strip IANA annotation; return (clean_name, annotation, status)."""
    for rx in (_ANNOT_DASH, _ANNOT_PAREN):
        m = rx.match(raw)
        if m:
            sub = m.group('sub').strip()
            ann = m.group('ann').strip()
            # First whitespace-delimited token, alphabetic chars only, lowercase.
            # Strips stray punctuation like the trailing ';' on "OBSOLETE;".
            status = re.sub(r'[^a-z]', '', ann.split()[0].lower())
            return sub, ann, status
    return raw.strip(), None, 'registered'


def extract_supersedee(annotation: str | None) -> str | None:
    if not annotation:
        return None
    m = _SUPERSEDES.search(annotation)
    return m.group('repl').strip() if m else None


def parse_media_types() -> list[dict]:
    tree = ET.parse('/tmp/iana-media-types.xml')
    root = tree.getroot()

    records: list[dict] = []
    seen: set[str] = set()
    for reg in root.findall("iana:registry", NS):
        top = reg.get('id')
        if not top:
            continue
        for record_el in reg.findall("iana:record", NS):
            name_el = record_el.find("iana:name", NS)
            if name_el is None:
                continue
            raw = rtext(name_el)
            if not raw:
                continue
            subtype, annotation, status = classify_name(raw)
            if not subtype or not re.fullmatch(r'[A-Za-z0-9._+\-]+', subtype):
                print(f"  skip (unsafe subtype): {top}/{raw!r}")
                continue
            canon = f"{top}/{subtype}"
            if canon in seen:
                print(f"  duplicate canonical: {canon}")
                continue
            seen.add(canon)
            rec: dict = {
                "registry": "media-types",
                "name": canon,
                "type": top,
                "subtype": subtype,
                "status": status,
            }
            if annotation is not None:
                rec["annotation"] = annotation
                repl = extract_supersedee(annotation)
                if repl:
                    rec["superseded_by"] = repl
            tmpl = None
            for f in record_el.findall("iana:file", NS):
                if f.get('type') == 'template' and f.text:
                    tmpl = f.text.strip()
            if tmpl:
                rec["template"] = tmpl
            refs = []
            counts = {}
            for xref in record_el.findall("iana:xref", NS):
                item = redact_xref(xref)
                if item is not None:
                    refs.append(item)
                    counts[item["type"]] = counts.get(item["type"], 0) + 1
            if refs:
                rec["references"] = refs
                rec["references_count_by_type"] = dict(sorted(counts.items()))
            records.append(rec)

    records.sort(key=lambda r: r["name"].lower())
    return records


def parse_uri_schemes() -> list[dict]:
    tree = ET.parse('/tmp/iana-uri-schemes.xml')
    root = tree.getroot()
    uri_reg = root.find("iana:registry[@id='uri-schemes-1']", NS)
    if uri_reg is None:
        raise SystemExit("uri-schemes-1 registry not found in /tmp/iana-uri-schemes.xml")

    records: list[dict] = []
    for record_el in uri_reg.findall("iana:record", NS):
        v_el = record_el.find("iana:value", NS)
        if v_el is None or not v_el.text:
            continue
        raw_name = rtext(v_el)
        name, annotation, annot_status = classify_name(raw_name)
        if not name or not re.fullmatch(r'[A-Za-z0-9._+\-]+', name):
            print(f"  skip (unsafe uri-scheme name): {raw_name!r}")
            continue
        status_el = record_el.find("iana:status", NS)
        status = (status_el.text if status_el is not None and status_el.text else "Provisional").strip()
        rec: dict = {
            "registry": "uri-schemes",
            "name": name,
            "status": status,
            "type": "uri-scheme",
        }
        if annotation is not None:
            rec["annotation"] = annotation
            repl = extract_supersedee(annotation)
            if repl:
                rec["superseded_by"] = repl
            # Annotation supersedes the IANA <status> when present
            rec["status"] = annot_status
        d_el = record_el.find("iana:description", NS)
        if d_el is not None:
            desc = rtext(d_el)
            if desc:
                rec["description"] = desc
        refs = []
        counts = {}
        for xref in record_el.findall("iana:xref", NS):
            item = redact_xref(xref)
            if item is not None:
                refs.append(item)
                counts[item["type"]] = counts.get(item["type"], 0) + 1
        if refs:
            rec["references"] = refs
            rec["references_count_by_type"] = dict(sorted(counts.items()))
        records.append(rec)

    # Dedup by case-insensitive name (last-wins); preserves IANA-listed case.
    by_name: dict[str, dict] = {}
    for r in records:
        by_name[r['name'].lower()] = r
    return sorted(by_name.values(), key=lambda r: r['name'].lower())


def main() -> None:
    mt = parse_media_types()
    per_type = Counter(r['type'] for r in mt)
    per_status = Counter(r['status'] for r in mt)
    mt_path = ROOT / "data/media-types/iana-media-types.json"
    mt_path.write_text(json.dumps({
        "source": "https://www.iana.org/assignments/media-types/",
        "registry": "media-types",
        "registry_id": "media-types",
        "standard": "RFC 6838",
        "snapshot_date": "2026-10-16",
        "count": len(mt),
        "per_type_counts": dict(sorted(per_type.items())),
        "status_counts": dict(sorted(per_status.items())),
        "records": mt,
    }, indent=2))
    print(f"wrote {len(mt)} media-type records ({mt_path})")
    print(f"  per top-level type: {dict(per_type)}")
    print(f"  by status: {dict(per_status)}")

    us = parse_uri_schemes()
    per_status_us = Counter(r['status'] for r in us)
    us_path = ROOT / "data/uri-schemes/iana-uri-schemes.json"
    us_path.write_text(json.dumps({
        "source": "https://www.iana.org/assignments/uri-schemes/",
        "registry": "uri-schemes",
        "registry_id": "uri-schemes-1",
        "standard": "RFC 3986 / RFC 7595",
        "snapshot_date": "2026-10-16",
        "count": len(us),
        "status_counts": dict(sorted(per_status_us.items())),
        "records": us,
    }, indent=2))
    print(f"wrote {len(us)} uri-scheme records ({us_path})")
    print(f"  by status: {dict(per_status_us)}")


if __name__ == "__main__":
    main()
