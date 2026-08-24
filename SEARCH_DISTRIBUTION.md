# Search distribution and citation growth

Baseline: **19 August 2026** · Outreach requalification updated: **20 August 2026** · Public URL inventory updated: **24 August 2026**

This is the operating plan for search discovery, webmaster-tool measurement, IndexNow evidence, and selective external citation outreach after the CBT Cards public-library pivot. It deliberately separates observable facts from account-only metrics. A `site:` search sample is not an official index count, and a green deploy alone is not proof that a notification request authenticated successfully.

## Current baseline

The canonical website is `https://cbt-cards.github.io/`. The current sitemap contains **42 public URLs**, including the CBT Cards-owned content library, Contact, Partnerships, the AI get-started guide, and the separately sourced mobile release-history page. Russian machine-draft and German planned previews are `noindex` and excluded. `robots.txt` explicitly allows `OAI-SearchBot`, allows other compliant crawlers, and declares the sitemap.

A limited external search sample on 19 August 2026 used four site-scoped queries covering the domain, learning pages, worksheets, and toolkit pages. One CBT Cards result was observed, `/features/`, with the search result reporting a crawl age of roughly three weeks. The newer learn/worksheet/toolkit child pages did not appear in that limited sample.

That is a **partial discovery observation**, not a claim that only one page is indexed. Official Google indexed/submitted counts require Google Search Console; Bing counts require Bing Webmaster Tools. Until those accounts are connected and queried, `data/search-measurement.json` leaves the official fields null rather than inventing numbers from search-result sampling.

The older MetalHatsCats product/toolkit surfaces remain a separate distribution problem. See `LEGACY_REDIRECT_AUDIT.md`; the standalone CBT Cards site must not compensate for missing external redirects by reintroducing legacy URLs as canonicals.

## Crawler and submission controls

- `robots.txt` explicitly allows `OAI-SearchBot` and does not block normal compliant search crawlers.
- `sitemap.xml` is the canonical public URL inventory.
- `scripts/notify_indexnow.py` submits changed public HTML URLs only after a successful Pages deployment.
- IndexNow produces a machine-readable receipt containing execution time, URL count/list, endpoint result, and success/failure state.
- The IndexNow job is not hidden behind `continue-on-error`. Deployment happens first, so an IndexNow outage cannot undeploy the site, but the workflow shows the notification failure.
- Search Console and Bing Webmaster sitemap submission remain external-account operations. They should be recorded in the measurement ledger when verified.

## Eight-week measurement window

`data/search-measurement.json` contains eight weekly checkpoints from 26 August through 14 October 2026. Each checkpoint keeps Google, Bing, referral, landing/query, and external-citation metrics separate.

The preferred measurements are aggregate webmaster-tool data. CBT Cards should **not** add client-side analytics merely to fill a dashboard. GitHub Pages does not provide the server-side referral log needed to measure every store-link or AI-search referral, so those fields remain null until a privacy-compatible measurement source is deliberately chosen.

For each weekly checkpoint, record what is actually available:

- submitted and indexed URLs;
- impressions, clicks, CTR, and average position where the provider exposes them;
- top landing pages and queries;
- store-link referrals only if a privacy-compatible source exists;
- identifiable AI-search referrals only when there is a defensible source rather than guesswork;
- external linking domains, especially citations to worksheet/toolkit/practice pages.

A missing metric is `null`, not zero. Zero means the measurement source explicitly reported zero.

## Outreach policy

`data/outreach-targets.json` contains 12 researched targets across curated mental-health resource lists, Agent Skills catalogs/directories, automated skill indexes/research corpora, and resource directories.

The list is a queue, not a mail merge. Outreach should be selective:

1. Recheck the target's current contribution/submission rules immediately before contact.
2. Use the smallest canonical CBT Cards URL that actually fits the target. Mental-health resource lists should usually receive `/worksheets/` or `/practice/`; agent catalogs should receive the portable `SKILL.md`.
3. Preserve the project's general-wellness, publication-review, evidence, translation, privacy and licensing boundaries. Do not pitch CBT Cards as clinically validated treatment.
4. Prefer a pull request or documented submission flow over unsolicited email when the target is an open-source catalog.
5. Do not force CBT Cards into a directory whose scope does not fit merely to increase backlink count.
6. Do not encourage redistribution that exceeds the current public license. `LICENSING_DECISION.md` is a pending decision memo, not a new grant.
7. Record contact/submission URL, date, result, and resulting canonical link in the target record when outreach actually occurs.

## Current high-fit targets

The 19–20 August process rechecks changed several targets from vague `not_contacted` entries into explicit execution states:

- `dreamingechoes/awesome-mental-health` is topically suitable for the reviewed practice library. Its current guide requires one pull request per resource and permits small tools/apps without treating them as therapy-efficacy submissions. The content fit is ready, but the connected GitHub environment cannot fork the target repository, so the target is `ready_requires_fork` rather than falsely `submitted`.
- `theimpossibleastronaut/awesome-mentalhealth` is a strong fit for the free browser-local worksheets and accepts English HTTPS resources. No documented issue-based suggestion path was found; repository contribution remains the defensible route, so it is also `ready_requires_fork` here.
- Agent Skill Exchange requires a fork + pull request into its catalog. The technical fit is strong, but the same fork limitation applies and any copied/adapted skill must retain CBT Cards' active license rather than inherit a catalog license by implication.
- `block/agent-skills`, the source repository for the Goose Skills Marketplace, was rechecked on 20 August. Its current contribution guide explicitly requires a fork, branch, root-level skill folder and pull request, with CI validation. The technical fit is strong, but the connected GitHub environment cannot perform the required fork, so it is `ready_requires_fork`; its Apache-2.0 repository license also means any future copied CBT Cards skill must preserve the actual CBT Cards license explicitly.
- `dmgrok/agent_skills_directory` now resolves to `dmgrok/agent-plugins`. Its New Provider issue flow is technically executable and automated, but the current template explicitly expects a permissive-style repository license such as MIT or Apache 2.0. CBT Cards remains CC BY-NC-SA 4.0, so this target is `blocked_by_catalog_license_policy` until issue #7 is deliberately resolved.
- `JPeetz/agent-skills` is similarly held behind its current skill-license expectations rather than being submitted with a mislabeled license.

This requalification matters: a distribution target can be a strong topical/technical fit and still be ineligible today. Outreach counts should reflect actual submissions and acceptances, not merely researched names.

## Completion boundary for issue #9

The repository can provide crawler access, sitemaps, IndexNow evidence, measurement contracts, and a researched outreach queue. Closing the issue still requires external observations over time:

- verified Google Search Console property/sitemap and baseline data;
- verified Bing Webmaster Tools property/sitemap and baseline data;
- at least one inspected successful production IndexNow receipt;
- weekly data filled for the intended eight-week period as time passes;
- actual selective outreach/citation outcomes rather than a list of targets alone.

Search growth is deliberately treated as measured distribution work, not as proof that adding more meta tags eventually summons traffic through ritual repetition.
