from typing import Tuple, Callable, Any, Optional

from pygame.color import Color
from pygame.math import Vector2

from ui import Component, FormattedText
from ui import Style

COLOR_WHITE = Color(255, 255, 255)


class Checkbox(Component):
  def __init__(self, size: Tuple[int, int], screen, label: FormattedText, checked: bool = False, **kwargs):
    super().__init__(size, screen, **kwargs)
    self._callback: Callable[[bool], Any] = kwargs.get('callback')
    self._label = label
    self._style_on_click = kwargs.get('style_onclick')
    self._cooldown = 0
    self._checked = checked
    self._update_text()

  def update(self, elapsed_time: int):
    if self._cooldown > 0:
      self._cooldown = max(self._cooldown - elapsed_time, 0)
      if self._cooldown == 0:
        self._active_style = self._style_hovered if self._is_hovered else self._style

  def set_callback(self, callback: Callable[[bool], Any]):
    self._callback = callback

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    text_pos = Vector2(self._rect.centerx - self._label.size[0] / 2,
                       self._rect.centery - self._label.size[1] / 2)
    self._label.set_pos(text_pos)

  def _render(self):
    self._label.render()

  def _on_click(self, mouse_pos: Optional[Tuple[int, int]]):
    self._checked = not self._checked
    self._update_text()
    if self._callback:
      self._callback(self._checked)
    self._active_style = self._style_on_click
    self._cooldown = 150

  def _update_text(self):
    self._label.format_text("x" if self._checked else "_")


def checkbox(font, screen, size: Tuple[int, int], callback: Callable[[bool], Any], label: str, checked: bool = False):
  return Checkbox(size=size,
                  screen=screen,
                  callback=callback,
                  label=FormattedText(screen, font, COLOR_WHITE, label + "  [%s]", None),
                  checked=checked,
                  style=Style(background=Color(50, 50, 100), border_color=Color(150, 150, 150)),
                  style_hovered=Style(background=Color(80, 80, 120), border_color=Color(180, 180, 180)),
                  style_onclick=Style(background=Color(80, 80, 120), border_color=Color(200, 255, 200),
                                      border_width=2))
