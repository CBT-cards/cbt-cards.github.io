# CBT Cards website

The official, static product website for CBT Cards. It is intentionally dependency-free: the root and seven public pages are plain, accessible HTML and CSS so the site can deploy directly to GitHub Pages.

## Local preview

```bash
python3 -m http.server 4173
```

Open `http://localhost:4173/`. There is no build step.

## Deployment

The website is published by `.github/workflows/deploy-pages.yml` after a push to `main`. In GitHub repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**. The required repository name is `CBT-cards/cbt-cards.github.io`; it serves `https://cbt-cards.github.io/` without a base-path prefix.

## Content and assets

- Update page copy in `index.html` or the relevant page directory.
- Product-owned visual assets are in `public/assets/`.
- Keep all internal links root-relative so the Pages user-site URL works correctly.
- Store URLs are maintained in visible store links on each relevant page.
- Confirm app privacy behavior against the Flutter source before changing `privacy/index.html`.

See [MIGRATION.md](MIGRATION.md) for legacy URL mapping and asset notes.

## License

The original CBT Cards website content is licensed under [CC BY-NC-SA 4.0](LICENSE): attribution and the same license are required for sharing or adaptations, and commercial use is not permitted without prior written permission from MetalHatsCats. CBT Cards names and logos are not licensed for reuse.
