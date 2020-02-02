from typing import Tuple

from pygame.color import Color
from pygame.math import Vector2

from ui import Component, Text


class TextField(Component):
  def __init__(self, font, size: Tuple[int, int], padding: int, max_length, **kwargs):
    super().__init__(size, **kwargs)
    self._contents = ""
    self._text = Text(font, Color(255, 255, 255), self._contents)
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
