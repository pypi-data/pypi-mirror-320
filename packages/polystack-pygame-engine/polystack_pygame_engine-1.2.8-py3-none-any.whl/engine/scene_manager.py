"""
SceneManager for managing active scenes in the game engine.

This module provides functionality for switching between scenes, updating the
current active scene, and managing persistent GameObjects.
"""
from typing import Optional, List

from engine.event_system import EventBus
from engine.game_object import GameObject
from engine.scene import Scene


class SceneManager:
    """
    Manages scenes and transitions between them.

    This class handles the active scene in the game, providing methods to switch
    scenes, update the current scene, and manage persistent GameObjects that
    remain across scene transitions.
    """

    _active_scene: Optional[Scene] = None
    _persistent_objects: List[GameObject] = []
    _all_scenes: List[Scene] = []  # Global registry of all scenes

    @staticmethod
    def register_scene(scene: Scene) -> None:
        """
        Register a new scene with the SceneManager.

        Args:
            scene (Scene): The scene to register.
        """
        if scene not in SceneManager._all_scenes:
            SceneManager._all_scenes.append(scene)

    @staticmethod
    def load_scene(scene: Scene) -> None:
        """
        Set the given scene as the active scene, preserving persistent objects.

        Args:
            scene (Scene): The scene to load as the active scene.
        """
        if SceneManager._active_scene:
            SceneManager._move_persistent_objects(scene)
        SceneManager._active_scene = scene
        SceneManager.register_scene(scene)

    @staticmethod
    def get_active_scene() -> Optional[Scene]:
        """
        Get the currently active scene.

        Returns:
            Optional[Scene]: The currently active scene, or None if no scene is active.
        """
        return SceneManager._active_scene

    @staticmethod
    def update_active_scene(delta_time: float) -> None:
        """
        Update the active scene.

        Args:
            delta_time (float): The time elapsed since the last update.
        """
        if SceneManager._active_scene:
            SceneManager._active_scene.update(delta_time)

    @staticmethod
    def add_persistent_object(game_object: GameObject) -> None:
        """
        Add a GameObject to the list of persistent objects.

        Args:
            game_object (GameObject): The GameObject to persist across scenes.
        """
        if game_object not in SceneManager._persistent_objects:
            SceneManager._persistent_objects.append(game_object)

    @staticmethod
    def remove_persistent_object(game_object: GameObject) -> None:
        """
        Remove a GameObject from the persistent list and all scenes except the active one.

        Args:
            game_object (GameObject): The GameObject to remove.
        """
        if game_object in SceneManager._persistent_objects:
            SceneManager._persistent_objects.remove(game_object)

        # Remove from all non-active scenes
        for scene in SceneManager._all_scenes:
            if scene != SceneManager._active_scene and game_object in scene.game_objects:
                scene.game_objects.remove(game_object)

    @staticmethod
    def _move_persistent_objects(new_scene: Scene) -> None:
        """
        Move all persistent objects to the new scene.

        Args:
            new_scene (Scene): The scene to which persistent objects are moved.
        """
        for game_object in SceneManager._persistent_objects:
            if game_object not in new_scene.game_objects:
                new_scene.add_game_object(game_object)

    @staticmethod
    def reset_scene() -> None:
        """
        Reset the current active scene by clearing its GameObjects
        and reloading any persistent objects.
        """
        if SceneManager._active_scene:
            # Clear the scene's GameObjects, except for persistent objects
            SceneManager._active_scene.game_objects = []
            SceneManager._move_persistent_objects(SceneManager._active_scene)

    @staticmethod
    def transition_to_scene(new_scene: Scene, transition_effect=None) -> None:
        """
        Transition to a new scene, optionally using a transition effect.

        Args:
            new_scene (Scene): The scene to transition to.
            transition_effect (Callable, optional): A function to execute during the transition.
        """
        if transition_effect:
            transition_effect()
        SceneManager.load_scene(new_scene)
