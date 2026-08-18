# Settlers III MapGen — TODO programme

## Prochaine grosse étape génération
- [ ] **Upgraded : généraliser la morphologie locale** pour ne plus dépendre du checkpoint 768 comme référence exécutable.
- [ ] Construire une vraie bibliothèque/procédure de formes Upgraded réutilisable avec tous les archétypes.
- [ ] Reprendre ensuite la validation progressive multi-tailles, une map à la fois.

## UX / outillage — v1.3
- [x] Barre de progression de génération (progression par étapes du pipeline).
- [x] Bouton seed aléatoire.
- [x] Import `.edm` / `.map` / `.sav` en lecture.
- [x] Export EDM + MAP pour les tailles disposant d'un scaffold validé (768 actuellement).
- [~] Export SAV : **writer SAV non validé** ; copie inchangée autorisée uniquement pour un SAV importé.
- [x] Visualisations : global / heightmap / ressources / territoires.
- [x] Vue territoires depuis `claim`, particulièrement utile sur SAV.
- [x] Zoom sur la visualisation (slider + molette).
- [x] Toutes les tailles natives visibles : 384/448/512/576/640/704/768.
- [x] Nombre max joueurs adapté : 8/11/15/19/20/20/20.
- [~] Génération multi-tailles : sélecteur prêt, mais seule 768 est calibrée dans le moteur actuel.
- [x] Onglet Statistiques basique.
- [x] Scrollbars dans Validations / Pipeline / Métadonnées / Statistiques.
- [ ] Édition directe de la map — gros morceau, **pas maintenant**.

## À préserver
- [ ] Archetype = macro-forme uniquement.
- [ ] Mode = contenu/règles/balance/objets/ressources/etc.
- [ ] Starts générés très tôt et protégés par les passes suivantes.
- [ ] Legacy / Upgraded / Custom restent séparés.
- [ ] Aucun aperçu imaginaire : rendu déterministe depuis les vraies données.
