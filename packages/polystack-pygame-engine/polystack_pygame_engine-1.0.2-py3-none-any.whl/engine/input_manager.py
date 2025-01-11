"""
InputManager for centralizing input handling in the game engine.

This module provides an InputManager class for mapping key presses to actions,
supporting customizable key bindings and multiple input devices.
"""

from typing import Dict, List, Callable, Literal
import pygame

class InputManager:
    """
    Centralized input manager for handling key mappings and actions.
    """
    _action_bindings: Dict[str, List[Dict]] = {}  # Maps actions to key bindings with states
    _action_callbacks: Dict[str, List[Callable[[], None]]] = {}  # Maps actions to callbacks

    @staticmethod
    def bind_action(action: str, key: int, state: Literal["down", "up", "hold"] = "down") -> None:
        """
        Bind a key and state to a specific action.

        Args:
            action (str): The action name.
            key (int): The Pygame key code to bind to the action.
            state (str): The key state to trigger the action ("down", "up", "hold").
        """
        if action not in InputManager._action_bindings:
            InputManager._action_bindings[action] = []
        if not any(binding for binding in InputManager._action_bindings[action] if binding["key"] == key and binding["state"] == state):
            InputManager._action_bindings[action].append({"key": key, "state": state})

    @staticmethod
    def unbind_action(action: str, key: int, state: Literal["down", "up", "hold"] = "down") -> None:
        """
        Unbind a key and state from a specific action.

        Args:
            action (str): The action name.
            key (int): The Pygame key code to unbind from the action.
            state (str): The key state to unbind ("down", "up", "hold").
        """
        if action in InputManager._action_bindings:
            InputManager._action_bindings[action] = [
                binding for binding in InputManager._action_bindings[action]
                if not (binding["key"] == key and binding["state"] == state)
            ]

    @staticmethod
    def register_callback(action: str, callback: Callable[[], None]) -> None:
        """
        Register a callback for a specific action.

        Args:
            action (str): The action name.
            callback (Callable[[], None]): The function to call when the action is triggered.
        """
        if action not in InputManager._action_callbacks:
            InputManager._action_callbacks[action] = []
        InputManager._action_callbacks[action].append(callback)

    @staticmethod
    def handle_event(event: pygame.event.Event) -> None:
        """
        Handle a Pygame event and trigger actions if applicable.

        Args:
            event (pygame.event.Event): The Pygame event to handle.
        """
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            state = "down" if event.type == pygame.KEYDOWN else "up"
            for action, bindings in InputManager._action_bindings.items():
                for binding in bindings:
                    if binding["key"] == event.key and binding["state"] == state:
                        for callback in InputManager._action_callbacks.get(action, []):
                            callback()

    @staticmethod
    def handle_held_keys() -> None:
        """
        Handle actions bound to "hold" state (keys that are being held down).
        """
        keys = pygame.key.get_pressed()
        for action, bindings in InputManager._action_bindings.items():
            for binding in bindings:
                if binding["state"] == "hold" and keys[binding["key"]]:
                    for callback in InputManager._action_callbacks.get(action, []):
                        callback()

# Example Usage
# -------------
# def move_left():
#     print("Moving left!")

# def move_right():
#     print("Moving right!")

# InputManager.bind_action("move_left", pygame.K_LEFT, "hold")
# InputManager.bind_action("move_right", pygame.K_RIGHT, "down")

# InputManager.register_callback("move_left", move_left)
# InputManager.register_callback("move_right", move_right)

# In the game loop:
# for event in pygame.event.get():
#     InputManager.handle_event(event)
# InputManager.handle_held_keys()