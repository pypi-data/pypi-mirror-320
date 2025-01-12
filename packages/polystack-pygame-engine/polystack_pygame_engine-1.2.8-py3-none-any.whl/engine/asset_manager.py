"""
This module contains the AssetManager class, which is responsible for
loading, caching, and retrieving game assets.
"""
import json

import pygame

class AssetManager:
    """
    A singleton class for managing game assets such as images, sounds, and fonts.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AssetManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_assets"):
            self._assets = {}

    def load_image(self, name: str, filepath: str) -> pygame.Surface:
        """
        Load an image asset, or retrieve it from the cache if already loaded.

        Args:
            name (str): The name to reference the image.
            filepath (str): Path to the image file.

        Returns:
            pygame.Surface: The loaded image.
        """
        if name not in self._assets:
            self._assets[name] = pygame.image.load(filepath).convert_alpha()
        return self._assets[name]

    def load_sound(self, name: str, filepath: str) -> pygame.mixer.Sound:
        """
        Load a sound asset, or retrieve it from the cache if already loaded.

        Args:
            name (str): The name to reference the sound.
            filepath (str): Path to the sound file.

        Returns:
            pygame.mixer.Sound: The loaded sound.
        """
        if name not in self._assets:
            self._assets[name] = pygame.mixer.Sound(filepath)
        return self._assets[name]

    def load_font(self, name: str, filepath: str, size: int) -> pygame.font.Font:
        """
        Load a font asset, or retrieve it from the cache if already loaded.

        Args:
            name (str): The name to reference the font.
            filepath (str): Path to the font file.
            size (int): Font size.

        Returns:
            pygame.font.Font: The loaded font.
        """
        font_key = f"{name}_{size}"
        if font_key not in self._assets:
            self._assets[font_key] = pygame.font.Font(filepath, size)
        return self._assets[font_key]

    def get(self, name: str):
        """
        Retrieve an asset by name.

        Args:
            name (str): The name of the asset.

        Returns:
            Any: The requested asset, or None if it doesn't exist.
        """
        return self._assets.get(name)

    def clear(self):
        """
        Clear all loaded assets from memory.
        """
        self._assets.clear()

    def preload_assets(self, preload_config: dict):
        """
        Preload multiple assets based on a configuration.

        Args:
            preload_config (dict): A dictionary defining the assets to preload.
                                   Example:
                                   {
                                       "images": [
                                           {"name": "player", "path": "assets/player.png"},
                                           {"name": "enemy", "path": "assets/enemy.png"}
                                       ],
                                       "sounds": [
                                           {"name": "click", "path": "assets/click.wav"}
                                       ],
                                       "fonts": [
                                           {"name": "main_font", "path": "assets/fonts/arial.ttf", "size": 24}
                                       ]
                                   }
        """
        for asset_type, assets in preload_config.items():
            for i, asset in enumerate(assets):
                print(f"Loading asset {i + 1}/{len(assets)}: {asset['name']}")
                name = asset["name"]
                filepath = asset["path"]

                if asset_type == "images":
                    self.load_image(name, filepath)
                elif asset_type == "sounds":
                    self.load_sound(name, filepath)
                elif asset_type == "fonts":
                    size = asset.get("size", 24)  # Default font size
                    self.load_font(name, filepath, size)

    def preload_assets_from_file(self, filepath: str):
        """
        Preload assets from a JSON file.

        Args:
            filepath (str): Path to the JSON file containing asset preload data.
        """
        with open(filepath, "r", encoding="utf8") as file:
            preload_config = json.load(file)
            self.preload_assets(preload_config)
