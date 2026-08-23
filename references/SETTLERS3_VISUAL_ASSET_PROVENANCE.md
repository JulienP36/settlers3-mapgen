# Settlers III MapGen — registre de provenance des éléments visuels

> Registre vivant initialisé avec v1.8 DEV_4_R1. Le compléter avant toute nouvelle intégration d'un asset externe.

| Élément | Chemin / génération | Provenance | Usage | Statut / précaution |
|---|---|---|---|---|
| Palette joueurs J1–J20 | `references/SETTLERS3_PLAYER_COLORS_20_REFERENCE_20260820.png` | Capture fournie par le propriétaire du projet, interface de The Settlers III | Calibration visuelle de `PLAYER_COLORS` | Référence uniquement ; ne pas prétendre à une licence ou propriété non établie. |
| Marqueurs de départ J1–J20 | `references/SETTLERS3_PLAYER_START_MARKERS_J1_J20_REFERENCE_20260822.png` | Capture fournie et explicitement validée par le propriétaire du projet, affichage observé dans l'éditeur officiel | DEV_4_R1 : extraction déterministe runtime des 20 sprites ; fond herbe retiré par chroma exact | Conserver l'original ; toute modernisation manuelle est reportée à la future refonte Pixel Art. |
| Couleurs ressources éditeur | `references/SETTLERS3_EDITOR_RESOURCE_COLORS_REFERENCE_20260820.png` | Capture fournie par le propriétaire du projet, éditeur officiel | Calibration des couleurs de la Vue Ressources | Référence uniquement. |
| Preuve seed/diversité v1.10 | `references/SETTLERS3_V1_10_SEED_DIVERSITY_EVIDENCE_20260822.png` | Capture réelle de MapGen fournie par le propriétaire | Preuve documentaire pour l'audit v1.10 | Données réelles de cartes générées ; ne pas utiliser comme illustration générique. |
| Icônes Vue/Heatmap, cadenas, croix, LED et drapeaux | Dessinées par Pillow dans `s3mapgen/gui_v16.py` | Dessin déterministe propre au projet, sans fichier externe | Interface Tk | Remplaçables lors d'une future passe Pixel Art. |
| Miniatures et previews de cartes | `s3mapgen/preview.py` depuis `MapState` réel | Rendu déterministe des données EDM/MAP/SAV ou d'une génération réelle | Viewer, Batch, export PNG | Aucune image imaginaire ; ne jamais substituer une illustration générée. |

Les droits attachés aux éléments provenant du jeu ne doivent jamais être extrapolés. Tout nouvel asset externe à redistribuer doit avoir une provenance documentée et une autorisation explicite conforme à `PROJECT_WORKFLOW.md`.
