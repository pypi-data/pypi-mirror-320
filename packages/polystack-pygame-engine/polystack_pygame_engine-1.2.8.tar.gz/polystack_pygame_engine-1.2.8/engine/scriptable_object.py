"""
ScriptableObject base class for reusable and shareable game data.

This module provides a base class for creating scriptable objects that store data
independently of GameObjects, enabling easy reuse and sharing across the game.
"""

import json

from engine.event_system import EventBus


class ScriptableObject:
    """
    Base class for creating scriptable objects.

    Scriptable objects store data that can be reused across the game. These objects
    are not tied to any specific GameObject or scene, making them ideal for items,
    configurations, and global settings.
    """

    def __init__(self, name: str):
        """
        Initialize a new ScriptableObject.

        Args:
            name (str): The name of the ScriptableObject.
        """
        self.name = name

    def save_to_file(self, file_path: str) -> None:
        """
        Save the ScriptableObject data to a JSON file.

        Args:
            file_path (str): The path to the file where the data will be saved.
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.__dict__, file, ensure_ascii=False, indent=4)
        EventBus.publish("scriptable_object_saved", self, file_path)

    @classmethod
    def load_from_file(cls, file_path: str):
        """
        Load ScriptableObject data from a JSON file.

        Args:
            file_path (str): The path to the file to load data from.

        Returns:
            ScriptableObject: An instance of the ScriptableObject with loaded data.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        instance = cls(data['name'])
        instance.__dict__.update(data)
        EventBus.publish("scriptable_object_loaded", instance, file_path)
        return instance

# Example usage:
# Create a scriptable object
# item = ScriptableObject("HealthPotion")
# item.effect = "Restore Health"
# item.value = 50

# Save to file
# item.save_to_file("health_potion.json")

# Load from file
# loaded_item = ScriptableObject.load_from_file("health_potion.json")
