# Machine-readable data licensing decision

Status: **pending publisher and legal approval**

Prepared: **19 August 2026**

This document records a licensing decision that has **not** been made yet. It does not grant CC BY 4.0, CC0, commercial-use permission, or any other new reuse right. Current rights remain governed by `LICENSE`, record-level license metadata, and any more specific source terms.

This is a publisher/engineering decision record, not legal advice.

## Current position

The repository currently uses **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**. Commercial reuse is not permitted under that license without separate permission, attribution is required, and adaptations must use the same license.

The public machine-readable surface is not one homogeneous rights object:

- `data/catalog.json` is CBT Cards-owned resource metadata and currently points to the repository `LICENSE`.
- `data/knowledge.jsonl` contains six CBT Cards-owned learning records and six records adapted from the pinned MetalHatsCats CBT Toolkit.
- the pinned MetalHatsCats CBT Toolkit v0.1.0 is documented as CC BY-NC-SA 4.0 in `data/toolkit-source.json`;
- the eleven-record reviewed practice system, its RAG chunks, schemas, evals, and most project metadata are CBT Cards-owned repository material under the current default terms unless a file says otherwise;
- the current Agent Skill v1.8.0 explicitly declares `CC-BY-NC-SA-4.0` in its frontmatter;
- product artwork and brand identifiers are not part of any future permissive **data** grant merely because they live in the same repository;
- CBT Cards names, logos, and trademark rights are not granted by the Creative Commons license.

`data/knowledge.jsonl` is therefore a mixed-provenance distribution. A single permissive file-level label must not be applied to it until every record is covered by the proposed terms or the file is split into independently licensed distributions.

## Decision goals

The publisher needs to decide which of these goals actually matters:

1. Should commercial AI assistants, RAG systems, search products, and paid integrations be allowed to reuse CBT Cards-owned machine-readable data without separate permission?
2. Should attribution remain a legal condition of reuse, or only a preferred citation practice?
3. Is ShareAlike desirable for machine-readable derivatives, or does it create too much integration friction?
4. Which exact datasets are intended for permissive reuse?
5. Does MetalHatsCats have the necessary rights to offer additional terms for the source-derived toolkit records, or should those records stay under CC BY-NC-SA 4.0?
6. Should the Agent Skill itself stay NC-SA even if selected datasets become permissive?
7. Which assets must be explicitly excluded from any new data grant?

## Option A: keep CC BY-NC-SA 4.0 everywhere

**Effect:** no licensing change.

Benefits:

- simplest rights model;
- source-derived knowledge records and source toolkit remain aligned;
- attribution, NonCommercial, and ShareAlike remain mandatory under the existing license.

Tradeoffs:

- commercial agent/RAG reuse requires separate permission;
- some commercial catalogs, research corpora, and integrations may avoid the material or be unable to redistribute it;
- ShareAlike can be difficult to apply cleanly to composite retrieval systems.

Choose this option if restricting commercial reuse is intentional rather than accidental friction.

## Option B: CC BY 4.0 for explicitly enumerated CBT Cards-owned machine data

**Effect if later approved:** commercial reuse and adaptation of the approved data scope would be allowed while attribution and change indication remain required under CC BY 4.0.

This is the recommended technical path **if** the publisher wants commercial agent/RAG reuse while retaining legally enforceable attribution.

A safe implementation would be scoped, not repository-wide:

- keep the repository/default editorial and artwork terms unchanged unless separately decided;
- enumerate the exact CBT Cards-owned datasets receiving CC BY 4.0;
- keep toolkit-source material and toolkit-derived records under CC BY-NC-SA 4.0 unless the rights holder confirms authority and explicitly approves additional terms;
- split mixed distributions, or add record-level licensing that makes the effective rights unambiguous to a consumer;
- keep brand/trademark rights outside the grant;
- preserve canonical URLs/source IDs as attribution and provenance aids.

Likely candidates for a future scoped CC BY 4.0 grant, subject to publisher/legal review, include CBT Cards-owned catalog metadata, the six original learning knowledge records, the reviewed practice/ontology/evidence/relation/recommendation/RAG layer, evaluation datasets authored by CBT Cards, and selected schemas/metadata.

The six `source-card-*` knowledge records are **not** automatically in that candidate set. They are adaptations of toolkit records and need a separate rights decision.

## Option C: CC0 for narrow factual metadata only

**Effect if later approved:** CC0 attempts to waive copyright and related/database rights as broadly as legally possible for the approved scope.

This can be appropriate for narrow factual metadata such as identifiers, canonical URLs, counts, or compatibility indexes when maximum machine reuse matters more than attribution enforcement.

It is a poor fit if the publisher wants attribution to remain a legal condition. Under CC0, a canonical link or credit can still be requested as good practice, but that request is not the same as a copyright-license requirement.

Do not use CC0 as a shortcut for editorial practice text, source-derived toolkit content, artwork, or brand assets without an explicit rights and product decision.

## Option D: separate commercial permissions / dual licensing

The existing CC BY-NC-SA license is non-exclusive. A rights holder can separately offer commercial permission or other terms for material it controls.

This can preserve the current public NC-SA baseline while enabling approved partners. It also creates operational overhead: permission records, scope/version tracking, and partner-specific terms become part of the product surface. Use it only if that overhead is intentional.

## Mixed `knowledge.jsonl` problem

The current 12-record file is deliberately useful for retrieval, but licensing cannot pretend provenance disappeared during curation.

Current record groups:

### CBT Cards-owned learning records

- `cbt-thought-record`
- `automatic-thoughts`
- `thought-vs-fact`
- `worry-time`
- `activity-planning`
- `cbt-journaling`

These can be considered for a future CBT Cards-owned permissive data grant after publisher/legal approval.

### Toolkit-derived records

- `source-card-4`
- `source-card-15`
- `source-card-16`
- `source-card-21`
- `source-card-27`
- `source-card-32`

These retain an explicit toolkit provenance and current CC BY-NC-SA 4.0 source-license reference. Before offering them under additional terms, confirm the rights holder and authority to relicense the adapted material. If that authority is not confirmed, keep them NC-SA and split any future permissive distribution so consumers cannot mistake the file for a single-license dataset.

## Attribution and canonical-link policy

Under the current CC BY-NC-SA 4.0 terms, appropriate credit, a license link, and change indication are required. A useful machine-readable attribution should normally preserve:

- `CBT Cards` / `MetalHatsCats` as the identified source/publisher where applicable;
- the record's canonical CBT Cards URL;
- the applicable license URL;
- stable source/record IDs where present;
- source-toolkit attribution for toolkit-derived records;
- an indication when wording or structure was changed.

A canonical URL is strongly preferred because it preserves review, safety, provenance, and update context. Do not describe that preferred URL format as a new legal condition beyond the applicable license text.

## Brand and asset boundary

Any future permissive **data** grant should explicitly exclude unless separately approved:

- CBT Cards names and logos as trademarks/brand identifiers;
- app icon and branded product artwork;
- screenshots or third-party assets whose rights are not independently confirmed;
- third-party source material merely linked or quoted by CBT Cards;
- any source-toolkit content outside the rights actually controlled by the licensor.

A data license does not authorize endorsement or use of CBT Cards branding to imply an official integration.

## Agent Skill boundary

The current skill v1.8.0 declares `license: CC-BY-NC-SA-4.0`. A future permissive data decision does not silently change the skill license. If the skill should become CC BY 4.0 or another license, release a new immutable skill version and update the alias, manifest, catalog, install docs, changelog, and portability checks deliberately.

## Implementation plan after a publisher decision

If Option B is approved:

1. Record publisher approval date, approver, scope, and legal-review status in this decision record or a dedicated approval record.
2. Enumerate exact paths/record IDs covered by the new grant.
3. Confirm rights for every source-derived record before including it.
4. Split mixed distributions when different licenses would otherwise apply to one file ambiguously.
5. Add explicit `license_id`/`license_url` metadata to each covered dataset/record and its schema.
6. Update `/agents/`, README, `llms.txt`/`llms-full.txt`, catalog discovery, citation guidance, and RAG manifests.
7. Keep artwork/trademark exclusions visible next to the permissive data grant.
8. Add CI that rejects any record whose license metadata conflicts with its provenance group.
9. Publish a changelog entry stating that a data-license release is not a relicensing of excluded artwork, trademarks, or third-party/source content.
10. Re-evaluate external skill/data directories that are currently blocked by NC-SA terms.

If Option A is approved, record that decision explicitly too. “No change” should still be deliberate rather than perpetual ambiguity.

## Official license references used for the decision

- CC BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/
- CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
- CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/
- Creative Commons licensing considerations and database guidance: https://creativecommons.org/share-your-work/cclicenses/ and https://creativecommons.org/faq/

These links explain the license mechanisms. They do not replace publisher/legal review of CBT Cards' specific rights and mixed-provenance files.
