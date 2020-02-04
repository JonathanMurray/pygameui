#!/usr/bin/env python3
from typing import Tuple, Callable, Any, Optional

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.time import Clock

from button import button, HoldDownBehavior, Button, SingleClickBehavior
from containers import GridContainer, EvenSpacingContainer, AbsolutePosContainer
from text import StaticText, BlinkingCursor
from text import TextArea
from ui import Style, Component

MATRIX_GREEN = Color(32, 194, 14)
WHITE = Color(255, 255, 255)
KEYBOARD_BACKGROUND_COLOR = Color(100, 100, 100)
BUTTON_BACKGROUND_COLOR = Color(50, 50, 50)

SCREEN_RESOLUTION = (800, 600)
BUTTON_SIZE = (64, 64)
PADDING = 32


def main():
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_RESOLUTION)
  pygame.display.set_caption("Keyboard & Terminal")
  clock = Clock()

  font = Font('resources/Arial Rounded Bold.ttf', 18)
  font_large = Font('resources/consola.ttf', 32)
  background_color = (0, 0, 0)

  terminal = TextArea(font_large, MATRIX_GREEN, (SCREEN_RESOLUTION[0] - PADDING * 2, 300), padding=16,
                      blinking_cursor=BlinkingCursor(800),
                      style=Style(border_color=WHITE))

  key_components = [
    keyboard_button(font, terminal, pygame.K_q),
    keyboard_button(font, terminal, pygame.K_w),
    keyboard_button(font, terminal, pygame.K_e),
    keyboard_button(font, terminal, pygame.K_r),
    keyboard_button(font, terminal, pygame.K_t),
    keyboard_button(font, terminal, pygame.K_y),
    keyboard_button(font, terminal, pygame.K_u),
    keyboard_button(font, terminal, pygame.K_i),
    keyboard_button(font, terminal, pygame.K_o),
    keyboard_button(font, terminal, pygame.K_p),
    keyboard_button(font, terminal, pygame.K_a),
    keyboard_button(font, terminal, pygame.K_s),
    keyboard_button(font, terminal, pygame.K_d),
    keyboard_button(font, terminal, pygame.K_f),
    keyboard_button(font, terminal, pygame.K_g),
    keyboard_button(font, terminal, pygame.K_h),
    keyboard_button(font, terminal, pygame.K_j),
    keyboard_button(font, terminal, pygame.K_k),
    keyboard_button(font, terminal, pygame.K_l),
    return_button(font, terminal),
    blank_button(font),
    keyboard_button(font, terminal, pygame.K_z),
    keyboard_button(font, terminal, pygame.K_x),
    keyboard_button(font, terminal, pygame.K_c),
    keyboard_button(font, terminal, pygame.K_v),
    keyboard_button(font, terminal, pygame.K_b),
    keyboard_button(font, terminal, pygame.K_n),
    keyboard_button(font, terminal, pygame.K_m),
    space_button(font, terminal),
    backspace_button(font, terminal)
  ]

  keyboard = GridContainer(children=key_components, dimensions=(10, 3), padding=5, margin=5,
                           style=Style(background_color=KEYBOARD_BACKGROUND_COLOR, border_color=WHITE))
  keyboard_container = EvenSpacingContainer(SCREEN_RESOLUTION[0] - PADDING * 2, 300, [keyboard], padding=0)

  container = AbsolutePosContainer(SCREEN_RESOLUTION,
                                   [(Vector2(PADDING, PADDING), terminal), (Vector2(PADDING, 360), keyboard_container)])
  container.set_pos(Vector2(0, 0))

  while True:
    for event in pygame.event.get():
      handle_exit(event)
      if event.type == pygame.MOUSEBUTTONDOWN:
        container.handle_mouse_was_clicked(pygame.mouse.get_pos())
      elif event.type == pygame.MOUSEBUTTONUP:
        container.handle_mouse_was_released()
      elif event.type == pygame.MOUSEMOTION:
        container.handle_mouse_motion(pygame.mouse.get_pos())
      elif event.type == pygame.KEYDOWN:
        container.handle_key_was_pressed(event.key)
      elif event.type == pygame.KEYUP:
        container.handle_key_was_released(event.key)
    elapsed_time = clock.tick()

    container.update(elapsed_time)

    screen.fill(background_color)
    container.render(screen)
    pygame.display.flip()


def keyboard_button(font, text_area: TextArea, key: int) -> Component:
  text = chr(key).upper()
  return button(font, BUTTON_SIZE, callback=lambda: text_area.append(text), label=text, hotkey=key,
                hold=button_behavior())


def blank_button(font):
  return button(font, BUTTON_SIZE, callback=lambda: None, label="")


def space_button(font, text_area: TextArea):
  return button(font, BUTTON_SIZE, callback=lambda: text_area.append(" "), label="Space", hotkey=pygame.K_SPACE,
                hold=button_behavior())


def return_button(font, text_area: TextArea):
  return button(font, BUTTON_SIZE, callback=lambda: text_area.append("\n"), label="RET", hotkey=pygame.K_RETURN,
                hold=button_behavior())


def backspace_button(font, text_area: TextArea):
  return button(font, BUTTON_SIZE, callback=lambda: text_area.backspace(), label="<-", hotkey=pygame.K_BACKSPACE,
                hold=button_behavior())


def button_behavior():
  return HoldDownBehavior(400, 30)


def button(font, size: Tuple[int, int], callback: Callable[[], Any], label: str, hotkey: Optional[int] = None,
    hold: Optional[HoldDownBehavior] = None):
  return Button(size=size,
                callback=callback,
                label=StaticText(font, WHITE, label),
                behavior=hold if hold else SingleClickBehavior(),
                hotkey=hotkey,
                style=Style(background_color=BUTTON_BACKGROUND_COLOR, border_color=Color(150, 150, 150)),
                style_hovered=Style(background_color=BUTTON_BACKGROUND_COLOR, border_color=Color(210, 210, 210),
                                    border_width=2),
                style_onclick=Style(background_color=BUTTON_BACKGROUND_COLOR, border_color=MATRIX_GREEN,
                                    border_width=3))


def handle_exit(event):
  if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    pygame.quit()
    exit(0)


if __name__ == '__main__':
  main()
