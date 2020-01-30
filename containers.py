from typing import List, Tuple

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
