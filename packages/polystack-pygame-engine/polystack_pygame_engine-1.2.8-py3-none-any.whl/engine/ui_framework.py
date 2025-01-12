"""
UI Framework for creating modular and interactive user interfaces in Pygame.

This framework provides a base class for UI elements (`UIElement`), interactive
components (e.g., `UIButton`), layout management, styling, integration with the
EventBus, and a root canvas to manage all UI elements.

Inspired by Unity's UI system, it includes advanced components like sliders,
checkboxes, and progress bars.
"""

import pygame

from engine.animation_system import Animation
from engine.event_system import EventBus

class Style:
    """
    A class to encapsulate styling options for UI elements.
    """
    def __init__(self, background_color=(50, 50, 50), border_color=(255, 255, 255),
                 border_width=2, font=None, text_color=(255, 255, 255)):
        self.background_color = background_color
        self.border_color = border_color
        self.border_width = border_width
        self.font = font if font else pygame.font.Font(None, 24)
        self.text_color = text_color


class UIElement:
    """
    Base class for all UI elements.
    """
    def __init__(self, x: int, y: int, width: int, height: int, style: Style = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.active = True
        self.style = style if style else Style()

    def render(self, screen: pygame.Surface):
        if self.visible:
            pygame.draw.rect(screen, self.style.background_color, self.rect)
            pygame.draw.rect(screen, self.style.border_color, self.rect, self.style.border_width)

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, delta_time: float):
        pass

class UIImage(UIElement):
    """
    A UI element for rendering images.
    """
    def __init__(self, x: int, y: int, width: int, height: int, image: pygame.Surface):
        super().__init__(x, y, width, height)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = image.get_rect()
        self.rect.center = (x, y)

    def render(self, screen: pygame.Surface):
        if self.visible:
            screen.blit(self.image, self.rect)

class UIText(UIElement):
    """
    A UI element for rendering simple text.
    """
    def __init__(self, x: int, y: int, text: str, style: Style = None):
        width, height = style.font.size(text) if style else (100, 24)
        super().__init__(x, y, width, height, style)
        self.text = text

    def render(self, screen: pygame.Surface):
        if self.visible:
            text_surface = self.style.font.render(self.text, True, self.style.text_color)
            screen.blit(text_surface, self.rect.topleft)

class UIAnimatedElement(UIElement):
    """
    A UI element that supports animations.
    """
    def __init__(self, x: int, y: int, width: int, height: int, animation: Animation):
        super().__init__(x, y, width, height)
        self.animation = animation

    def render(self, screen: pygame.Surface):
        if self.visible:
            frame = self.animation.get_current_frame()
            if frame:
                frame_scaled = pygame.transform.scale(frame, (self.rect.width, self.rect.height))
                screen.blit(frame_scaled, self.rect.topleft)

    def update(self, delta_time: float):
        self.animation.update(delta_time)

class UIButton(UIElement):
    """
    A clickable button UI element.
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str, callback=None, style: Style = None):
        super().__init__(x, y, width, height, style)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.default_color = self.style.background_color
        self.hover_color = (100, 100, 100)  # Default hover color

    def render(self, screen: pygame.Surface):
        if self.visible:
            self.style.background_color = self.hover_color if self.hovered else self.default_color
            super().render(screen)

            # Render text
            text_surface = self.style.font.render(self.text, True, self.style.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event):
        if self.active:
            if event.type == pygame.MOUSEMOTION:
                self.hovered = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
                if self.callback:
                    self.callback()
                EventBus.publish("button_clicked", {
                    "button_text": self.text,
                    "position": self.rect.topleft
                })


class UISlider(UIElement):
    """
    A slider UI element for selecting values within a range.
    """
    def __init__(self, x: int, y: int, width: int, height: int, min_value: float, max_value: float,
                 initial_value: float, callback=None, style: Style = None):
        super().__init__(x, y, width, height, style)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.callback = callback
        self.handle_rect = pygame.Rect(x, y, 10, height)
        self.update_handle_position()

    def update_handle_position(self):
        self.handle_rect.x = self.rect.x + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)

    def render(self, screen: pygame.Surface):
        if self.visible:
            # Render slider background
            pygame.draw.rect(screen, self.style.background_color, self.rect)
            # Render handle
            pygame.draw.rect(screen, self.style.border_color, self.handle_rect)

    def handle_event(self, event: pygame.event.Event):
        if self.active and event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.update_value(event.pos[0])

    def update_value(self, mouse_x: int):
        relative_x = mouse_x - self.rect.x
        self.value = self.min_value + (relative_x / self.rect.width) * (self.max_value - self.min_value)
        self.value = max(self.min_value, min(self.max_value, self.value))
        self.update_handle_position()
        if self.callback:
            self.callback(self.value)


class UICheckbox(UIElement):
    """
    A checkbox UI element for toggling a boolean value.
    """
    def __init__(self, x: int, y: int, size: int, checked: bool = False, callback=None, style: Style = None):
        super().__init__(x, y, size, size, style)
        self.checked = checked
        self.callback = callback

    def render(self, screen: pygame.Surface):
        if self.visible:
            pygame.draw.rect(screen, self.style.background_color, self.rect)
            pygame.draw.rect(screen, self.style.border_color, self.rect, self.style.border_width)
            if self.checked:
                pygame.draw.line(screen, self.style.text_color, self.rect.topleft, self.rect.bottomright, 3)
                pygame.draw.line(screen, self.style.text_color, self.rect.topright, self.rect.bottomleft, 3)

    def handle_event(self, event: pygame.event.Event):
        if self.active and event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.checked = not self.checked
            if self.callback:
                self.callback(self.checked)


class UIProgressBar(UIElement):
    """
    A progress bar UI element for displaying progress.
    """
    def __init__(self, x: int, y: int, width: int, height: int, min_value: float, max_value: float,
                 initial_value: float, style: Style = None):
        super().__init__(x, y, width, height, style)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value

    def render(self, screen: pygame.Surface):
        if self.visible:
            # Render progress bar background
            pygame.draw.rect(screen, self.style.background_color, self.rect)
            # Render progress
            progress_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(screen, self.style.border_color, progress_rect)

    def set_value(self, value: float):
        self.value = max(self.min_value, min(self.max_value, value))


class Canvas:
    """
    The root container for all UI elements.
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.elements = []

    def add_element(self, element: UIElement):
        self.elements.append(element)

    def render(self):
        for element in self.elements:
            element.render(self.screen)

    def update(self, dt: float):
        for element in self.elements:
            element.update(dt)

    def handle_event(self, event: pygame.event.Event):
        for element in self.elements:
            element.handle_event(event)
