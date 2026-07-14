# CBT Cards migration inventory

| Old MetalHatsCats URL | New URL | Mechanism | Status |
| --- | --- | --- | --- |
| `/products/cbt-cards` | `https://cbt-cards.github.io/` | Next.js permanent redirect | implemented |
| `/products/cbt-cards/privacy` | `https://cbt-cards.github.io/privacy/` | Next.js permanent redirect | implemented |
| `/products/cbt-cards/terms` | `https://cbt-cards.github.io/terms/` | Next.js permanent redirect | implemented |
| `/cbt` | `https://cbt-cards.github.io/how-it-works/` | Next.js permanent redirect | implemented |
| `/cbt/cards` | `https://cbt-cards.github.io/features/` | Next.js permanent redirect | implemented |
| `/cbt/metaphors` | `https://cbt-cards.github.io/features/` | Next.js permanent redirect | implemented |
| `/cbt/protocols` and protocol pages | `https://cbt-cards.github.io/how-it-works/` | Next.js permanent redirect | implemented |
| `/news/cbt-cards-app` | `https://cbt-cards.github.io/` | Next.js permanent redirect | implemented |

## Assets

`public/assets/` contains copied product-owned artwork from the CBT Cards Flutter app and prior MHC product listing: application icon, onboarding screen, and mascot artwork. No stock imagery was introduced.

## Publishing

The repository is an organization Pages repository: `CBT-cards/cbt-cards.github.io`. Once GitHub Pages is set to **GitHub Actions** in its Pages settings, the workflow in `.github/workflows/deploy-pages.yml` deploys pushes to `main` to `https://cbt-cards.github.io/`.

No CNAME is included because the requested primary domain is the default GitHub Pages domain.
