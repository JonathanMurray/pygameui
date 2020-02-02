from typing import Tuple, Optional

import pygame
from pygame.color import Color
from pygame.math import Vector2
from pygame.rect import Rect


class BackgroundGrid:
  def __init__(self, screen_resolution, line_color: Color, cell_width):
    self._screen_resolution = screen_resolution
    self._line_color = line_color
    self._cell_width = cell_width

  def render(self, surface):
    for x in range(0, self._screen_resolution[0], self._cell_width):
      pygame.draw.line(surface, self._line_color, (x, 0), (x, self._screen_resolution[1]))
    for y in range(0, self._screen_resolution[1], self._cell_width):
      pygame.draw.line(surface, self._line_color, (0, y), (self._screen_resolution[0], y))


class Style:
  def __init__(self, background: Optional[Color] = None, border_color: Optional[Color] = None, border_width: int = 1):
    self.background = background
    self.border_color = border_color
    self.border_width = border_width


class Component:
  def __init__(self, size: Tuple[int, int], **kwargs):
    self.size = size
    self._rect = None
    self._style = kwargs.get('style')
    self._style_hovered = kwargs.get('style_hovered')
    self._is_hovered = False
    self._active_style = self._style
    self._is_visible = True

  def update(self, elapsed_time: int):
    pass

  def set_pos(self, pos: Vector2):
    self._rect = Rect(pos, self.size)

  def handle_key_was_pressed(self, key):
    pass

  def handle_mouse_was_clicked(self, mouse_pos: Tuple[int, int]):
    self._assert_initialized()
    if self._is_visible and self._rect.collidepoint(mouse_pos[0], mouse_pos[1]):
      self._on_click(mouse_pos)

  def handle_mouse_was_released(self):
    pass

  def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
    self._assert_initialized()
    hover = self._rect.collidepoint(mouse_pos[0], mouse_pos[1])
    if self._is_hovered and not hover:
      self._active_style = self._style
      self._on_blur()
    elif not self._is_hovered and hover:
      if self._style_hovered:
        self._active_style = self._style_hovered
      self._on_hover(mouse_pos)
    self._is_hovered = hover

  def render(self, surface):
    self._assert_initialized()
    if self._is_visible:
      if self._active_style and self._active_style.background:
        pygame.draw.rect(surface, self._active_style.background, self._rect)
      self._render_contents(surface)
      if self._active_style and self._active_style.border_color:
        pygame.draw.rect(surface, self._active_style.border_color, self._rect, self._active_style.border_width)

  def set_visible(self, visible: bool):
    self._is_visible = visible

  def is_visible(self) -> bool:
    return self._is_visible

  def _render_contents(self, surface):
    pass

  def _on_click(self, mouse_pos: Optional[Tuple[int, int]]):
    pass

  # TODO Remove if not needed
  def _on_hover(self, mouse_pos: Tuple[int, int]):
    pass

  # TODO Remove if not needed
  def _on_blur(self):
    pass

  def _assert_initialized(self):
    if self._rect is None:
      raise Exception("You must set the position of this component before interacting with it!")
