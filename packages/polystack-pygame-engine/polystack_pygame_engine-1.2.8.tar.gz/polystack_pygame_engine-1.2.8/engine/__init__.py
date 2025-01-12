"""
Initialization module for the game engine package.

This module allows importing all core functionalities of the engine, such as GameObject,
Scene, SceneManager, ScriptableObject, and built-in components.
"""

from .game_object import GameObject, Component
from .scene import Scene
from .scene_manager import SceneManager
from .scriptable_object import ScriptableObject
from .event_system import EventBus
from .input_manager import InputManager
from .prefab_system import PrefabSystem
from .asset_manager import AssetManager
from .animation_system import Animation, StateMachine
from .ui_framework import UIButton, Style, Canvas

__all__ = [
    "GameObject",
    "Component",
    "Scene",
    "SceneManager",
    "ScriptableObject",
    "EventBus",
    "InputManager",
    "PrefabSystem",
    "AssetManager",
    "Animation",
    "StateMachine",
    "UIButton",
    "Style",
    "Canvas"
]
