"""
This module contains the Animator component class.
"""

from engine import Component
from engine.animation_system import Animation, StateMachine


class Animator(Component):
    """
    Component for managing animations with a state machine.
    """
    def __init__(self, game_object):
        super().__init__(game_object)
        self.animations = {}
        self.state_machine = StateMachine()
        self.current_animation = None

    def add_animation(self, animation: Animation, state_name: str, transitions: dict):
        """
        Add an animation with an associated state and transitions.

        Args:
            animation (Animation): The animation to add.
            state_name (str): The state name.
            transitions (dict): Transition rules for this state.
        """
        self.animations[state_name] = animation
        self.state_machine.add_state(state_name, transitions)

    def play(self, state_name: str):
        """
        Switch to a specific animation state.

        Args:
            state_name (str): The state to play.
        """
        #print("Playing animation:", state_name)
        if state_name in self.animations:
            self.current_animation = self.animations[state_name]
            self.current_animation.current_frame = 0
            self.current_animation.elapsed_time = 0
            self.state_machine.set_state(state_name)

    def update(self, delta_time: float):
        """
        Update the current animation and handle transitions.

        Args:
            delta_time (float): Time since the last update.
        """
        # Check for state transitions
        new_state = self.state_machine.update()
        # print("Current state:", self.state_machine.current_state, "New state:", new_state)
        if new_state: # and new_state == self.state_machine.current_state
            #print("Transitioning to state:", new_state)
            self.play(new_state)

        # Update the current animation
        if self.current_animation:
            self.current_animation.update(delta_time)

    def get_current_frame(self):
        """
        Get the current animation frame to render.

        Returns:
            pygame.Surface: The current frame surface.
        """
        if self.current_animation:
            return self.current_animation.get_current_frame()
        return None
