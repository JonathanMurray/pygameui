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
  original_image = pygame.image.load(file_path)
  original_image.convert()
  scaled_image = pygame.transform.scale(original_image, size)
  return Surface(scaled_image, style=Style(border_color=Color(255, 255, 255)))
