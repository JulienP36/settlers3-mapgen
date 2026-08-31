"""Moteur Legacy procédural.

Le moteur actuel implémente l'archétype Continental. Le catalogue et les
identités d'archétypes vivent dans ``generation.archetypes`` ; ils ne sont
pas dupliqués sous chaque moteur.
"""

from .pipeline import generate

__all__ = ("generate",)
