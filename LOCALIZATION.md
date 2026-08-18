# CBT Cards localization workflow

CBT Cards keeps source content, translation drafts, editorial review, and public publication as separate states. This is especially important for health-adjacent reflection material: a readable translation is not automatically an approved translation.

## Sources of truth

- `data/knowledge.jsonl` contains the current curated source-language records. English (`en`) is the current source locale.
- `data/locales.json` defines locale lifecycle and whether a locale may expose machine-readable data or public HTML.
- `data/translations.jsonl` contains localized overlays keyed by stable `resource_id` + `locale`.
- `scripts/check_localization.py` validates translation state, source snapshots, and publication boundaries.
- `scripts/build_localized_pages.py` deterministically renders `/languages/`, public locale hubs, localized resource pages, and the generated localization block in `sitemap.xml`.

Do not edit generated localized HTML directly. Change the locale/translation source data and regenerate it.

## Translation states

### Machine draft

A machine-generated or otherwise unreviewed translation must remain:

- `translation_status: machine_draft`
- `review_status: unreviewed`
- `publication_status: not_published`
- `canonical_url: null`
- `reviewed: null`

Machine drafts may exist as public machine-readable development data when the locale registry allows it. They must not be described as official CBT Cards translations and must not produce localized HTML.

### Human reviewed, not yet published

After a qualified human language/editorial review, a record may move to:

- `translation_status: human_reviewed`
- `review_status: reviewed_for_publication`
- `publication_status: not_published`
- `canonical_url: null`
- `reviewed: YYYY-MM-DD`

This state is useful when review is complete but the localized public surface is not ready to ship.

### Published localization

A reviewed translation may be published only when:

- the locale has `public_html: true` in `data/locales.json`;
- the record is `human_reviewed` and `reviewed_for_publication`;
- `publication_status` is changed to `published`;
- `canonical_url` is exactly `https://cbt-cards.github.io/<locale>/resources/<resource_id>/`;
- `reviewed` records the actual human review date;
- `source_reviewed` still matches the current source record's `reviewed` value.

Run the generator after these data changes:

```bash
python3 scripts/build_localized_pages.py --write
```

Then run the full checks before committing generated output:

```bash
python3 scripts/check_localization.py
python3 scripts/check_site.py
python3 scripts/check_crawl_graph.py
python3 scripts/check_schemas.py
```

The generator manages the human language-status page, public locale hubs, localized resource pages, and the generated localization section of the sitemap. The normal repository checks still verify canonical URLs, internal links, crawl depth, catalog targets, and other site-wide invariants.

## Human review checklist

A reviewer should compare the localized record with the exact source record referenced by `resource_id` and confirm all of the following before changing `translation_status` to `human_reviewed`:

1. The title and summary preserve the practical meaning without strengthening health or efficacy claims.
2. Every `key_points` item corresponds to the same source item and preserves sequence where sequence matters.
3. `product_relation` accurately describes CBT Cards and does not invent app behavior, privacy behavior, or clinical interpretation.
4. `safety_scope` is at least as clear as the source and does not weaken the general-wellness boundary.
5. Terms such as CBT, diagnosis, treatment, clinical validation, anxiety, grounding, and cognitive distortion are translated consistently and appropriately for the locale.
6. The translation does not turn neutral reflection prompts into commands that sound like individualized treatment instructions.
7. The source record has not changed since the draft was produced. `source_reviewed` must equal the current source record `reviewed` date.
8. The reviewer has actually reviewed the localized wording. AI generation or AI self-review alone is not recorded as `human_reviewed`.

`reviewed_for_publication` means editorial and safety review for CBT Cards public use. It does not mean clinical validation, evidence of efficacy, or suitability for an individual.

## Incremental rollout

`public_html` is a locale-level capability switch, not a claim that every translation in that locale is published. A locale may contain a mixture of published human-reviewed records and unpublished machine drafts.

This allows gradual rollout. For example, Russian can publish two reviewed resources while ten other Russian records remain machine drafts. Each record keeps its own publication status, and the generator exposes only records explicitly marked `published`.

## Adding a new locale

1. Add the locale to `data/locales.json` as `planned` with `machine_readable: false` and `public_html: false`.
2. When translation work begins, promote it deliberately to `pilot` and enable `machine_readable` if draft overlays should be publicly inspectable.
3. Add translation records keyed by existing stable source IDs.
4. Add localized generator interface labels in `scripts/build_localized_pages.py` before enabling `public_html`.
5. Do not enable public HTML until at least one record has completed human/editorial review and the localized page wording has been checked in context.
6. Record meaningful locale or publication changes in the public changelog.

Do not create a second independent source tree for translated content. The stable source record plus locale overlay is the contract.
