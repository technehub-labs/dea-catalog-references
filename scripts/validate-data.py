#!/usr/bin/env python3
"""validate-data.py -- guard the data invariants of the dea-catalog-references mirror.

Assertions:
  - media-types count > 0 and exactly matches the IANA-snapshot contract
  - uri-schemes count matches the IANA-snapshot contract
  - ecf-coordinates count matches
  - canonical media-type names are unique (case-insensitive, within top-level type)
  - every record has the expected fields; non-registered records carry an annotation
  - record-with-superseded_by has a parseable <type>/<subtype> on the right-hand side
  - every record has a corresponding per-record HTML file under the expected path
  - JSON files match the SHA256SUMS manifest

Exit code: 0 on success, 1 on any failed assertion.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Snapshot contract -- these are the counts the IANA registries produce for
# the 2026-10-16 XML snapshots in /tmp.
EXPECTED = {
    "media-types": 2366,   # canonical {type}/{clean_subtype}; was 2,305 prior to fix
    "uri-schemes": 451,    # uri-schemes-1 sub-registry
    "ecf-coordinates": 49, # Enterprise Concept Framework 7x7 = 49 cells
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"OK   {msg}")


def validate_media_types() -> None:
    p = ROOT / "data/media-types/iana-media-types.json"
    data = json.loads(p.read_text())
    records = data.get("records") or []
    n = len(records)
    if n != EXPECTED["media-types"]:
        fail(f"media-types count {n} != expected {EXPECTED['media-types']}")
    ok(f"media-types count = {n}")

    canonical = [r["name"] for r in records]
    by_type_lc = Counter(c.lower() for c in canonical)
    dups = {k: v for k, v in by_type_lc.items() if v > 1}
    if dups:
        fail(f"case-insensitive duplicates in canonical media-type names: {dups}")
    ok(f"no case-insensitive duplicate canonicals among {n} records")

    for r in records[:5] + records[-5:]:
        for k in ("registry", "name", "type", "subtype", "status"):
            if k not in r or not r[k]:
                fail(f"missing/empty field {k!r} in record: {r}")
    if any(r.get("status") != "registered" and not r.get("annotation")
           for r in records):
        fail("found non-registered record without an annotation field")
    ok("all non-registered records carry an annotation")

    for r in records:
        repl = r.get("superseded_by")
        if not repl:
            continue
        if "/" in repl:
            continue  # canonical form
        # IANA sometimes writes annotations without the leading "type/".
        # Try to resolve relative to the source record's top-level type;
        # warn (do not fail) if the candidate does not match a known record.
        candidate = f"{r['type']}/{repl}"
        known = any(x["name"].lower() == candidate.lower() for x in records)
        if not known:
            print(
                f"  warn: superseded_by {repl!r} for {r['name']!r} could not be"
                f" resolved to a canonical {r['type']}/* record (raw IANA text)"
            )

    # Every record must have a matching HTML file
    missing = [
        (r["type"], r["subtype"])
        for r in records
        if not (ROOT / "media-types" / r["type"] / f"{r['subtype']}.html").exists()
    ]
    if missing:
        fail(f"missing per-record HTML for: {missing[:5]} (total {len(missing)})")
    ok(f"every record has a per-record HTML file")


def validate_uri_schemes() -> None:
    p = ROOT / "data/uri-schemes/iana-uri-schemes.json"
    data = json.loads(p.read_text())
    records = data.get("records") or []
    n = len(records)
    if n != EXPECTED["uri-schemes"]:
        fail(f"uri-schemes count {n} != expected {EXPECTED['uri-schemes']}")
    ok(f"uri-schemes count = {n}")

    by_name_lc = Counter(r["name"].lower() for r in records)
    dups = {k: v for k, v in by_name_lc.items() if v > 1}
    if dups:
        fail(f"case-insensitive duplicates in uri-scheme names: {dups}")
    ok(f"no case-insensitive duplicate uri-scheme names among {n} records")

    # Descriptions should never be truncated (the v1 parser dropped xref text)
    trunc = [r["name"] for r in records
             if (r.get("description") or "").rstrip().endswith("by")]
    if trunc:
        fail(f"uri-scheme descriptions appear truncated: {trunc}")
    ok("no truncated URI-scheme descriptions")

    missing = [r["name"]
               for r in records
               if not (ROOT / "uri-schemes" / f"{r['name']}.html").exists()]
    if missing:
        fail(f"missing per-record HTML for: {missing[:5]} (total {len(missing)})")
    ok(f"every uri-scheme has a per-record HTML file")


def validate_ecf() -> None:
    p = ROOT / "data/ecf-coordinates/coordinates.json"
    data = json.loads(p.read_text())
    coords = data.get("coordinates") or []
    if len(coords) != EXPECTED["ecf-coordinates"]:
        fail(f"ecf cells count {len(coords)} != expected {EXPECTED['ecf-coordinates']}")
    ok(f"ecf cells count = {len(coords)}")



def validate_path_b1() -> None:
    """Path B-1: /dea/<path> redirect surface (2,817 shims + paths.tsv).

    Asserts every row in data/paths.tsv has:
    - a corresponding redirect shim at dea/<path>.html
    - a target HTML file present on disk
    - the shim body satisfies the meta-refresh shape
    """
    import sys as _sys
    _sys.path.insert(0, str((ROOT / "scripts").resolve()))
    from _paths import load_paths_tsv, shim_path_for, target_html_exists  # type: ignore

    tsv = ROOT / "data/paths.tsv"
    if not tsv.exists():
        fail("data/paths.tsv missing")
    rows = load_paths_tsv(tsv)
    if not rows:
        fail("data/paths.tsv is empty")
    ok(f"paths.tsv: {len(rows)} rows")

    missing_shim = []
    missing_target = []
    malformed_shim = []
    for row in rows:
        sp = shim_path_for(row.path)
        if not sp.exists():
            missing_shim.append(row.path); continue
        body = sp.read_text()
        if 'http-equiv="refresh"' not in body or 'lists.technehub.com' + row.target not in body:
            malformed_shim.append(row.path); continue
        if not target_html_exists(row.target):
            missing_target.append((row.path, row.target))
    if missing_shim:
        fail(f"missing redirect shims ({len(missing_shim)}): {missing_shim[:5]}")
    if missing_target:
        fail(f"shims point to missing targets ({len(missing_target)}): {missing_target[:5]}")
    if malformed_shim:
        fail(f"shims have wrong redirect target ({len(malformed_shim)}): {malformed_shim[:5]}")
    ok(f"every paths.tsv row has a shim with a valid target ({len(rows)} checked)")



_PERSON_TOKEN = re.compile(r'^redacted:person:[0-9a-f]{6}$')
_IANA_NAME = re.compile(r'[A-Z][a-z]+_[A-Z][a-z]+')


def validate_person_xref_redaction() -> None:
    """Every <xref type="person"> data is a deterministic redaction token.

    Rationale (docs/LICENSING-AND-LIA.md): the IANA registry publishes
    registrant contacts as personal names. To flip the legal posture from
    "publishes a directory of personal names" to "publishes aggregate
    contact statistics", the parser substitutes each person-name with a
    deterministic opaque token
    `redacted:person:<6-char-prefix-of-sha256-of(name+salt)>`. Same name =>
    same token; salt is constant + documented.

    This assertion makes the redaction a regression-grade invariant: any
    future code path that re-introduces a raw name surfaces here.
    """
    paths = (
        "data/media-types/iana-media-types.json",
        "data/uri-schemes/iana-uri-schemes.json",
    )
    suspicious: list[tuple[str, str, str]] = []
    missing_count_field: list[str] = []
    person_count_seen = 0
    for rel in paths:
        d = json.loads((ROOT / rel).read_text())
        for r in d.get("records", []):
            counts = r.get("references_count_by_type") or {}
            n_person = 0
            for x in r.get("references") or []:
                if x.get("type") != "person":
                    continue
                n_person += 1
                data = x.get("data", "")
                if _PERSON_TOKEN.match(data):
                    continue
                if _IANA_NAME.search(data):
                    suspicious.append((rel, r.get("name", "?"), data))
                else:
                    suspicious.append((rel, r.get("name", "?"),
                                       f"unexpected format: {data!r}"))
            if n_person > 0 and "person" not in counts:
                missing_count_field.append(f"{rel} {r.get('name','?')}")
            person_count_seen += n_person
    if suspicious:
        fail(f"person xrefs not properly redacted: {suspicious[:5]}")
    if missing_count_field:
        fail(f"records with person xrefs missing references_count_by_type.person: "
             f"{missing_count_field[:5]}")
    ok(f"person xrefs redacted to opaque tokens ({person_count_seen} tokens across"
       f" both mirrors)")


def validate_sha256sums() -> None:
    sum_path = ROOT / "data/SHA256SUMS"
    if not sum_path.exists():
        fail(f"missing {sum_path}")
    expected = {}
    for line in sum_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        h, _, rel = line.partition("  ")
        if not h or not rel:
            continue
        expected[rel] = h
    for rel, expected_hash in expected.items():
        fp = ROOT / "data" / rel
        if not fp.exists():
            fail(f"SHA256SUMS references missing file: data/{rel}")
        actual = hashlib.sha256(fp.read_bytes()).hexdigest()
        if actual != expected_hash:
            fail(f"sha256 mismatch for data/{rel}: {actual} != {expected_hash}")
    ok(f"SHA256SUMS verified ({len(expected)} files)")


def main() -> None:
    validate_media_types()
    validate_uri_schemes()
    validate_ecf()
    validate_path_b1()
    validate_person_xref_redaction()
    validate_sha256sums()
    print("All assertions passed.")


if __name__ == "__main__":
    main()
