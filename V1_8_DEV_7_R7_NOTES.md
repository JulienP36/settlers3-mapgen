# v1.8 DEV_7_R7 — Modalité capacité et retour maîtrisé des loupes

## Périmètre

- avertissement de réduction de capacité remplacé par un véritable dialogue modal : le sélecteur situé derrière est désactivé, la capture d’entrée est exclusive et une seule confirmation peut exister ;
- dialogue disponible en FR/EN/DE/ES et relié au système de thèmes clair/sombre ;
- retour des loupes sur les miniatures Batch et Historique sous forme de calque RGBA sans carré opaque ;
- trois états visuels : translucide au repos, réveillé au survol, activé lorsque le grand aperçu correspondant est affiché ;
- un seul propriétaire visuel global : aucune combinaison de survol, aperçu épinglé ou changement de sélection ne peut laisser plusieurs loupes réveillées/activées ;
- clic et survol de 700 ms conservés ; drag, zoom, remplacement sans clignotement et position préservée restent inchangés ;
- la prévision Batch R6 reste générique et tient déjà compte des futurs verrous manuels via la liste commune des protections.

## Garanties

- la loupe est dessinée de manière déterministe par Pillow sur le rendu réel de la miniature ; aucune image fictive ou asset externe ;
- aucun fond rectangulaire n’est ajouté autour de l’icône ;
- moteur de génération v1.5, formats binaires et données déterministes inchangés ;
- aucune publication sur `dev` avant validation Windows.

## Validation interne

- 185 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés.

## Checklist Windows

1. Déclencher la réduction de capacité puis tenter molette/clic derrière le dialogue : aucune interaction extérieure et aucune seconde confirmation ne doivent être possibles.
2. Vérifier le dialogue dans les thèmes clair/sombre et les quatre langues.
3. Vérifier une loupe translucide centrée, grande et sans carré opaque sur chaque miniature disponible.
4. Survoler successivement plusieurs miniatures Batch : seule celle sous le pointeur doit être réveillée.
5. Attendre 700 ms : la loupe devient active et le grand aperçu apparaît.
6. Épingler un aperçu puis survoler une autre miniature : la nouvelle loupe se réveille seule ; en quittant, l’état actif revient à la miniature épinglée.
7. Cliquer une autre miniature : remplacement à position constante et une seule loupe active.
8. Recliquer la miniature source : fermeture de l’aperçu et retour à l’état inactif.
9. Refaire les transitions dans le Centre d’historique, notamment après un changement de sélection.

