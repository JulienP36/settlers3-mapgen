# Settlers III MapGen — registre de provenance des éléments visuels

> Registre vivant initialisé avec v1.8 DEV_4_R1. Le compléter avant toute nouvelle intégration d'un asset externe.

| Élément | Chemin / génération | Provenance | Usage | Statut / précaution |
|---|---|---|---|---|
| Palette joueurs J1–J20 | `references/SETTLERS3_PLAYER_COLORS_20_REFERENCE_20260820.png` | Capture fournie par le propriétaire du projet, interface de The Settlers III | Calibration visuelle de `PLAYER_COLORS` | Référence uniquement ; ne pas prétendre à une licence ou propriété non établie. |
| Marqueurs de départ J1–J20 | `references/SETTLERS3_PLAYER_START_MARKERS_J1_J20_REFERENCE_20260822.png` | Capture fournie et explicitement validée par le propriétaire du projet, affichage observé dans l'éditeur officiel | DEV_4_R1 : extraction déterministe runtime des 20 sprites ; fond herbe retiré par chroma exact | Conserver l'original ; toute modernisation manuelle est reportée à la future refonte Pixel Art. |
| Couleurs ressources éditeur | `references/SETTLERS3_EDITOR_RESOURCE_COLORS_REFERENCE_20260820.png` | Capture fournie par le propriétaire du projet, éditeur officiel | Calibration des couleurs de la Vue Ressources | Référence uniquement. |
| Preuve seed/diversité v1.10 | `references/SETTLERS3_V1_10_SEED_DIVERSITY_EVIDENCE_20260822.png` | Capture réelle de MapGen fournie par le propriétaire | Preuve documentaire pour l'audit v1.10 | Données réelles de cartes générées ; ne pas utiliser comme illustration générique. |
| Icônes Vue/Heatmap, cadenas, croix, LED et drapeaux | Dessinées par Pillow dans `s3mapgen/application/ui/widgets/icons.py` | Dessin déterministe propre au projet, sans fichier externe | Interface Tk | Remplaçables lors d'une future passe Pixel Art. |
| Miniatures et previews de cartes | `s3mapgen/application/rendering/preview.py` depuis `MapState` réel | Rendu déterministe des données EDM/MAP/SAV ou d'une génération réelle | Viewer, Batch, export PNG | Aucune image imaginaire ; ne jamais substituer une illustration générée. |
| Capture Génération / Viewer v1.8 | `docs/screenshots/v1_8_generation_viewer.png` | Capture Windows réelle de DEV_11_R2 fournie par le propriétaire, carte générée seed `2026081901` | README FR/EN | Interface anglaise, thème sombre ; aucun chemin personnel visible. |
| Capture Statistiques v1.8 | `docs/screenshots/v1_8_statistics.png` | Capture Windows réelle de DEV_11_R2 fournie par le propriétaire, données de carte générée | README FR/EN | Carte thermique et rapport Statistics ; aucun fichier externe ou contenu inventé. |
| Capture Graphiques v1.8 | `docs/screenshots/v1_8_charts.png` | Capture Windows réelle de DEV_11_R2 fournie par le propriétaire, données de carte générée | README FR/EN | Vue Resources et graphique Mining stock déterministes. |
| Capture Batch v1.8 | `docs/screenshots/v1_8_batch.png` | Capture Windows réelle de DEV_11_R2 fournie par le propriétaire, quatre tâches Batch | README FR/EN | Miniatures déterministes ; une configuration identique montre volontairement l’état `Reused from cache`. |

Les droits attachés aux éléments provenant du jeu ne doivent jamais être extrapolés. Tout nouvel asset externe à redistribuer doit avoir une provenance documentée et une autorisation explicite conforme à `PROJECT_WORKFLOW.md`.
