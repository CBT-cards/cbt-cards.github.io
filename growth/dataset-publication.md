# Dataset publication status

CBT Cards has a genuine public data corpus and treats dataset publication as a separate reproducibility/citation concern from the live website.

Current state: **DOI not issued**.

Canonical preparation artifacts:

- `data/dataset.jsonld` — Schema.org Dataset metadata and selected distributions.
- `data/dataset-publication.json` — release boundary, DOI lifecycle and integrity requirements.
- `CITATION.cff` — repository citation metadata.
- `research/` and editorial-review surfaces — methodology/review context.

Before archival publication, select a dataset release version, review the intended release boundary, freeze exact public distributions and compute SHA-256 checksums. Then publish that frozen release through Zenodo or another appropriate persistent archive using owner-authorized access.

Only after the archive issues and resolves a DOI should that DOI be added to `data/dataset.jsonld`, `data/dataset-publication.json`, `CITATION.cff` and the human citation surface.

The DOI is for stable citation and reproducibility. It is not a Search ranking signal, clinical endorsement, quality certificate or guarantee of AI citation.
