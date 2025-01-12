"""
AudioManager for managing background music and sound effects in the game engine.

This module provides a centralized system for handling audio playback, volume control,
and audio transitions.
"""

import pygame

class AudioManager:
    """
    A singleton class for managing audio in the game.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AudioManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        pygame.mixer.init()
        self.background_music = None
        self.sounds = {}
        self.music_volume = 1.0
        self.sfx_volume = 1.0

    def load_music(self, filepath: str):
        """
        Load a music track for background playback.

        Args:
            filepath (str): Path to the music file.
        """
        self.background_music = filepath

    def play_music(self, loop: bool = True):
        """
        Play the loaded background music.

        Args:
            loop (bool): Whether to loop the music track.
        """
        if self.background_music:
            loops = -1 if loop else 0
            pygame.mixer.music.load(self.background_music)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)

    def stop_music(self):
        """
        Stop the background music.
        """
        pygame.mixer.music.stop()

    def set_music_volume(self, volume: float):
        """
        Set the volume for background music.

        Args:
            volume (float): Volume level (0.0 to 1.0).
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def load_sound(self, name: str, filepath: str):
        """
        Load a sound effect.

        Args:
            name (str): Name of the sound.
            filepath (str): Path to the sound file.
        """
        self.sounds[name] = pygame.mixer.Sound(filepath)
        self.sounds[name].set_volume(self.sfx_volume)

    def play_sound(self, name: str):
        """
        Play a sound effect by name.

        Args:
            name (str): Name of the sound to play.
        """
        if name in self.sounds:
            self.sounds[name].play()

    def set_sfx_volume(self, volume: float):
        """
        Set the volume for all sound effects.

        Args:
            volume (float): Volume level (0.0 to 1.0).
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
