from typing import Tuple, Any

from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2

from ui import Component


class StaticText(Component):
  def __init__(self, font: Font, color: Color, text: str, **kwargs):
    super().__init__(font.size(text), **kwargs)
    self._font = font
    self._color = color
    self._rendered_text = self._font.render(text, True, color)

  def set_text(self, text: str):
    self.size = self._font.size(text)
    self._rendered_text = self._font.render(text, True, self._color)

  def _render_contents(self, surface):
    surface.blit(self._rendered_text, self._rect)


class FormattedText(Component):
  def __init__(self, font: Font, color: Color, format_string: str, format_variable: Any, **kwargs):
    text = format_string % format_variable
    text_size = font.size(text)
    super().__init__(text_size, **kwargs)
    self._format_string = format_string
    self._font = font
    self._color = color
    self._rendered_text = self._font.render(text, True, color)

  def format_text(self, variable: Any):
    text = self._format_string % variable
    self.size = self._font.size(text)
    self._rendered_text = self._font.render(text, True, self._color)

  def _render_contents(self, surface):
    surface.blit(self._rendered_text, self._rect)


class EditableText(Component):
  def __init__(self, font, size: Tuple[int, int], padding: int, max_length, **kwargs):
    super().__init__(size, **kwargs)
    self._contents = ""
    self._text = StaticText(font, Color(255, 255, 255), self._contents)
    self._padding = padding
    self._max_length = max_length

  def _render_contents(self, surface):
    self._text.render(surface)

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    text_pos = pos + Vector2(self._padding, self._padding)
    self._text.set_pos(text_pos)

  def append(self, text: str):
    self._contents += text
    self._contents = self._contents[0:self._max_length]
    self._text.set_text(self._contents)

  def backspace(self):
    self._contents = self._contents[0:-1]
    self._text.set_text(self._contents)
