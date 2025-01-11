# game_object.py

"""
Module for managing GameObjects and their Components in a game engine.

This module defines the GameObject class, which represents entities in a game,
and the Component class, which allows
extending GameObject functionality through a compositional approach.
"""
from engine.event_system import EventBus


class GameObject:
    """
    Represents an entity in the game world.

    A GameObject can have multiple components attached to it, enabling modular functionality such as rendering,
    physics, or custom behaviors. Each GameObject has a unique name, a collection of components, and an active state.
    """

    def __init__(self, name: str):
        """
        Initialize a new GameObject.

        Args:
            name (str): The name of the GameObject.
        """
        self.name = name
        self.components = {}
        self.active = True

    def add_component(self, component_class):
        """
        Add a new component to the GameObject.

        Args:
            component_class (type): The class of the component to add.

        Returns:
            Component: An instance of the added component.

        Raises:
            ValueError: If a component of the same type already exists on the GameObject.
        """
        if component_class.__name__ in self.components:
            raise ValueError(f"Component {component_class.__name__} already exists on {self.name}")
        component = component_class(self)
        self.components[component_class.__name__] = component
        # Publish event for adding a component
        EventBus.publish("component_added", self, component)
        return component

    def get_component(self, component_class):
        """
        Retrieve a component of the specified type from the GameObject.

        Args:
            component_class (type): The class of the component to retrieve.

        Returns:
            Component or None: The instance of the requested component, or None if not found.
        """
        return self.components.get(component_class.__name__)

    def update(self, delta_time: float):
        """
        Update all active components attached to the GameObject.

        Args:
            delta_time (float): The time elapsed since the last update.
        """
        if not self.active:
            return
        for component in self.components.values():
            if component.active:
                component.update(delta_time)


class Component:
    """
    Base class for components that can be attached to a GameObject.

    Components extend the functionality of GameObjects. Derived classes should implement specific behaviors or
    attributes, such as physics or rendering.
    """

    def __init__(self, game_object: GameObject):
        """
        Initialize a new Component.

        Args:
            game_object (GameObject): The GameObject to which this component is attached.
        """
        self.game_object = game_object
        self.active = True

    def update(self, delta_time: float):
        """
        Update the component.

        Args:
            delta_time (float): The time elapsed since the last update.
        
        This method should be overridden by derived classes to implement specific behavior.
        """
        pass
