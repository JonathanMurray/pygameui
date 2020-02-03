#!/usr/bin/env python3
import os
from typing import Tuple, Callable, Any, Optional, List

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.time import Clock

from button import HoldDownBehavior, Button, SingleClickBehavior
from containers import GridContainer, EvenSpacingContainer, AbsolutePosContainer
from text import StaticText
from ui import Style

MATRIX_GREEN = Color(32, 194, 14)
WHITE = Color(255, 255, 255)
KEYBOARD_BACKGROUND_COLOR = Color(100, 100, 100)
COLOR_FILE = Color(50, 50, 50)
COLOR_DIR = Color(50, 50, 150)

SCREEN_RESOLUTION = (800, 600)
BUTTON_SIZE = (256, 24)
PADDING = 32


def change_dir(directory: str, buttons: List[Button], text_current_dir: StaticText):
  os.chdir(directory)
  file_names = os.listdir(".")
  text_current_dir.set_text(os.getcwd())
  setup_keys(file_names, buttons, text_current_dir)


def create_file_callback(filename: str, buttons: List[Button], text_current_dir: StaticText):
  return lambda: change_dir(filename, buttons, text_current_dir) if os.path.isdir(filename) else print("FILE")


def main():
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_RESOLUTION)
  pygame.display.set_caption("Keyboard & Terminal")
  clock = Clock()

  font = Font('resources/consola.ttf', 14)
  background_color = (0, 0, 0)

  grid_dimensions = (3, 13)
  buttons = [blank_button(font) for _ in range(grid_dimensions[0] * grid_dimensions[1])]

  grid = GridContainer(children=buttons, dimensions=grid_dimensions, padding=5, margin=1,
                       style=Style(background_color=KEYBOARD_BACKGROUND_COLOR, border_color=WHITE))
  grid_container = EvenSpacingContainer((SCREEN_RESOLUTION[0] - PADDING * 2, 300), [grid], padding=0)

  dir_path = os.path.dirname(os.path.realpath(__file__))
  text_current_dir = StaticText(font, Color(255, 255, 255), dir_path,
                                style=Style(background_color=Color(50, 50, 50)))
  file_names = os.listdir(".")

  container = AbsolutePosContainer(SCREEN_RESOLUTION,
                                   [(Vector2(PADDING, PADDING), text_current_dir),
                                    (Vector2(PADDING, 200), grid_container)])
  container.set_pos(Vector2(0, 0))

  setup_keys(file_names, buttons, text_current_dir)

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


def setup_keys(file_names: List[str], buttons: List[Button], text_current_dir: StaticText):
  buttons[0].set_label("..")
  buttons[0].set_callback(lambda: change_dir("..", buttons, text_current_dir))
  for i, btn in enumerate(buttons[1:]):
    if i < len(file_names):
      filename = file_names[i]
      btn.set_label(filename)
      btn.set_callback(create_file_callback(filename, buttons, text_current_dir))
      btn.set_label_color(Color(150, 150, 255) if os.path.isdir(filename) else WHITE)
    else:
      btn.set_label("")
      btn.set_callback(lambda: None)


def blank_button(font):
  return button(font, BUTTON_SIZE, callback=lambda: None, label="", background_color=COLOR_FILE)


def dir_button(font):
  return button(font, BUTTON_SIZE, callback=lambda: None, label="", background_color=Color(255, 255, 0))


def button(font, size: Tuple[int, int], callback: Callable[[], Any], label: str, background_color: Color,
    hotkey: Optional[int] = None,
    hold: Optional[HoldDownBehavior] = None):
  return Button(size=size,
                callback=callback,
                label=StaticText(font, WHITE, label),
                behavior=hold if hold else SingleClickBehavior(),
                hotkey=hotkey,
                style=Style(background_color=background_color),
                style_hovered=Style(background_color=background_color, border_color=Color(210, 210, 210),
                                    border_width=1),
                style_onclick=Style(background_color=background_color, border_color=MATRIX_GREEN,
                                    border_width=3))


def handle_exit(event):
  if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    pygame.quit()
    exit(0)


if __name__ == '__main__':
  main()
