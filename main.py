#!/usr/bin/env python3
from typing import List, Tuple, Callable, Any

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.rect import Rect

COLOR_WHITE = Color(255, 255, 255, 0)
SCREEN_RESOLUTION = (800, 600)


class BackgroundGrid:
  def __init__(self, screen, line_color: Color, cell_width):
    self.screen = screen
    self.line_color = line_color
    self.cell_width = cell_width

  def render(self):
    for x in range(0, SCREEN_RESOLUTION[0], self.cell_width):
      pygame.draw.line(self.screen, self.line_color, (x, 0), (x, SCREEN_RESOLUTION[1]))
    for y in range(0, SCREEN_RESOLUTION[1], self.cell_width):
      pygame.draw.line(self.screen, self.line_color, (0, y), (SCREEN_RESOLUTION[0], y))


class Component:

  def __init__(self, size: Tuple[int, int], screen, **kwargs):
    self.size = size
    self.screen = screen
    self.rect = None
    self.background = kwargs.get('background')
    self.border = kwargs.get('border')

  def set_pos(self, pos: Vector2):
    self.rect = Rect(pos, self.size)

  def handle_mouse_click(self, mouse_pos: Tuple[int, int]):
    self._assert_initialized()
    if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
      self._on_click(mouse_pos)

  def render(self):
    self._assert_initialized()
    if self.background:
      pygame.draw.rect(self.screen, self.background, self.rect)
    self._render()
    if self.border:
      pygame.draw.rect(self.screen, self.border, self.rect, 1)

  def _render(self):
    pass

  def _on_click(self, mouse_pos: Tuple[int, int]):
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
    print("Button was clicked: %s" % self)
    if self.callback:
      self.callback()


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
    print(self.size)

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


def main():
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_RESOLUTION)
  font = Font('Arial Rounded Bold.ttf', 14)
  background_color = (0, 0, 0)
  grid = BackgroundGrid(screen, Color(20, 20, 20, 0), 32)

  button1 = ColorToggler(size=(200, 100), screen=screen,
                         text=Text(screen, font, COLOR_WHITE, "Click me to change color!"),
                         colors=[Color(255, 0, 0, 0), Color(0, 255, 0, 0), Color(0, 0, 255, 0)],
                         border=COLOR_WHITE)

  button2 = Button(size=(200, 100), screen=screen, callback=lambda: print("I said don't!"),
                   text=Text(screen, font, COLOR_WHITE, "Don't click me"), background=Color(0, 0, 100, 0),
                   border=COLOR_WHITE)
  button3 = Button(size=(200, 100), screen=screen, callback=lambda: print("Hello"),
                   text=Text(screen, font, Color(255, 0, 0, 0), "Button 3"), background=Color(0, 0, 100, 0),
                   border=COLOR_WHITE)
  div = Component(size=(200, 100), screen=screen, background=COLOR_WHITE)
  container = VerticalListContainer(500, screen, [button1, button2, div, button3], 5, 20, border=COLOR_WHITE,
                                    background=(0, 0, 150, 0))
  container.set_pos(Vector2(0, 0))

  while True:
    for event in pygame.event.get():
      handle_exit(event)
      if event.type == pygame.MOUSEBUTTONDOWN:
        # print("Mouse-click: (%s, %s)" % pygame.mouse.get_pos())
        container.handle_mouse_click(pygame.mouse.get_pos())

    screen.fill(background_color)
    grid.render()
    container.render()
    pygame.display.flip()


def handle_exit(event):
  if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    pygame.quit()
    exit(0)


if __name__ == '__main__':
  main()
