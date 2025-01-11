"""
This module contains the GameSettings class, which is responsible
for loading and saving the game settings.
"""

import json


class GameSettings:
    """
    A class for loading and saving game settings to a JSON file
    """
    DEFAULT_SETTINGS = {
        "resolution": [800, 600],
        "volume": 1.0,
        "controls": {
            "move_up": "W",
            "move_down": "S",
            "move_left": "A",
            "move_right": "D",
        },
    }

    def __init__(self, filepath="settings.json"):
        self.filepath = filepath
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()

    def load_settings(self):
        """
        Load the game settings from the JSON file.
        """
        try:
            with open(self.filepath, "r") as file:
                self.settings.update(json.load(file))
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_settings()  # Create default settings file if it doesn't exist

    def save_settings(self):
        """
        Save the game settings to the JSON file.
        """
        with open(self.filepath, "w", encoding="utf8") as file:
            json.dump(self.settings, file, indent=4)

    def get(self, key, default=None):
        """
        Get a setting value by key.
        :param key:  The key of the setting.
        :param default:  The default value if the key is not found.
        :return:  The value of the setting.
        """
        return self.settings.get(key, default)

    def set(self, key, value):
        """
        Set a setting value by key.
        :param key:  The key of the setting.
        :param value:  The value to set.
        :return:  None
        """
        self.settings[key] = value
        self.save_settings()