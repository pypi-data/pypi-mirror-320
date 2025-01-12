"""
SpriteRenderer component for rendering sprites in a GameObject.

This module defines the SpriteRenderer component, which manages a visual
representation (image) for a GameObject and renders it on the screen.
"""
import pygame

from engine.components.transform import Transform
from engine.game_object import Component
from engine.prefab_system import register_component


@register_component
class SpriteRenderer(Component):
    """
    Component for rendering a sprite in a GameObject.

    The SpriteRenderer component manages an image and renders it at the position
    specified by the associated Transform component of the GameObject.
    """

    def __init__(self, game_object):
        """
        Initialize a new SpriteRenderer component.

        Args:
            game_object (GameObject): The GameObject to which this component is attached.
        """
        super().__init__(game_object)
        self.image = None

    def set_image(self, image):
        """
        Set the image to be rendered.

        Args:
            image: The image to be rendered (must be a Pygame surface).
        """
        self.image = image

    def render(self, screen):
        """
        Render the image on the screen at the GameObject's position.

        Args:
            screen: The Pygame surface where the image will be drawn.

        Raises:
            AttributeError: If the GameObject does not have a Transform component.
        """
        if self.image:
            position = self.game_object.get_component(Transform).position
            screen.blit(self.image, position)

    # def to_dict(self):
    #     """
    #     Serialize the SpriteRenderer to a dictionary.
    #
    #     Returns:
    #         dict: A dictionary representation of the SpriteRenderer component.
    #     """
    #     return {
    #         "image_color": self.image.get_at((0, 0)) if self.image else None,
    #         "image_size": self.image.get_size() if self.image else None
    #     }

    def to_dict(self):
        """
        Serialize the SpriteRenderer to a dictionary.

        Returns:
            dict: A dictionary representation of the SpriteRenderer component.
        """
        return {
            "image_color": tuple(self.image.get_at((0, 0))) if self.image else None,
            "image_size": self.image.get_size() if self.image else None,
        }

    def from_dict(self, data):
        """
        Deserialize the SpriteRenderer from a dictionary.

        Args:
            data (dict): Serialized data.
        """
        if data.get("image_color") and data.get("image_size"):
            self.image = pygame.Surface(data["image_size"])
            self.image.fill(tuple(data["image_color"]))
