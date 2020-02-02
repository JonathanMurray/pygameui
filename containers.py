from enum import Enum
from typing import List, Tuple, Any, Optional

import pygame
from pygame.color import Color
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from ui import Component


class AbstractContainer(Component):
  def __init__(self, size: Tuple[int, int], children: List[Component], **kwargs):
    super().__init__(size, **kwargs)
    self._children = children

  def _render_contents(self, surface):
    for component in self._children:
      component.render(surface)

  def _on_click(self, mouse_pos: Optional[Tuple[int, int]]):
    for component in self._children:
      component.handle_mouse_was_clicked(mouse_pos)

  def update(self, elapsed_time: int):
    for component in self._children:
      component.update(elapsed_time)

  def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
    super().handle_mouse_motion(mouse_pos)
    for component in self._children:
      component.handle_mouse_motion(mouse_pos)

  def handle_key_was_pressed(self, key):
    for component in self._children:
      component.handle_key_was_pressed(key)

  def handle_key_was_released(self, key):
    for component in self._children:
      component.handle_key_was_released(key)

  def _on_blur(self):
    for component in self._children:
      component._on_blur()

  def handle_mouse_was_released(self):
    for component in self._children:
      component.handle_mouse_was_released()


class AbsolutePosContainer(AbstractContainer):

  def __init__(self, size: Tuple[int, int], positioned_children: List[Tuple[Vector2, Component]]):
    super().__init__(size, [c[1] for c in positioned_children])
    self._positioned_children = positioned_children

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    for relative_pos, component in self._positioned_children:
      component.set_pos(pos + relative_pos)


class Orientation(Enum):
  HORIZONTAL = 1
  VERTICAL = 2


class ListContainer(AbstractContainer):
  def __init__(self, width: Any, height: Any, children: List[Component], margin: Any, padding: int,
      orientation: Orientation, **kwargs):
    super().__init__((width, height), children, **kwargs)
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
  def __init__(self, size: Tuple[int, int], children: List[Component], padding: int, **kwargs):
    super().__init__(size, children, **kwargs)
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


# NOTE: Scroll container sets "local" positions for its children, in contrast to other containers
# The children are rendered on a separate surface and then blitted / clipped onto the screen
class ScrollContainer(AbstractContainer):
  SCROLLBAR_WIDTH = 15
  SCROLLBAR_MARGIN = 5

  def __init__(self, height: Any, children: List[Component], padding: int, margin: int, **kwargs):
    container_width = max(c.size[0] for c in children) \
                      + padding * 2 \
                      + ScrollContainer.SCROLLBAR_WIDTH \
                      + ScrollContainer.SCROLLBAR_MARGIN
    size = (container_width, height)
    super().__init__(size, children, **kwargs)
    sum_height = sum(c.size[1] for c in children) + padding * 2 + margin * (len(children) - 1)
    self._max_scroll = sum_height - height
    self._padding = padding
    self._margin = margin
    self._scroll_y = 0
    self._scrollbar = None
    self._scrollbar_top = None
    self._scrollbar_bottom = None
    self._scrolling_velocity = 0

  def scroll(self, dy: int):
    self._scroll_y = max(0, min(self._scroll_y + dy, self._max_scroll))
    self._update_children()

  def _render_contents(self, surface):
    s = Surface(self.size, pygame.SRCALPHA)
    for component in self._children:
      component.render(s)
    surface.blit(s, self._rect.topleft)
    pygame.draw.rect(surface, Color(150, 150, 150), self._scrollbar)
    height = 10
    up_arrow = [(self._scrollbar.centerx, self._scrollbar.top + 2),
                (self._scrollbar.left + 1, self._scrollbar.top + 2 + height),
                (self._scrollbar.right - 2, self._scrollbar.top + 2 + height)]
    pygame.draw.aalines(surface, Color(255, 255, 255), True, up_arrow)
    down_arrow = [(self._scrollbar.centerx, self._scrollbar.bottom - 2),
                  (self._scrollbar.left + 1, self._scrollbar.bottom - 2 - height),
                  (self._scrollbar.right - 2, self._scrollbar.bottom - 2 - height)]
    pygame.draw.aalines(surface, Color(255, 255, 255), True, down_arrow)

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    self._update_children()
    self._scrollbar = Rect(
        self._rect.right - ScrollContainer.SCROLLBAR_WIDTH - ScrollContainer.SCROLLBAR_MARGIN,
        self._rect.top + ScrollContainer.SCROLLBAR_MARGIN,
        ScrollContainer.SCROLLBAR_WIDTH,
        self._rect.h - ScrollContainer.SCROLLBAR_MARGIN * 2)
    self._scrollbar_top = Rect(self._scrollbar.x, self._scrollbar.y, self._scrollbar.w, self._scrollbar.h // 2)
    self._scrollbar_bottom = Rect(self._scrollbar.x, self._scrollbar.y + self._scrollbar.h // 2, self._scrollbar.w,
                                  self._scrollbar.h // 2)

  def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
    super().handle_mouse_motion(mouse_pos)
    local_mouse_pos = (mouse_pos[0] - self._rect.x, mouse_pos[1] - self._rect.y)
    for component in self._children:
      component.handle_mouse_motion(local_mouse_pos)

  def _on_click(self, mouse_pos: Optional[Tuple[int, int]]):
    local_mouse_pos = (mouse_pos[0] - self._rect.x, mouse_pos[1] - self._rect.y)
    scroll_amount = 3
    if self._scrollbar_top.collidepoint(mouse_pos):
      self._scrolling_velocity = -scroll_amount
    if self._scrollbar_bottom.collidepoint(mouse_pos):
      self._scrolling_velocity = scroll_amount
    for component in self._children:
      component.handle_mouse_was_clicked(local_mouse_pos)

  def handle_mouse_was_released(self):
    super().handle_mouse_was_released()
    self._scrolling_velocity = 0

  def _update_children(self):
    pos = Vector2(self._padding, self._padding - self._scroll_y)
    for component in self._children:
      component.set_pos(pos)
      pos += (0, component.size[1] + self._margin)

  def update(self, elapsed_time: int):
    super().update(elapsed_time)
    self.scroll(self._scrolling_velocity)


class GridContainer(AbstractContainer):
  def __init__(self, children: List[Component], dimensions: Tuple[int, int], padding: int, margin: int, **kwargs):
    self._cell_size = (max(c.size[0] for c in children), max(c.size[1] for c in children))
    size = (dimensions[0] * self._cell_size[0] + 2 * padding + (dimensions[0] - 1) * margin,
            dimensions[1] * self._cell_size[1] + 2 * padding + (dimensions[1] - 1) * margin)
    super().__init__(size, children, **kwargs)
    self._dimensions = dimensions
    self._padding = padding
    self._margin = margin

  def set_pos(self, pos: Vector2):
    super().set_pos(pos)
    relative_pos = (self._padding, self._padding)
    num_cols = self._dimensions[0]
    for i, component in enumerate(self._children):
      component.set_pos(pos + relative_pos)
      if i % num_cols == num_cols - 1:
        relative_pos = (self._padding, relative_pos[1] + self._cell_size[1] + self._margin)
      else:
        relative_pos = (relative_pos[0] + self._cell_size[0] + self._margin, relative_pos[1])
