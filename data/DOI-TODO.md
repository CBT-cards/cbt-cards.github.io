# External DOI activation

Repository preparation is complete enough to define the remaining owner-authorized archive step.

- [ ] Choose the first canonical dataset release version.
- [ ] Review `data/dataset-publication.json` release boundary.
- [ ] Freeze exact public release files.
- [ ] Compute and record SHA-256 checksums for the frozen distributions.
- [ ] Review `data/dataset.jsonld`, methodology/provenance, license and `CITATION.cff`.
- [ ] Publish the frozen release in Zenodo (or another appropriate persistent archive) using the dataset owner's authorized account.
- [ ] Verify the archive record and DOI resolution.
- [ ] Write the exact issued DOI back to `data/dataset.jsonld`, `data/dataset-publication.json` and `CITATION.cff`.
- [ ] Preserve this release identity when future live corpus data changes.

Do not add a placeholder DOI before issuance.
