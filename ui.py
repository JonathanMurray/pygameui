from typing import List, Tuple, Callable, Any, Optional

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
  def __init__(self, background: Optional[Color] = None, border: Optional[Color] = None):
    self.background = background
    self.border = border


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
    if self.active_style and self.active_style.border:
      pygame.draw.rect(self.screen, self.active_style.border, self.rect, 1)

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
    self.font = font
    self.rendered_text = self.font.render(text, True, color)

  def _render(self):
    self.screen.blit(self.rendered_text, self.rect)


class Button(Component):
  def __init__(self, size: Tuple[int, int], screen, text: Text, **kwargs):
    super().__init__(size, screen, **kwargs)
    self.callback = kwargs.get('callback')
    self.text = text
    self.style_on_click = kwargs.get('style_onclick')
    self._cooldown = 0

  def update(self, elapsed_time: int):
    if self._cooldown > 0:
      self._cooldown = max(self._cooldown - elapsed_time, 0)
      if self._cooldown == 0:
        self.active_style = self.style_hovered if self.is_hovered else self.style

  def set_callback(self, callback: Callable[[], Any]):
    self.callback = callback

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    text_pos = Vector2(pos.x + self.size[0] / 2 - self.text.size[0] / 2,
                       pos.y + self.size[1] / 2 - self.text.size[1] / 2)
    self.text.set_pos(text_pos)

  def _render(self):
    self.text.render()

  def _on_click(self, mouse_pos: Tuple[int, int]):
    if self.callback:
      self.callback()
    self.active_style = self.style_on_click
    self._cooldown = 150


class ColorToggler(Button):
  def __init__(self, size: Tuple[int, int], screen, text: Text, colors: List[Color], **kwargs):
    super().__init__(size, screen, text, **kwargs)
    self.colors = colors
    self.index = 0
    self.background = self.colors[self.index]

  def _on_click(self, mouse_pos: Tuple[int, int]):
    self.index = (self.index + 1) % len(self.colors)
    self.background = self.colors[self.index]


class AbstractContainer(Component):
  def __init__(self, size: Tuple[int, int], screen, components: List[Component], **kwargs):
    super().__init__(size, screen, **kwargs)
    self.components = components

  def _render(self):
    for component in self.components:
      component.render()

  def _on_click(self, mouse_pos: Tuple[int, int]):
    for component in self.components:
      component.handle_mouse_click(mouse_pos)

  def update(self, elapsed_time: int):
    for component in self.components:
      component.update(elapsed_time)

  def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
    super().handle_mouse_motion(mouse_pos)
    for component in self.components:
      component.handle_mouse_motion(mouse_pos)

  def _on_blur(self):
    for component in self.components:
      component._on_blur()


class AbsolutePosContainer(AbstractContainer):

  def __init__(self, size: Tuple[int, int], screen, components: List[Tuple[Vector2, Component]]):
    super().__init__(size, screen, [c[1] for c in components])
    self.components = components

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    for relative_pos, component in self.components:
      component.set_pos(pos + relative_pos)


class HorizontalListContainer(AbstractContainer):
  def __init__(self, size: Tuple[int, int], screen, components: List[Component], margin: int, padding: int):
    super().__init__(size, screen, components)
    self.margin = margin
    self.padding = padding

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    relative_pos = Vector2(self.padding, self.padding)
    for component in self.components:
      component.set_pos(pos + relative_pos)
      relative_pos += (component.size[0] + self.margin, 0)


class VerticalListContainer(AbstractContainer):
  def __init__(self, width: int, screen, components: List[Component], margin: int, padding: int, **kwargs):
    super().__init__((width, 1), screen, components, **kwargs)
    self.margin = margin
    self.padding = padding
    children_sum_height = sum(c.size[1] for c in self.components)
    container_height = children_sum_height + (len(self.components) - 1) * self.margin + 2 * self.padding
    self.size = (self.size[0], container_height)

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    relative_pos = Vector2(self.padding, self.padding)
    for component in self.components:
      component.set_pos(pos + relative_pos)
      relative_pos += (0, component.size[1] + self.margin)


class EvenSpacingContainer(AbstractContainer):
  def __init__(self, size: Tuple[int, int], screen, components: List[Component], padding: int, **kwargs):
    super().__init__(size, screen, components, **kwargs)
    self.padding = padding

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    width_sum = sum([component.size[0] for component in self.components])
    margin = (self.size[0] - width_sum - self.padding * 2) / (len(self.components) - 1)
    relative_pos = Vector2(self.padding, self.padding)
    for component in self.components:
      component.set_pos(pos + relative_pos)
      relative_pos += (component.size[0] + margin, 0)
