#!/usr/bin/env python3
"""parse-iana.py -- convert IANA XML sources to JSON mirrors.

Inputs:  /tmp/iana-media-types.xml, /tmp/iana-uri-schemes.xml
Outputs: data/media-types/iana-media-types.json
         data/uri-schemes/iana-uri-schemes.json
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"iana": "http://www.iana.org/assignments"}
ROOT = Path(__file__).resolve().parent.parent

def text_of(el, tag: str) -> str | None:
    found = el.find(f"iana:{tag}", NS)
    return found.text if found is not None else None


def parse_media_types() -> list[dict]:
    tree = ET.parse("/tmp/iana-media-types.xml")
    records = []
    seen: set[str] = set()
    for record in tree.getroot().iter():
        if record.tag.split("}")[-1] != "record":
            continue
        name = text_of(record, "name")
        if not name or name in seen:
            continue
        seen.add(name)
        rec = {
            "name": name,
            "type": "media-type",
            "template": text_of(record, "template"),
            "status": "registered",
        }
        refs = []
        for xref in record.findall("iana:xref", NS):
            t = xref.get("type", "xref")
            d = xref.text or ""
            if d:
                refs.append({"type": t, "data": d})
        if refs:
            rec["references"] = refs
        records.append(rec)
    records.sort(key=lambda r: r["name"])
    return records


def parse_uri_schemes() -> list[dict]:
    tree = ET.parse("/tmp/iana-uri-schemes.xml")
    root = tree.getroot()
    uri_reg = root.find("iana:registry[@id='uri-schemes-1']", NS)
    if uri_reg is None:
        raise SystemExit("uri-schemes-1 registry not found in /tmp/iana-uri-schemes.xml")
    records = []
    seen: set[str] = set()
    for record in uri_reg.findall("iana:record", NS):
        value = text_of(record, "value")
        if not value or value in seen:
            continue
        seen.add(value)
        rec = {
            "name": value,
            "description": text_of(record, "description"),
            "status": text_of(record, "status") or "registered",
            "type": "uri-scheme",
        }
        refs = []
        for xref in record.findall("iana:xref", NS):
            t = xref.get("type")
            d = xref.get("data")
            if t and d:
                refs.append({"type": t, "data": d})
        if refs:
            rec["references"] = refs
        records.append(rec)
    records.sort(key=lambda r: r["name"])
    return records


def main() -> None:
    mt = parse_media_types()
    (ROOT / "data/media-types/iana-media-types.json").write_text(
        json.dumps(
            {
                "source": "https://www.iana.org/assignments/media-types/",
                "standard": "RFC 6838",
                "snapshot_date": "2026-10-16",
                "count": len(mt),
                "records": mt,
            },
            indent=2,
        )
    )
    print(f"wrote {len(mt)} media-type records")

    us = parse_uri_schemes()
    statuses: dict[str, int] = {}
    for s in us:
        statuses[s["status"]] = statuses.get(s["status"], 0) + 1
    (ROOT / "data/uri-schemes/iana-uri-schemes.json").write_text(
        json.dumps(
            {
                "source": "https://www.iana.org/assignments/uri-schemes/",
                "registry_id": "uri-schemes-1",
                "standard": "RFC 3986 / RFC 7595",
                "snapshot_date": "2026-10-16",
                "count": len(us),
                "status_counts": statuses,
                "records": us,
            },
            indent=2,
        )
    )
    print(f"wrote {len(us)} uri-scheme records")


if __name__ == "__main__":
    main()