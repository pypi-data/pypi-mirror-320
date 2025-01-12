"""
This module contains the Animation and Animator classes for managing animations in a game.
"""

import pygame

class Animation:
    """
    Represents a single animation with its frames and playback settings.
    """
    def __init__(self, name: str, frames: list[pygame.Surface], frame_rate: int, loop: bool = True):
        self.name = name
        self.frames = frames
        self.frame_rate = frame_rate
        self.loop = loop
        self.current_frame = 0
        self.elapsed_time = 0

    def update(self, delta_time: float):
        """
        Update the animation frame based on elapsed time.

        Args:
            delta_time (float): Time since the last update.
        """
        self.elapsed_time += delta_time
        if self.elapsed_time >= 1 / self.frame_rate:
            self.elapsed_time = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.current_frame = 0 if self.loop else len(self.frames) - 1

    def get_current_frame(self):
        """
        Get the current frame to render.

        Returns:
            pygame.Surface: The current frame surface.
        """
        return self.frames[self.current_frame]

class StateMachine:
    """
    A simple state machine to manage animation states and transitions.
    """
    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, state_name: str, transitions: dict):
        """
        Add a new state to the machine.

        Args:
            state_name (str): Name of the state.
            transitions (dict): Transition rules (e.g., {"run": lambda: player_is_running}).
        """
        self.states[state_name] = transitions

    def set_state(self, state_name: str):
        """
        Set the current state.

        Args:
            state_name (str): The state to switch to.
        """
        if state_name in self.states:
            self.current_state = state_name

    def update(self):
        """
        Update the state machine, checking transitions.

        Returns:
            str: The new state name if a transition occurs, otherwise None.
        """
        if not self.current_state:
            return None

        for target_state, condition in self.states[self.current_state].items():
            if condition():  # Execute the condition function
                #print("Checking transition to:", target_state, "Condition:", condition(), "Current state:", self.current_state)
                self.set_state(target_state)
                return target_state

        return None
