from enum import Enum
from typing import List, Tuple, Any

from pygame.math import Vector2

from ui import Component


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


class Orientation(Enum):
  HORIZONTAL = 1
  VERTICAL = 2


class ListContainer(AbstractContainer):
  def __init__(self, width: Any, height: Any, screen, components: List[Component], margin: int, padding: int,
      orientation: Orientation, **kwargs):
    super().__init__((width, height), screen, components, **kwargs)
    self.margin = margin
    self.padding = padding
    if width == 'fit_contents':
      if orientation == Orientation.HORIZONTAL:
        children_sum = sum(c.size[0] for c in self.components)
        container_width = children_sum + (len(self.components) - 1) * self.margin + 2 * self.padding
      else:
        container_width = max(c.size[0] for c in self.components) + self.padding * 2
    else:
      container_width = width
    if height == 'fit_contents':
      if orientation == Orientation.HORIZONTAL:
        container_height = max(c.size[1] for c in self.components) + self.padding * 2
      else:
        children_sum = sum(c.size[1] for c in self.components)
        container_height = children_sum + (len(self.components) - 1) * self.margin + 2 * self.padding
    else:
      container_height = height
    self.size = (container_width, container_height)
    self.orientation = orientation

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    relative_pos = Vector2(self.padding, self.padding)
    for component in self.components:
      component.set_pos(pos + relative_pos)
      if self.orientation == Orientation.HORIZONTAL:
        relative_pos += (component.size[0] + self.margin, 0)
      else:
        relative_pos += (0, component.size[1] + self.margin)


class EvenSpacingContainer(AbstractContainer):
  def __init__(self, size: Tuple[int, int], screen, components: List[Component], padding: int, **kwargs):
    super().__init__(size, screen, components, **kwargs)
    self.padding = padding

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    width_sum = sum([component.size[0] for component in self.components])
    if len(self.components) < 2:
      margin = 0
    else:
      margin = (self.size[0] - width_sum - self.padding * 2) / (len(self.components) - 1)
    relative_pos = Vector2(self.padding, self.padding)
    for component in self.components:
      component.set_pos(pos + relative_pos)
      relative_pos += (component.size[0] + margin, 0)
