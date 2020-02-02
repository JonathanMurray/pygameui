from typing import Tuple

from pygame.math import Vector2

from text import FormattedText
from ui import Component


class Counter(Component):
  def __init__(self, size: Tuple[int, int], formatted_text: FormattedText, **kwargs):
    super().__init__(size, **kwargs)
    self._text = formatted_text
    self._count = 0
    self._update_text()

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    self._update_text_pos()

  def _render_contents(self, surface):
    self._text.render(surface)

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
