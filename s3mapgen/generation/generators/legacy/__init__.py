"""Moteurs Legacy : cœur natif actif et pipeline procédural de comparaison.

Le cœur natif porte le terrain et le contenu global récupéré de l'exécutable.
Les objets/ressources propres aux départs, les colons et l'écriture SAV restent
explicitement réservés au futur flux SAV.
"""

from .native_pipeline import generate

__all__ = ("generate",)
