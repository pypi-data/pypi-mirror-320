"""
Transform component for managing position, rotation, and scale of GameObjects.

This module defines the Transform component, which provides basic spatial properties
and methods for manipulating the position of GameObjects.
"""
from engine.game_object import Component
from engine.prefab_system import register_component


@register_component
class Transform(Component):
    """
    Component for managing spatial properties of a GameObject.

    The Transform component handles the position, rotation, and scale of the associated
    GameObject, enabling movement and spatial transformations.
    """

    def __init__(self, game_object):
        """
        Initialize a new Transform component.

        Args:
            game_object (GameObject): The GameObject to which this component is attached.
        """
        super().__init__(game_object)
        self.position = [0, 0]
        self.rotation = 0
        self.scale = [1, 1]

    def move(self, x: float, y: float):
        """
        Move the GameObject by the specified amounts.

        Args:
            x (float): The amount to move along the x-axis.
            y (float): The amount to move along the y-axis.
        """
        self.position[0] += x
        self.position[1] += y

    def to_dict(self):
        """
        Serialize the Transform component to a dictionary.
        """
        return {
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
        }