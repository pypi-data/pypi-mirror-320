"""
Scene module for managing game objects within a scene.
"""

from typing import List, Optional

import pygame

from engine.ui_framework import Canvas
from engine.game_object import GameObject


class Scene:
    """Represents a scene containing multiple game objects."""

    def __init__(self, name: str, screen: pygame.Surface):
        """Initialize a new Scene.

        Args:
            name (str): The name of the scene.
        """
        self.name: str = name
        self.game_objects: List[GameObject] = []
        self.canvas: Canvas = Canvas(screen)

    def add_game_object(self, game_object: GameObject) -> None:
        """Add a game object to the scene.

        Args:
            game_object (GameObject): The game object to add.

        Raises:
            ValueError: If the game object is already in the scene.
        """
        if game_object in self.game_objects:
            raise ValueError(f"GameObject '{game_object.name}' is already in the scene.")
        self.game_objects.append(game_object)

    def remove_game_object(self, game_object: GameObject) -> None:
        """Remove a game object from the scene.

        Args:
            game_object (GameObject): The game object to remove.

        Raises:
            ValueError: If the game object is not in the scene.
        """
        if game_object not in self.game_objects:
            raise ValueError(f"GameObject '{game_object.name}' is not in the scene.")
        self.game_objects.remove(game_object)

    def update(self, delta_time: float) -> None:
        """Update all active game objects in the scene.

        Args:
            delta_time (float): Time elapsed since the last update.
        """
        for game_object in self.game_objects:
            if game_object.active:
                game_object.update(delta_time)
        self.canvas.render()
        self.canvas.update(delta_time)

    def find_game_object(self, name: str) -> Optional[GameObject]:
        """Find a game object by name.

        Args:
            name (str): The name of the game object to find.

        Returns:
            Optional[GameObject]: The game object if found, otherwise None.
        """
        for game_object in self.game_objects:
            if game_object.name == name:
                return game_object
        return None
