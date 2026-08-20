# Settlers III MapGen v1.7 DEV_3

Petit ajout isolé au-dessus de DEV_2 :

- `update_latest_release.bat` : récupération en un clic de la dernière GitHub Release STABLE ;
- interrogation exclusive de `releases/latest` du dépôt officiel ;
- sélection prioritaire de l'asset `SETTLERS3_MAPGEN_*_STABLE_*.zip` ;
- téléchargement dans `updates/` ;
- aucune extraction, installation ou suppression automatique ;
- l'installation courante n'est jamais écrasée.

Cette base est volontairement conservatrice et pourra évoluer plus tard vers un vrai système d'update (comparaison de version, vérification SHA-256, extraction atomique, conservation des préférences, rollback).
