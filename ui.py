from typing import Tuple, Optional, Any

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.rect import Rect


class BackgroundGrid:
  def __init__(self, screen, screen_resolution, line_color: Color, cell_width):
    self._screen = screen
    self._screen_resolution = screen_resolution
    self._line_color = line_color
    self._cell_width = cell_width

  def render(self):
    for x in range(0, self._screen_resolution[0], self._cell_width):
      pygame.draw.line(self._screen, self._line_color, (x, 0), (x, self._screen_resolution[1]))
    for y in range(0, self._screen_resolution[1], self._cell_width):
      pygame.draw.line(self._screen, self._line_color, (0, y), (self._screen_resolution[0], y))


class Style:
  def __init__(self, background: Optional[Color] = None, border_color: Optional[Color] = None, border_width: int = 1):
    self.background = background
    self.border_color = border_color
    self.border_width = border_width


class Component:
  def __init__(self, size: Tuple[int, int], screen, **kwargs):
    self.size = size
    self._screen = screen
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

  def handle_button_click(self, key):
    pass

  def handle_mouse_click(self, mouse_pos: Tuple[int, int]):
    self._assert_initialized()
    if self._rect.collidepoint(mouse_pos[0], mouse_pos[1]):
      self._on_click(mouse_pos)

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

  def render(self):
    self._assert_initialized()
    if self._is_visible:
      if self._active_style and self._active_style.background:
        pygame.draw.rect(self._screen, self._active_style.background, self._rect)
      self._render()
      if self._active_style and self._active_style.border_color:
        pygame.draw.rect(self._screen, self._active_style.border_color, self._rect, self._active_style.border_width)

  def set_visible(self, visible: bool):
    self._is_visible = visible

  def is_visible(self) -> bool:
    return self._is_visible

  def _render(self):
    pass

  def _on_click(self, mouse_pos: Optional[Tuple[int, int]]):
    pass

  def _on_hover(self, mouse_pos: Tuple[int, int]):
    pass

  def _on_blur(self):
    pass

  def _assert_initialized(self):
    if self._rect is None:
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
    self._screen.blit(self._rendered_text, self._rect)


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
    self._screen.blit(self._rendered_text, self._rect)


class Counter(Component):
  def __init__(self, size: Tuple[int, int], screen, formatted_text: FormattedText, **kwargs):
    super().__init__(size, screen, **kwargs)
    self._text = formatted_text
    self._count = 0
    self._update_text()

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    self._update_text_pos()

  def _render(self):
    self._text.render()

  def increment(self):
    self._count += 1
    self._update_text()
    self._update_text_pos()

  def decrement(self):
    self._count -= 1
    self._update_text()
    self._update_text_pos()

  def _update_text(self):
    self._text.format_text(self._count)

  def _update_text_pos(self):
    text_pos = Vector2(self._rect.centerx - self._text.size[0] / 2,
                       self._rect.centery - self._text.size[1] / 2)
    self._text.set_pos(text_pos)
