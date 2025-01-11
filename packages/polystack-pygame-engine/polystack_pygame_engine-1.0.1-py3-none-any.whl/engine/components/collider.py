"""
Collider component for handling collision detection in GameObjects.

This module defines the Collider component, which provides methods for setting
bounding boxes and detecting collisions between GameObjects.
"""
from engine.game_object import Component
from engine.event_system import EventBus
from engine.prefab_system import register_component


@register_component
class Collider(Component):
    """
    Component for handling collisions in a GameObject.

    The Collider component defines a bounding box and provides methods for detecting
    overlaps with other Colliders.
    """

    def __init__(self, game_object):
        """
        Initialize a new Collider component.

        Args:
            game_object (GameObject): The GameObject to which this component is attached.
        """
        super().__init__(game_object)
        self.bounds = [0, 0, 0, 0]

    def set_bounds(self, x: int, y: int, width: int, height: int):
        """
        Set the bounds of the collider.

        Args:
            x (int): The x-coordinate of the top-left corner of the bounds.
            y (int): The y-coordinate of the top-left corner of the bounds.
            width (int): The width of the bounding box.
            height (int): The height of the bounding box.
        """
        self.bounds = [x, y, width, height]

    def check_collision(self, other_collider):
        """
        Check for a collision with another Collider.

        Args:
            other_collider (Collider): The other Collider to check against.

        Returns:
            bool: True if a collision is detected, False otherwise.
        """
        x1, y1, w1, h1 = self.bounds
        x2, y2, w2, h2 = other_collider.bounds
        collision = not (x1 > x2 + w2 or x1 + w1 < x2 or y1 > y2 + h2 or y1 + h1 < y2)
        if collision:
            # Publish collision event
            EventBus.publish("collision_detected", self.game_object, other_collider.game_object)
        return collision
