"""
GameManager for centralizing game initialization, state management, and event handling.

This module provides a structured way to manage the game's lifecycle, including
asset preloading, state transitions, and global event handling.
"""

import pygame

from engine import InputManager, SceneManager
from engine.event_system import EventBus
from engine.asset_manager import AssetManager
from engine.game_settings import GameSettings
from engine.ui_framework import Canvas

class GameManager:
    """
    Central manager for initializing and running the game.
    """
    def __init__(self, title="Game", width=800, height=600, fps=60, fullscreen=False):
        pygame.init()
        self.flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((width, height), self.flags)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = True
        self.state = "Menu"  # Example states: "Menu", "Playing", "Paused"
        self.event_bus = EventBus()
        self.asset_manager = AssetManager()
        self.settings = GameSettings()
        self.canvas = Canvas(self.screen)

    def apply_settings(self):
        """
        Apply current settings (e.g., resolution, fullscreen).
        """
        resolution = self.settings.get("resolution", [800, 600])
        fullscreen = self.settings.get("fullscreen", False)
        self.flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode(resolution, self.flags)

    def toggle_fullscreen(self):
        """
        Toggle fullscreen mode and update settings.
        """
        fullscreen = not self.settings.get("fullscreen", False)
        self.settings.set("fullscreen", fullscreen)
        self.apply_settings()

    def set_state(self, state):
        """
        Change the current game state.

        Args:
            state (str): The state to switch to (e.g., "Menu", "Playing").
        """
        self.state = state

    def handle_events(self):
        """
        Handle global events and propagate them through the event bus.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            InputManager.handle_event(event)
            self.event_bus.publish("global_event", event)
            self.canvas.handle_event(event)
        InputManager.handle_held_keys()

    def update(self, delta_time):
        """
        Update the current game state and active scene.

        Args:
            delta_time (float): Time elapsed since the last frame.
        """
        if self.state == "Menu":
            pass  # Update menu-specific logic
        elif self.state == "Playing":
            SceneManager.update_active_scene(delta_time)

    def render(self):
        """
        Render the current game state.
        """
        self.screen.fill((0, 0, 0))
        if self.state == "Menu":
            self.canvas.render()
        # elif self.state == "Playing":
            # SceneManager.update_active_scene(self.screen)

    def run(self):
        """
        Main game loop.
        """
        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000.0
            self.handle_events()
            self.update(delta_time)
            self.render()
            pygame.display.flip()
        pygame.quit()

# Example Usage
if __name__ == "__main__":
    game_manager = GameManager(title="My Game", width=800, height=600, fps=60, fullscreen=True)
    game_manager.run()
