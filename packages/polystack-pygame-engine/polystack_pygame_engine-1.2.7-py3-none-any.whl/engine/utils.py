import pygame

def load_sprite_sheet(image: pygame.Surface, frame_width: int, frame_height: int) -> list[pygame.Surface]:
    """
    Extract individual frames from a sprite sheet.

    Args:
        image (pygame.Surface): The sprite sheet image.
        frame_width (int): Width of each frame.
        frame_height (int): Height of each frame.

    Returns:
        list[pygame.Surface]: List of frames extracted from the sprite sheet.
    """
    frames = []
    sheet_width, sheet_height = image.get_size()
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frame = image.subsurface(pygame.Rect(x, y, frame_width, frame_height))
            frames.append(frame)
    return frames
