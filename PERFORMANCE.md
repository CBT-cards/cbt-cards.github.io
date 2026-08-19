# Asset performance baseline and decision

Measured: 2026-08-19

This document records the lab measurement used for the CBT Cards asset-performance change. It is a reproducible engineering benchmark, not field Core Web Vitals data and not a promise that every network/device will see the same timings.

## Decision

CBT Cards keeps the existing visual identity and original PNG/TTF files as source or fallback assets where useful, but the normal web path now prefers:

- responsive WebP sources for large body illustrations;
- WOFF2 for the two bundled Nunito web fonts;
- a small WebP header icon while retaining the PNG favicon/web-manifest icon;
- a purpose-built 1200×630 JPEG for Open Graph previews instead of a multi-megabyte portrait illustration;
- explicit intrinsic image dimensions and existing alt text;
- eager/high-priority loading for the above-the-fold home hero and lazy/async loading for below-the-fold illustrations.

No CDN, client-side image library, JavaScript loader, or new runtime dependency was added.

## Representative mobile lab test

Baseline: `main` commit `ffded05355987fbcc2dd67268340f266aab14000`.

Method:

- GitHub Actions Ubuntu 24.04 runner;
- Google Chrome 151.0.7922.108;
- Lighthouse 12.8.2 default mobile simulated throttling;
- identical local static Python HTTP servers for baseline and candidate trees;
- three runs per tree;
- median reported below.

Evidence run: GitHub Actions run `32222319137`, artifact `asset-performance-evidence-32222319137` (retained temporarily by Actions).

| Metric | Baseline median | Candidate median | Change |
| --- | ---: | ---: | ---: |
| Lighthouse performance score | 0.72 | 0.91 | +0.19 |
| Largest Contentful Paint | 18,977 ms | 3,378 ms | −15,599 ms (−82.2%) |
| Total transferred bytes | 4,465,458 | 478,434 | −3,987,024 (−89.3%) |
| Cumulative Layout Shift | 0.00494 | 0.00494 | no regression |

Individual runs were intentionally retained in the Actions evidence artifact so the median is not a single lucky sample. These are lab results; after deployment, real-user data should be preferred whenever enough field traffic exists.

## Asset-level changes

Representative generated files from the same build:

| Asset | Source | Optimized web path |
| --- | ---: | ---: |
| Home hero artwork | 2,035,346 B PNG | 13,438 B 500w WebP; 48,794 B full WebP |
| Card-journey artwork | 1,886,548 B PNG | 13,802 B 560w WebP; 50,506 B full WebP |
| Diary egg artwork | 1,785,169 B PNG | 9,638 B 560w WebP; 31,700 B full WebP |
| CBT feature artwork | 1,085,767 B PNG | 10,918 B 560w WebP; 107,932 B full WebP |
| Diary feature artwork | 1,309,819 B PNG | 33,790 B 560w WebP; 96,056 B full WebP |
| Header icon | 256,592 B PNG | 9,810 B WebP |
| Nunito Regular | 132,204 B TTF | 44,180 B WOFF2 |
| Nunito ExtraBold | 132,072 B TTF | 44,884 B WOFF2 |
| Social preview | previous page-specific portrait PNGs | 58,297 B, 1200×630 JPEG |

The optimized variant set tracked by the regression checker totals 595,665 bytes. A browser does not download every variant: `srcset` selects an appropriate image and below-the-fold images remain lazy-loaded.

## Layout and accessibility safeguards

- The home hero remains `fetchpriority="high"` and is not lazy-loaded.
- Below-the-fold home illustrations retain `loading="lazy"` and `decoding="async"`.
- Existing descriptive image alt text is preserved.
- The actual intrinsic size of `egg-card-journey.png` is 992×1586; the old HTML declared 1024×1792. The corrected dimensions avoid reserving the wrong aspect ratio before the image loads.
- `<picture>` wrappers receive explicit layout guards so introducing responsive sources does not change the existing grid geometry.
- The localized-page generator emits the same optimized header icon as checked-in generated pages, preventing the next localization build from silently reverting the optimization.

## Regression gate

`scripts/check_asset_budget.py` is executed by the normal Pages quality workflow. It fails when optimized assets disappear or exceed their byte budgets, when CSS returns to TTF web-font references, when heavy body PNGs lose their WebP `<picture>` source, when the header reverts to the 512px PNG, when Open Graph pages use the old heavy preview, when critical/lazy loading semantics regress, or when the localized-page generator stops matching the published asset policy.

Original high-resolution files remain available in the repository where they serve as source/fallback material. Unreferenced source artwork does not contribute to normal page transfer weight.
