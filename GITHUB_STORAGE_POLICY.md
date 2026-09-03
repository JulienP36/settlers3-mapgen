# GitHub storage policy

Tracked in normal GitHub Git:
- source code and tests;
- configs and generation profiles;
- compact engine data required at runtime (`data/*.npz`, scaffold/reference EDM/MAP files) while each file remains comfortably below GitHub's 100 MB hard file limit.

Ignored by default:
- `output/` generated maps/previews/reports;
- `.sav` runtime saves;
- the complete `references/` research/recovery tree. It is deliberately not
  pushed to GitHub while the audit material is being reorganized;
- release ZIPs and temporary files.

The source-package builder explicitly adds the local `references/` tree back to
each hand-off ZIP. Consequently, the ZIP retains the full recovery context even
though the normal GitHub push does not.

For long-term binary checkpoint storage, prefer Git LFS or GitHub Releases rather than committing every generated EDM/MAP/SAV into normal Git history.
