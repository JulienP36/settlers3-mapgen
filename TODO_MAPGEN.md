# Settlers III MapGen — TODO programme

## Prochaine grosse étape génération
- [ ] **Upgraded : généraliser la morphologie locale** pour ne plus dépendre du checkpoint 768 comme référence exécutable.
- [ ] Construire une vraie bibliothèque/procédure de formes Upgraded réutilisable avec tous les archétypes.
- [ ] Reprendre ensuite la validation progressive multi-tailles, une map à la fois.

## UX / outillage
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
- [x] Onglet **Paramètres** avec préférences persistantes dans le profil utilisateur.
- [x] Thème sombre / clair, sombre par défaut pour la v1.4 candidate.

### Visualisation / confort
- [x] Slider de transparence pour les vues **Heightmap**, **Ressources** et **Territoires** ; 0 % montre la map globale, 100 % la couche seule.
- [x] À la fin d'un processus, la barre passe en état terminé bleu puis disparaît automatiquement ; état erreur rouge.
- [x] Barre de progression étendue aux générations, imports, exports et sauvegardes d'aperçu.
- [x] Déplacement de la visualisation par drag.
- [x] Zoom molette temporisé/caché pour réduire la latence et sensibilité réglable.
- [x] Projection **parallélogramme** optionnelle pour la visualisation, sans modifier les données réelles de la map.

### Statistiques
- [ ] Enrichir fortement les statistiques, potentiellement sur plusieurs pages : quantités de ressources, pourcentages, comptes exacts des objets-ressources, objets décoratifs, terrains, territoires, etc.
- [ ] Ajouter plus tard des graphiques pour les statistiques qui gagnent à être visualisées.
- [ ] Édition directe de la map — gros morceau, **pas maintenant**.

## À préserver
- [ ] Archetype = macro-forme uniquement.
- [ ] Mode = contenu/règles/balance/objets/ressources/etc.
- [ ] Starts générés très tôt et protégés par les passes suivantes.
- [ ] Legacy / Upgraded / Custom restent séparés.
- [ ] Aucun aperçu imaginaire : rendu déterministe depuis les vraies données.
