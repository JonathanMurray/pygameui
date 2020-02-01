from enum import Enum
from typing import List, Tuple, Any

from pygame.math import Vector2

from ui import Component


class AbstractContainer(Component):
  def __init__(self, size: Tuple[int, int], screen, children: List[Component], **kwargs):
    super().__init__(size, screen, **kwargs)
    self._children = children

  def _render(self):
    for component in self._children:
      component.render()

  def _on_click(self, mouse_pos: Tuple[int, int]):
    for component in self._children:
      component.handle_mouse_click(mouse_pos)

  def update(self, elapsed_time: int):
    for component in self._children:
      component.update(elapsed_time)

  def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
    super().handle_mouse_motion(mouse_pos)
    for component in self._children:
      component.handle_mouse_motion(mouse_pos)

  def _on_blur(self):
    for component in self._children:
      component._on_blur()


class AbsolutePosContainer(AbstractContainer):

  def __init__(self, size: Tuple[int, int], screen, children: List[Tuple[Vector2, Component]]):
    super().__init__(size, screen, [c[1] for c in children])
    self._children = children

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    for relative_pos, component in self._children:
      component.set_pos(pos + relative_pos)


class Orientation(Enum):
  HORIZONTAL = 1
  VERTICAL = 2


class ListContainer(AbstractContainer):
  def __init__(self, width: Any, height: Any, screen, children: List[Component], margin: Any, padding: int,
      orientation: Orientation, **kwargs):
    super().__init__((width, height), screen, children, **kwargs)
    self._margin = margin
    self._padding = padding
    if width == 'fit_contents':
      if orientation == Orientation.HORIZONTAL:
        children_sum = sum(c.size[0] for c in self._children)
        container_width = children_sum + (len(self._children) - 1) * self._margin + 2 * self._padding
      else:
        container_width = max(c.size[0] for c in self._children) + self._padding * 2
    else:
      container_width = width
    if height == 'fit_contents':
      if orientation == Orientation.HORIZONTAL:
        container_height = max(c.size[1] for c in self._children) + self._padding * 2
      else:
        children_sum = sum(c.size[1] for c in self._children)
        container_height = children_sum + (len(self._children) - 1) * self._margin + 2 * self._padding
    else:
      container_height = height

    self.size = (container_width, container_height)
    self._orientation = orientation

    for child in children:
      if child.size[0] == 'fill_parent':
        if self._orientation == Orientation.VERTICAL:
          child.size = (self.size[0] - self._padding * 2, child.size[1])
        else:
          raise Exception("Cannot fill child's width inside a horizontal list!")
      if child.size[1] == 'fill_parent':
        if self._orientation == Orientation.HORIZONTAL:
          child.size = (child.size[0], self.size[1] - self._padding * 2)
        else:
          raise Exception("Cannot fill child's height inside a vertical list!")
    print("Children: %s" % [(c, c.size) for c in self._children])

    if margin == 'auto':
      if len(self._children) < 2:
        self._margin = 0
      elif orientation == Orientation.HORIZONTAL:
        width_sum = sum([component.size[0] for component in self._children])
        self._margin = (self.size[0] - width_sum - self._padding * 2) / (len(self._children) - 1)
      else:
        height_sum = sum([component.size[1] for component in self._children])
        self._margin = (self.size[1] - height_sum - self._padding * 2) / (len(self._children) - 1)

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    relative_pos = Vector2(self._padding, self._padding)
    for component in self._children:
      component.set_pos(pos + relative_pos)
      if self._orientation == Orientation.HORIZONTAL:
        relative_pos += (component.size[0] + self._margin, 0)
      else:
        relative_pos += (0, component.size[1] + self._margin)


class EvenSpacingContainer(AbstractContainer):
  def __init__(self, size: Tuple[int, int], screen, children: List[Component], padding: int, **kwargs):
    super().__init__(size, screen, children, **kwargs)
    self._padding = padding

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    width_sum = sum([component.size[0] for component in self._children])
    if len(self._children) < 2:
      margin = 0
    else:
      margin = (self.size[0] - width_sum - self._padding * 2) / (len(self._children) - 1)
    relative_pos = Vector2(self._padding, self._padding)
    for component in self._children:
      component.set_pos(pos + relative_pos)
      relative_pos += (component.size[0] + margin, 0)
