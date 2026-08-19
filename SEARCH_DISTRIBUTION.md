# Search distribution and citation growth

Baseline: **19 August 2026**

This is the operating plan for search discovery, webmaster-tool measurement, IndexNow evidence, and selective external citation outreach after the CBT Cards public-library pivot. It deliberately separates observable facts from account-only metrics. A `site:` search sample is not an official index count, and a green deploy alone is not proof that a notification request authenticated successfully.

## Current baseline

The canonical website is `https://cbt-cards.github.io/`. The current sitemap contains **38 public URLs**, including the separately sourced mobile release-history page. `robots.txt` explicitly allows `OAI-SearchBot`, allows other compliant crawlers, and declares the sitemap.

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

Highest-priority candidates include `dreamingechoes/awesome-mental-health` for the reviewed public practice library, Agent Skill Exchange, `dmgrok/agent_skills_directory`, Block/Goose Agent Skills, and `JPeetz/agent-skills` for the portable skill. Other targets need format, eligibility, licensing, or submission-path checks first. The machine-readable queue explains those tradeoffs so “10 targets” does not become 10 irrelevant pitches.

## Completion boundary for issue #9

The repository can provide crawler access, sitemaps, IndexNow evidence, measurement contracts, and a researched outreach queue. Closing the issue still requires external observations over time:

- verified Google Search Console property/sitemap and baseline data;
- verified Bing Webmaster Tools property/sitemap and baseline data;
- at least one inspected successful production IndexNow receipt;
- weekly data filled for the intended eight-week period as time passes;
- actual selective outreach/citation outcomes rather than a list of targets alone.

Search growth is deliberately treated as measured distribution work, not as proof that adding more meta tags eventually summons traffic through ritual repetition.
