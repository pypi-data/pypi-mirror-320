"""
Event system for enabling publish-subscribe communication.

This module provides a flexible EventBus class for decoupled communication between
systems, GameObjects, or components within the game engine.
"""

from typing import Callable, Dict, List, Any

class EventBus:
    """
    A global event bus for managing publish-subscribe communication.
    """
    _listeners: Dict[str, List[Callable[..., None]]] = {}

    @staticmethod
    def subscribe(event_name: str, callback: Callable[..., None]) -> None:
        """
        Subscribe a callback to a specific event.

        Args:
            event_name (str): The name of the event to subscribe to.
            callback (Callable[..., None]): The function to call when the event is published.
        """
        if event_name not in EventBus._listeners:
            EventBus._listeners[event_name] = []
        EventBus._listeners[event_name].append(callback)

    @staticmethod
    def unsubscribe(event_name: str, callback: Callable[..., None]) -> None:
        """
        Unsubscribe a callback from a specific event.

        Args:
            event_name (str): The name of the event to unsubscribe from.
            callback (Callable[..., None]): The function to remove from the event's subscribers.
        """
        if event_name in EventBus._listeners:
            if callback in EventBus._listeners[event_name]:
                EventBus._listeners[event_name].remove(callback)
            if not EventBus._listeners[event_name]:
                del EventBus._listeners[event_name]

    @staticmethod
    def publish(event_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Publish an event to all subscribed callbacks.

        Args:
            event_name (str): The name of the event to publish.
            *args: Positional arguments to pass to the callbacks.
            **kwargs: Keyword arguments to pass to the callbacks.
        """
        if event_name in EventBus._listeners:
            for callback in EventBus._listeners[event_name]:
                callback(*args, **kwargs)

# Example Usage
# ------------
# def on_player_died(score):
#     print(f"Player died! Final score: {score}")

# EventBus.subscribe("player_died", on_player_died)
# EventBus.publish("player_died", score=100)
