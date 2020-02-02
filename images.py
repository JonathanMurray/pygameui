from typing import Tuple

import pygame
from pygame.color import Color

from ui import Component, Style


class Surface(Component):
  def __init__(self, surface, **kwargs):
    super().__init__(surface.get_size(), **kwargs)
    self._surface = surface

  def _render_contents(self, surface):
    surface.blit(self._surface, self._rect)


def image_surface(file_path: str, size: Tuple[int, int]) -> Surface:
  image = load_and_scale_image(file_path, size)
  return Surface(image, style=Style(border_color=Color(255, 255, 255)))


def load_and_scale_image(file_path: str, size: Tuple[int, int]):
  original_image = pygame.image.load(file_path)
  original_image.convert()
  return pygame.transform.scale(original_image, size)
