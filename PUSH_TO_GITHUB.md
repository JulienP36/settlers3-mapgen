# Push this reconstructed repository to GitHub

This repository contains the reconstructed MapGen history through v1.3.

## From the repository folder

Create an empty GitHub repository first (no README/license/gitignore), then:

```bash
git remote add origin https://github.com/<USER>/<REPOSITORY>.git
git push -u origin main
git push origin --tags
```

SSH alternative:

```bash
git remote add origin git@github.com:<USER>/<REPOSITORY>.git
git push -u origin main
git push origin --tags
```

## From the Git bundle

```bash
git clone SETTLERS3_MAPGEN_HISTORY_v1.3.bundle settlers3-mapgen
cd settlers3-mapgen
git remote add origin https://github.com/<USER>/<REPOSITORY>.git
git push -u origin main
git push origin --tags
```

## Future release routine

```bash
git add -A
git commit -m "feat: ..."
git tag -a vX.Y -m "MapGen vX.Y"
git push origin main
git push origin --tags
```

Generated `output/` maps and `.sav` files are ignored in normal Git. Store major binary checkpoints in GitHub Releases or Git LFS if long-term remote storage is desired.
