"""
Prefab system for instantiating reusable GameObject templates.

This module provides functionality for creating, saving, and instantiating
prefabs to simplify GameObject creation and reuse.
"""
import copy
import json
from typing import Dict, Any
from engine.game_object import GameObject

# Add a global registry for components
COMPONENT_REGISTRY = {}

def register_component(cls):
    """
    Register a component class for use in the prefab system.

    Args:
        cls (type): The class to register.
    """
    COMPONENT_REGISTRY[cls.__name__] = cls
    return cls


class PrefabSystem:
    """
    Manages the creation and instantiation of prefabs.
    """

    @staticmethod
    def save_prefab(name: str, file_path: str, game_object: GameObject) -> None:
        """
        Save a prefab to a JSON file.

        Args:
            name (str): The name of the prefab.
            file_path (str): The file path to save the prefab.
            game_object (GameObject): The GameObject to save as a prefab.
        """
        prefab_data = {
            "name": game_object.name,
            "components": {
                comp.__class__.__name__: comp.to_dict() if hasattr(comp, "to_dict") else vars(comp)
                for comp in game_object.components.values()
            }
        }
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(prefab_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def instantiate_prefab(file_path: str) -> GameObject:
        """
        Instantiate a GameObject from a prefab file.

        Args:
            file_path (str): The path to the prefab file.

        Returns:
            GameObject: A new GameObject based on the prefab.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            prefab_data = json.load(file)

        # Create the GameObject
        game_object = GameObject(prefab_data["name"])
        for comp_name, comp_data in prefab_data["components"].items():
            # Lookup component class in the registry
            component_class = COMPONENT_REGISTRY.get(comp_name)
            if component_class:
                component = game_object.add_component(component_class)
                if hasattr(component, "from_dict"):
                    component.from_dict(comp_data)
                else:
                    component.__dict__.update(comp_data)

        return game_object

# Example Usage
# -------------
# player = GameObject("Player")
# transform = player.add_component(Transform)
# transform.position = [100, 100]

# PrefabSystem.create_prefab("PlayerPrefab", player)
# PrefabSystem.save_prefab("PlayerPrefab", "player_prefab.json")

# PrefabSystem.load_prefab("player_prefab.json")
# new_player = PrefabSystem.instantiate_prefab("PlayerPrefab")
