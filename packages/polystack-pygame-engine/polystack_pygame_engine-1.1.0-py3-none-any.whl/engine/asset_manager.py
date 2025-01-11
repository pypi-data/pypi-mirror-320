"""
This module contains the AssetManager class, which is responsible for
loading, caching, and retrieving game assets.
"""

import os
from typing import Dict, Any

import pygame


class AssetManager:
    """
    A class to manage loading, caching, and retrieving game assets.
    """

    _asset_cache: Dict[str, Any] = {}

    @staticmethod
    def load_image(name: str, path: str) -> pygame.Surface:
        """
        Load an image from the given path. Cache it for future use.

        :param path: Path to the image file.
        :param name: Name to cache the image under.
        :return: Loaded pygame.Surface.
        """
        if name in AssetManager._asset_cache:
            return AssetManager._asset_cache[name]

        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")

        image = pygame.image.load(path).convert_alpha()
        AssetManager._asset_cache[name] = image
        return image

    @staticmethod
    def load_sound(name: str, path: str) -> pygame.mixer.Sound:
        """
        Load a sound from the given path. Cache it for future use.

        :param path: Path to the sound file.
        :param name: Name to cache the sound under.
        :return: Loaded pygame.mixer.Sound.
        """
        if name in AssetManager._asset_cache:
            return AssetManager._asset_cache[name]

        if not os.path.exists(path):
            raise FileNotFoundError(f"Sound not found: {path}")

        sound = pygame.mixer.Sound(path)
        AssetManager._asset_cache[name] = sound
        return sound

    @staticmethod
    def load_font(name: str, path: str, size: int) -> pygame.font.Font:
        """
        Load a font from the given path. Cache it for future use.

        :param path: Path to the font file.
        :param size: Size of the font to load.

        :return: Loaded pygame.font.Font.
        """
        key = f"{name}:{size}"
        if key in AssetManager._asset_cache:
            return AssetManager._asset_cache[key]

        if not os.path.exists(path):
            raise FileNotFoundError(f"Font not found: {path}")

        font = pygame.font.Font(path, size)
        AssetManager._asset_cache[key] = font
        return font

    @staticmethod
    def get_asset(name: str) -> Any:
        """
        Retrieve an asset from the cache by its name.

        :param name: Name of the asset to retrieve.
        :return: Cached asset or None if not found.
        """
        return AssetManager._asset_cache.get(name)

    @staticmethod
    def preload_assets(assets: Dict[str, Dict[str, Any]]):
        """
        Preload a set of assets into the cache.

        :param assets: Dictionary where keys are asset names and values are dictionaries with 'type' and 'path'.
        """
        for name, asset_info in assets.items():
            try:
                asset_type = asset_info.get('type')
                path = asset_info.get('path')

                if asset_type == 'image':
                    AssetManager.load_image(name, path)
                elif asset_type == 'sound':
                    AssetManager.load_sound(name, path)
                elif asset_type == 'font':
                    size = asset_info.get('size', 16)  # Default font size if not specified
                    AssetManager.load_font(name, path, size)
            except Exception as e:
                print(f"Failed to preload {asset_type} named {name} at {path}: {e}")

    @staticmethod
    def clear_cache():
        """
        Clear all cached assets.
        """
        AssetManager._asset_cache.clear()
