# Settlers III MapGen v1.8 DEV_8_R4

Version Windows validée et finale de la passe **Raccourcis v2**, correctif ciblé de R3.

## Principaux changements à vérifier

1. Recapturer une touche seule : aucun `Alt` ne doit apparaître.
2. Capturer `Ctrl+…`, `Shift+…`, `Ctrl+Shift+…`, puis un véritable `Alt+…`.
3. Vérifier que les acquis visuels et fonctionnels validés en R3 sont strictement inchangés.

## Choix techniques

- Le JSON existant reste l’unique fichier de préférences ; son schéma passe à la version 2.
- La migration est indépendante pour chaque commande : une entrée malformée ne détruit pas les autres réglages.
- Une chaîne vide représente volontairement un raccourci désactivé.
- La fenêtre Aide est une vraie `Toplevel` réutilisable, pas un second système de traduction ni une boucle de surveillance.
- Les barres de titre sémantiques validées restent événementielles et inchangées.

## Validation interne

- 207 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés ;
- aucune modification intentionnelle du moteur de génération ni des formats binaires.

## Validation Windows

- touches simples capturées sans ajout de `Alt` ;
- vrais modificateurs Ctrl, Shift et Alt reconnus ;
- conflits, changements en attente, défilement compact, persistance et Aide dynamique validés ;
- DEV_8 clôturée sur R4.
