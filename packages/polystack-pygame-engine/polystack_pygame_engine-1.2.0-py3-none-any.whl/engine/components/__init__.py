"""
Initialization module for the game engine package.

This module allows importing all components for building game objects and scenes.
"""

from .transform import Transform
from .sprite_renderer import SpriteRenderer
from .collider import Collider
from .animator import Animator

__all__ = [
    "Transform",
    "SpriteRenderer",
    "Collider",
    "Animator"
]
