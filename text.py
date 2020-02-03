from typing import Tuple, Any, Optional

from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2

from ui import Component


class StaticText(Component):
  def __init__(self, font: Font, color: Color, text: str, **kwargs):
    super().__init__(font.size(text), **kwargs)
    self._font = font
    self._color = color
    self._text = text
    self._rendered_text = None
    self._update_text()

  def _update_text(self):
    self._rendered_text = self._font.render(self._text, True, self._color)

  def set_text(self, text: str):
    self.set_size(self._font.size(text))
    self._text = text
    self._update_text()

  def _render_contents(self, surface):
    surface.blit(self._rendered_text, self._rect)

  def set_color(self, color: Color):
    self._color = color
    self._update_text()


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
  def __init__(self, font, size: Tuple[int, int], padding: int, max_length: int, **kwargs):
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


class BlinkingCursor:
  def __init__(self, blink_interval: int):
    self._visible = False
    self._cooldown = 0
    self._blink_interval = blink_interval

  def update(self, elapsed_time: int):
    self._cooldown -= elapsed_time
    if self._cooldown < 0:
      self._cooldown += self._blink_interval
      self._visible = not self._visible
      return True

  def is_visible(self):
    return self._visible


class TextArea(Component):
  def __init__(self, font, color: Color, size: Tuple[int, int], padding: int,
      blinking_cursor: Optional[BlinkingCursor] = None, **kwargs):
    super().__init__(size, **kwargs)
    self._text = ""
    self._padding = padding
    self._font = font
    self._color = color
    self._blinking_cursor = blinking_cursor
    self._line_surfaces = []
    self._update_text()

  def update(self, elapsed_time: int):
    if self._blinking_cursor and self._blinking_cursor.update(elapsed_time):
      self._update_text()

  def _update_text(self):
    self._line_surfaces = []
    start_line = 0
    final_line = ""
    for i in range(len(self._text)):
      if self._text[i] == '\n':
        line = self._text[start_line:i]
        self._line_surfaces.append(self._render_line(line))
        start_line = i + 1
      window = self._text[start_line:i + 1]
      rendered_width = self._font.size(window)[0]
      if rendered_width > self.size[0] - self._padding * 2:
        truncated_line = self._text[start_line:i]
        self._line_surfaces.append(self._render_line(truncated_line))
        start_line = i
      if i == len(self._text) - 1:
        final_line = self._text[start_line:i + 1]
    if self._blinking_cursor and self._blinking_cursor.is_visible():
      line_trailer = "_"
    else:
      line_trailer = ""
    self._line_surfaces.append(self._render_line(final_line + line_trailer))

  def _render_line(self, line: str):
    return self._font.render(line, True, self._color)

  def _render_contents(self, surface):
    (x, y) = self._rect.topleft + Vector2(self._padding, self._padding)
    for line_surface in self._line_surfaces:
      surface.blit(line_surface, (x, y))
      y += line_surface.get_size()[1]

  def append(self, text: str):
    self._text += text
    self._update_text()

  def backspace(self):
    self._text = self._text[:-1]
    self._update_text()
