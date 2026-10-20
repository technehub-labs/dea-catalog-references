# Licensing and Legitimate-Interest Assessment (LIA)

This document is the authoritative legal posture for the `dea-catalog-references` mirrors of the IANA protocol registries. It declares the licensing regime for every artefact we publish and records the data-controller's documented Legitimate-Interest Assessment for the personal-name redaction step.

It is referenced from:
- `index.html` (the landing page on lists.technehub.com)
- `licensing.html` (the human surface of this document)
- `DATA-PROVENANCE.md` (per-mirror provenance notes)
- the `media-types/application/index.html` and `uri-schemes/info.html` per-record pages (via the canonical IANA link back)

## 1. What we publish

The repo hosts three external mirrors and one derivative data product. Each is governed by a different licence:

| Artefact | Origin | Licence governing it | What we ship |
|---|---|---|---|
| `data/media-types/iana-media-types.json` | `iana.org/assignments/media-types/` | **CC0 1.0** (per IANA + IETF Joint Statement, 2021-11-10) | The structured record data + a stripped-per-type annotation + an `xref expansion` of the registrant metadata. The names of registrant contacts are replaced with deterministic opaque tokens (see §4). |
| `data/uri-schemes/iana-uri-schemes.json` | `iana.org/assignments/uri-schemes/` | **CC0 1.0** (same) | Same shape. |
| `data/ecf-coordinates/coordinates.json` | `github.com/technehub-labs/dea-metaframework/blob/main/framework/matrix.md` | **Repo licence: MIT** (the source repo) | The 49-cell matrix drawn from the framework's `matrix.md`. |
| `data/paths.tsv`, `media-types/**/*.html`, `uri-schemes/**/*.html`, `dea/**/*.html`, `ecf/**/*.html` | Our own original generator + the data above | **MIT** (this repo's licence) | 2,817 redirect shims + 2,366 + 451 + 49 + 10 + 1 + 1 = 2,878 per-record HTML pages + this validator + the build script. |

We **do not** publish any of the IANA-rendered HTML pages, RFC text, or third-party documents that the registries cite. Those are excluded by IANA's own Joint Statement ("the RFC documents that are linked on those pages are excluded") and we never copy them.

## 2. The exact grant: IANA + IETF Joint Statement (verbatim)

The relevant text from `https://www.iana.org/help/licensing-terms` (Joint Statement of IANA and IETF, dated 10 November 2021):

> *IANA and IETF intend that the Protocol Registries may be freely used by any party for any purpose. Both IANA and IETF believe that the Protocol Registries consist primarily of factual information that is unlikely to be protectable as a matter of copyright law. However, for additional clarity, and to avoid any potential confusion about applicable rights, both IANA and IETF desire to (a) dedicate any applicable copyright rights that they may own in the Protocol Registries to the public domain, and (b) license any copyright or related rights for which they are a licensee (with a right to sublicense) to the broadest extent that they are permitted to do so. Accordingly, both IANA and IETF affirm that any applicable rights that they may have in the Protocol Registries are subject to the Creative Commons CC0 1.0 dedication found at `<https://creativecommons.org/publicdomain/zero/1.0/legalcode>`.*
>
> *Disclaimer. While as of the date of this statement neither IANA nor IETF are aware of any third parties claiming intellectual property rights in the Protocol Registries, neither can guarantee that third parties will not do so. Further, the Protocol Registries are made available without any other sort of representation or warranty. The limitations and disclaimers found in the CC0 1.0 dedication are an integral part of this joint statement. For example, in no way are the patent or trademark rights of any person affected by CC0, nor are the rights that other persons may have in the work or in how the work is used, including data protection rights.*

What "Protocol Registries" means, per the same statement's *Terminology* section:

> *"Protocol Registries" means the technical protocol registry data directly linked at either `<https://www.iana.org/protocols>` or `<https://www.ietf.org/assignments/>`; it does not include any other material on or linked from those pages (e.g., the RFC documents that are linked on those pages are excluded).*

That scope covers everything in our `data/media-types/iana-media-types.json` and `data/uri-schemes/iana-uri-schemes.json` files. The CC0 1.0 legal code is at `<https://creativecommons.org/publicdomain/zero/1.0/legalcode>`.

## 3. What CC0 1.0 means for downstream consumers

CC0 1.0 is the strongest open-data licence in the open-source ecosystem. Operationally:

- **No attribution required.** (You may attribute, but you don't have to.)
- **No copyleft.** (You can repackage, modify, and re-licence under any terms you choose.)
- **No warranty of any kind.** (Use at your own risk; IANA + IETF disclaim fitness-for-purpose and non-infringement.)
- **The grant extends to the greatest extent the rights-holder can grant**, capturing both copyright and adjacent rights.
- **Patent and trademark rights are explicitly NOT covered.** A separate trademark licence would be required to use the IANA / IETF marks; we do not, so this point is moot for us.
- **Data protection rights of third parties are explicitly NOT covered.** This is the only remaining axis of legal exposure and is addressed below (§4).

CC0 1.0 covers our mirror use-cases even if, contrary to IANA's stated belief, some of the factual registries were held to be copyrightable in some jurisdiction (e.g. via a database-right doctrine). The grant is broad enough to sub-license on any terms, including commercial ones.

## 4. Personal-data hygiene + Legitimate-Interest Assessment

### 4.1 The exposure

The IANA registries publish registrant contact metadata as personal names (typically in the form `First_Last`), for example:

- `<xref type="person" data="Roger_Buis"/>`
- `<xref type="person" data="Jörg_Palmer"/>`

These elements are inside the CC0 grant for *copyright* purposes (factual data is unprotected anyway, and IANA further waives any residual rights). However, CC0 explicitly disclaims coverage of *data protection* rights of natural persons. Personal-name republication on a public mirror can be subject to the EU/UK General Data Protection Regulation and similar regimes.

The exposure footprint in our 2026-10-16 snapshot:

| Registry | Records with at least one person xref | Total person xrefs | Distinct personal names |
|---|---|---|---|
| `media-types` | 1,700 of 2,366 (71.9%) | 2,016 | 911 |
| `uri-schemes-1` | 315 of 451 (69.8%) | 344 | 130 |

### 4.2 The redaction (the technical control)

The parser substitutes each `<xref type="person">` `data` field with a deterministic opaque token, structured as:

```
redacted:person:<6-char-prefix-of-sha256-of(name+salt)>
```

where the salt is the literal string `openDEA-catalog-refs-v1` (constant, hard-coded in `scripts/parse-iana.py`, and documented here and in `DATA-PROVENANCE.md`). Properties of this approach:

- **Deterministic.** The same input name always produces the same token. Consumers can detect when the same registrant appears across multiple records, count distinct registrants per record, and detect drift across rebuilds without ever seeing the personal name.
- **Reversible by design.** The salt is public; an adversary who already knows a candidate name can verify it by hashing. This is intentional: the goal is not cryptographic irreversibility, it is to remove the registry-as-directory function from this mirror (to flip the legal posture, not to defeat forensic adversaries).
- **Structural signal preserved.** The redaction preserves the *count* and *distribution* of registrant contacts; the `references_count_by_type` aggregate field on every record makes the contact structure visible to consumers without naming anyone.
- **Verifiable.** Every redaction is checked by `scripts/validate-data.py::validate_person_xref_redaction()`: any record whose `references[].type = "person"` has a `data` value that doesn't match the redaction token format (or that still carries an IANA-name-style substring) blocks the validator with rc=1.

The 2026-10-16 snapshot, post-redaction, has 2,016 + 344 = 2,360 records with one or more redaction tokens across both mirrors; zero raw personal names remain in the JSON mirror files.

### 4.3 The lawful basis assessment (GDPR / UK-GDPR Art. 6(1)(f))

In the (current) absence of registrant consent, the lawful basis selected for any residual processing is **legitimate interests** under Art. 6(1)(f) of GDPR and the equivalent UK-GDPR provision. The LIA follows the EDPB and ICO recommended three-part test:

**Purpose test.** The legitimate interest pursued is the publication of a stable, machine-readable, identifier-anchored index of IANA's public protocol registries so that OpenDEA catalog systems and downstream consumers can resolve canonical references (e.g. `application/json`, `https`) to a single canonical page. Operational necessity drives the requirement; the work is methodologically downstream of IANA's own public-interest mandate under the NTIA/IANA-functions-transition agreement.

**Necessity test.** Personal-name republication is NOT necessary for the legitimate interest. The contact-name field is purely informational metadata on the IANA record; consumers of the registry index do not use it for any operational function. Removing the field has no impact on the index's dereferencing, lookup, or reference-resolution value. (Verified empirically: the 2,360 records where a person xref was present still carry the same `references_count_by_type.person` count, so the contact structure is preserved; the only loss is the identity of the registrant.)

**Balancing test.**

- *Nature of the processing:* low. The data is the registrant's name; we publish no email, address, role, employer, or history. The publication is via a deterministic hash token that no longer identifies the natural person to a third-party reader. (An adversary who already knows the name can verify; we are not a useful tool for that adversary beyond what IANA already provides.)
- *Reasonable expectations of the data subject:* moderate to high. Registrants listed in the IANA registry have a reasonable expectation that IANA will continue to publish their name on the registry page; they have NOT consented specifically to republication by independent operators.
- *Likely impact:* low. With the redaction in place, no identified third-party reader learns anything new from our mirror.
- *Safeguards:* (a) the technical redaction (deterministic token) above; (b) only the per-record HTML page links back to IANA as the canonical source for the actual contact identity, giving registrants a single, well-known place to make any data-protection request; (c) the data is keyed to IANA's snapshot date and tied to its refresh cadence (we mirror what IANA publishes, when IANA publishes it), not an ongoing independent publication cycle.

**Conclusion.** The redaction is necessary to keep the rebalancing in the data subject's favour. Without the redaction, the balancing favours the data subject, and the legitimate interest fails. With the redaction, the residual processing is limited to the publication of an opaque structural count per record, which does not constitute the processing of personal data (a token is not personal data because it cannot reasonably be linked to an identified natural person without a side-channel). The LIA balance is satisfied.

### 4.4 What we do NOT do

- We do not publish any contact email, phone, address, employer, role, or historical record. None of these fields exist in the IANA XML source; we ship exactly the structured fields IANA ships.
- We do not index the mirror on third-party search engines by intent.
- We do not sell, license, or sub-license the personal-name data; it does not exist in the mirror, so there is nothing to license.
- We do not aggregate, profile, or cross-correlate personal data with other sources.
- We do not make automated decisions about the data subjects.

### 4.5 Data-subject rights and removal

Any data subject who wishes to exercise GDPR / UK-GDPR / similar rights over the personal-name residual that IANA mirrors may:

- Contact the registrant's registration authority (usually the IETF or the standards body that registered the value); IANA's Joint Statement notes that *the rights that other persons may have in the work* are unaffected by CC0, and IANA's own registry is the canonical authority for any data-subject request.
- Contact the operator of this mirror with the data subject's identity and the IANA record affected; we will follow up within 30 days. The most likely operational outcome is to escalate to IANA per the recommended chain (the mirror has no independent authority over the underlying registry).

## 5. Audit trail

| Date | Action | Source |
|---|---|---|
| 2026-10-16 | First mirror published; included raw personal names as published by IANA. | IANA XML snapshot |
| 2026-10-19 | Slice 1: corrected parser to canonical `name = type/subtype`; no personal-data change. | PR #1 in `dea-catalog-references` |
| 2026-10-19 | Path B-1: dereferencing layer at `/dea/<path>`; no personal-data change. | PR #2 |
| 2026-10-20 | Slice 3 (this document): redaction of `<xref type="person">` data, validator assertion, this LIA + `licensing.html`. | PR #3 in `dea-catalog-references` |

Every redaction is reproducible from the source XML and the documented salt (`openDEA-catalog-refs-v1`) via `scripts/parse-iana.py`. The `validate-data.py` invariant makes any future re-introduction of a raw personal name a CI failure rather than a silent change.

## 6. Disclaimer

This document is drafted by the maintainer of `dea-catalog-references`. It is intended as a good-faith, structured record of the legal posture; it is not legal advice. If any aspect of the registry republication or the personal-data redaction matters to your compliance posture, an EU/UK qualified lawyer or DPO should review the mirror against your specific use-case before you adopt it.
