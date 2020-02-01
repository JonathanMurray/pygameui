from typing import Tuple, Optional, Any

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.rect import Rect


class BackgroundGrid:
  def __init__(self, screen, screen_resolution, line_color: Color, cell_width):
    self.screen = screen
    self.screen_resolution = screen_resolution
    self.line_color = line_color
    self.cell_width = cell_width

  def render(self):
    for x in range(0, self.screen_resolution[0], self.cell_width):
      pygame.draw.line(self.screen, self.line_color, (x, 0), (x, self.screen_resolution[1]))
    for y in range(0, self.screen_resolution[1], self.cell_width):
      pygame.draw.line(self.screen, self.line_color, (0, y), (self.screen_resolution[0], y))


class Style:
  def __init__(self, background: Optional[Color] = None, border_color: Optional[Color] = None, border_width: int = 1):
    self.background = background
    self.border_color = border_color
    self.border_width = border_width


class Component:
  def __init__(self, size: Tuple[int, int], screen, **kwargs):
    self.size = size
    self.screen = screen
    self.rect = None
    self.style = kwargs.get('style')
    self.style_hovered = kwargs.get('style_hovered')
    self.is_hovered = False
    self.active_style = self.style

  def update(self, elapsed_time: int):
    pass

  def set_pos(self, pos: Vector2):
    self.rect = Rect(pos, self.size)

  def handle_mouse_click(self, mouse_pos: Tuple[int, int]):
    self._assert_initialized()
    if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
      self._on_click(mouse_pos)

  def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
    self._assert_initialized()
    hover = self.rect.collidepoint(mouse_pos[0], mouse_pos[1])
    if self.is_hovered and not hover:
      self.active_style = self.style
      self._on_blur()
    elif not self.is_hovered and hover:
      if self.style_hovered:
        self.active_style = self.style_hovered
      self._on_hover(mouse_pos)
    self.is_hovered = hover

  def render(self):
    self._assert_initialized()
    if self.active_style and self.active_style.background:
      pygame.draw.rect(self.screen, self.active_style.background, self.rect)
    self._render()
    if self.active_style and self.active_style.border_color:
      pygame.draw.rect(self.screen, self.active_style.border_color, self.rect, self.active_style.border_width)

  def _render(self):
    pass

  def _on_click(self, mouse_pos: Tuple[int, int]):
    pass

  def _on_hover(self, mouse_pos: Tuple[int, int]):
    pass

  def _on_blur(self):
    pass

  def _assert_initialized(self):
    if self.rect is None:
      raise Exception("You must set the position of this component before interacting with it!")


class Text(Component):
  def __init__(self, screen, font: Font, color: Color, text: str, **kwargs):
    super().__init__(font.size(text), screen, **kwargs)
    self._font = font
    self._color = color
    self._rendered_text = self._font.render(text, True, color)

  def set_text(self, text: str):
    self.size = self._font.size(text)
    self._rendered_text = self._font.render(text, True, self._color)

  def _render(self):
    self.screen.blit(self._rendered_text, self.rect)


class FormattedText(Component):
  def __init__(self, screen, font: Font, color: Color, format_string: str, format_variable: Any, **kwargs):
    text = format_string % format_variable
    text_size = font.size(text)
    super().__init__(text_size, screen, **kwargs)
    self._format_string = format_string
    self._font = font
    self._color = color
    self._rendered_text = self._font.render(text, True, color)

  def format_text(self, variable: Any):
    text = self._format_string % variable
    self.size = self._font.size(text)
    self._rendered_text = self._font.render(text, True, self._color)

  def _render(self):
    self.screen.blit(self._rendered_text, self.rect)
