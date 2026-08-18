# GitHub storage policy

Tracked in normal Git:
- source code and tests;
- configs and generation profiles;
- canonical Markdown/JSON references and snapshots;
- compact engine data required at runtime (`data/*.npz`, scaffold/reference EDM/MAP files) while each file remains comfortably below GitHub's 100 MB hard file limit.

Ignored by default:
- `output/` generated maps/previews/reports;
- `.sav` runtime saves;
- release ZIPs and temporary files.

For long-term binary checkpoint storage, prefer Git LFS or GitHub Releases rather than committing every generated EDM/MAP/SAV into normal Git history.
