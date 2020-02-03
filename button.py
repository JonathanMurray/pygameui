from enum import Enum
from typing import List, Tuple, Callable, Any, Optional

from pygame.color import Color
from pygame.math import Vector2

from text import StaticText
from ui import Component
from ui import Style

COLOR_WHITE = Color(255, 255, 255)


class ButtonEvent(Enum):
  FIRE = 1
  RELEASE = 2


class ButtonBehavior:
  def on_click(self) -> Optional[ButtonEvent]:
    return None

  def update(self, elapsed_time: int) -> Optional[ButtonEvent]:
    return None

  def on_release(self) -> Optional[ButtonEvent]:
    return None


class HoldDownBehavior(ButtonBehavior):
  def __init__(self, initial_delay: int, repeat_interval: int):
    self._initial_delay = initial_delay
    self._repeat_interval = repeat_interval
    self._is_held_down = False
    self._fire_timer = 0

  def on_click(self) -> Optional[ButtonEvent]:
    self._is_held_down = True
    self._fire_timer = self._initial_delay
    return ButtonEvent.FIRE

  def update(self, elapsed_time: int) -> Optional[ButtonEvent]:
    should_fire = False
    if self._is_held_down:
      self._fire_timer -= elapsed_time
      while self._fire_timer <= 0:
        self._fire_timer += self._repeat_interval
        should_fire = True
    if should_fire:
      return ButtonEvent.FIRE

  def on_release(self) -> Optional[ButtonEvent]:
    self._is_held_down = False
    return ButtonEvent.RELEASE


class SingleClickBehavior(ButtonBehavior):
  def __init__(self):
    self._cooldown = 0

  def on_click(self) -> Optional[ButtonEvent]:
    self._cooldown = 150
    return ButtonEvent.FIRE

  def update(self, elapsed_time: int) -> Optional[ButtonEvent]:
    if self._cooldown > 0:
      self._cooldown = max(self._cooldown - elapsed_time, 0)
      if self._cooldown == 0:
        return ButtonEvent.RELEASE


class Button(Component):
  def __init__(self, size: Tuple[int, int], label: StaticText, behavior: ButtonBehavior,
      hotkey: Optional[int] = None, **kwargs):
    super().__init__(size, **kwargs)
    self._callback: Callable[[], Any] = kwargs.get('callback')
    self._label = label
    self._style_on_click: Style = kwargs.get('style_onclick')
    self._hotkey = hotkey
    self._behavior = behavior

  def update(self, elapsed_time: int):
    self._handle_event(self._behavior.update(elapsed_time))

  def set_callback(self, callback: Callable[[], Any]):
    self._callback = callback

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    self._update_text_pos()

  def _update_text_pos(self):
    text_pos = Vector2(self._rect.centerx - self._label.size[0] / 2,
                       self._rect.centery - self._label.size[1] / 2)
    self._label.set_pos(text_pos)

  def set_label(self, label: str):
    self._label.set_text(label)
    self._update_text_pos()

  def set_label_color(self, color: Color):
    self._label.set_color(color)

  def _render_contents(self, surface):
    self._label.render(surface)

  def _on_click(self, mouse_pos: Optional[Tuple[int, int]]):
    self._handle_event(self._behavior.on_click())

  def handle_mouse_was_released(self):
    self._handle_event(self._behavior.on_release())

  def handle_key_was_pressed(self, key):
    if self.is_visible() and self._hotkey == key:
      self._handle_event(self._behavior.on_click())

  def handle_key_was_released(self, key):
    if self._hotkey == key:
      self._handle_event(self._behavior.on_release())

  def _handle_event(self, event: Optional[ButtonEvent]):
    if event == ButtonEvent.FIRE:
      self._active_style = self._style_on_click
      if self._callback:
        self._callback()
    elif event == ButtonEvent.RELEASE:
      self._active_style = self._style_hovered if self._is_hovered else self._style


class ColorToggler(Button):
  def __init__(self, size: Tuple[int, int], label: StaticText, colors: List[Color], **kwargs):
    super().__init__(size, label, **kwargs)
    self._colors = colors
    self._index = 0
    self._background = self._colors[self._index]

  def _on_click(self, mouse_pos: Optional[Tuple[int, int]]):
    self._index = (self._index + 1) % len(self._colors)
    self._background = self._colors[self._index]


def button(font, size: Tuple[int, int], callback: Callable[[], Any], label: str, hotkey: Optional[int] = None,
    hold: Optional[HoldDownBehavior] = None):
  return Button(size=size,
                callback=callback,
                label=StaticText(font, COLOR_WHITE, label),
                behavior=hold if hold else SingleClickBehavior(),
                hotkey=hotkey,
                style=Style(background_color=Color(50, 50, 100), border_color=Color(150, 150, 150)),
                style_hovered=Style(background_color=Color(80, 80, 120), border_color=Color(180, 180, 180)),
                style_onclick=Style(background_color=Color(80, 80, 120), border_color=Color(200, 255, 200),
                                    border_width=2))


def icon(font, size: Tuple[int, int], background_surface, label: str, hotkey: Optional[int] = None):
  return Button(size=size,
                callback=lambda: print("icon clicked!"),
                label=StaticText(font, COLOR_WHITE, label),
                behavior=SingleClickBehavior(),
                hotkey=hotkey,
                style=Style(background_surface=background_surface, border_color=Color(150, 150, 150)),
                style_hovered=Style(background_surface=background_surface, border_color=Color(180, 180, 180)),
                style_onclick=Style(background_surface=background_surface, border_color=Color(200, 255, 200),
                                    border_width=2))
