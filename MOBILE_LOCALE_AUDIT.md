# CBT Cards mobile/store locale reconciliation audit

Status: **mobile build verification pending**

Public store metadata rechecked: **19 August 2026**

This file is deliberately separate from `data/locales.json`. The locale registry describes **website publication state** for the public CBT Cards library. It must not be interpreted as a list of languages implemented by the iOS or Android apps.

## Website publication matrix

The current website source of truth is `data/locales.json`:

| Locale | Website state | Machine-readable | Public localized HTML |
| --- | --- | --- | --- |
| `en` English | source | yes | yes, source pages at the default root URLs |
| `ru` Russian | pilot | yes, 12 machine-draft overlays | no published localized records |
| `de` German | planned | no translation overlays yet | no |

These rows describe the website only. A Russian machine draft does not imply Russian app support, and a planned German website locale does not prove a German mobile build exists.

## Apple App Store observation

The public Apple App Store listing rechecked on 19 August 2026 identifies the release as **Version 3.0 CBT** and lists these languages:

- English
- French
- German
- Italian
- Portuguese
- Spanish

This is an observed store listing, not yet a verified app-source matrix. It should be reconciled against the exact iOS build/source before CBT Cards describes those six languages as implemented mobile locales outside the store observation itself.

## Google Play observation

The public Google Play listing rechecked on 19 August 2026 did not expose enough language/build metadata in the retrieved public surface to establish a complete Android locale matrix. Android language support therefore remains **unverified** in this audit until the current distributed build, app resources, and Play Console localization settings are inspected together.

## Historical project notes

Earlier project/release notes referenced additional languages such as Japanese, Chinese, Korean, Arabic, and Swedish. Those historical references are not treated as current support. They remain unverified until tied to a current mobile source commit/build and current store configuration.

## Required verification before issue #5 can close

1. Record the current iOS source commit/tag and distributed App Store build corresponding to Version 3.0 CBT.
2. Inspect the app's actual iOS localization resources and runtime locale configuration.
3. Record the current Android source commit/tag and distributed Google Play version/build.
4. Inspect Android localization resources and runtime locale configuration.
5. Export or record current App Store localization settings and supported-language metadata.
6. Export or record current Play Console store-listing/localization settings.
7. Reconcile discrepancies between source/build and store metadata instead of copying one into the other.
8. Decide which mobile languages, if any, should also become website publication candidates.
9. Create website locale records only through the existing planned → pilot → human-reviewed/published workflow; store support alone is not publication review.
10. For every published website locale, verify reciprocal `hreflang`, self-canonical URLs, localized metadata/structured data, mobile/desktop language navigation, and reviewed health-adjacent wording.

## Rule for agents and maintainers

Use `data/locales.json` and `data/translations.jsonl` to answer questions about the public website/library. Use verified mobile build/store evidence to answer questions about app-language support. Do not infer one from the other.
