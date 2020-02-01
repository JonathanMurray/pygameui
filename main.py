#!/usr/bin/env python3

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.time import Clock

from buttons import button, checkbox
from containers import ListContainer, Orientation
from ui import BackgroundGrid, Style

SCREEN_RESOLUTION = (800, 600)
COLOR_WHITE = Color(255, 255, 255)


def main():
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_RESOLUTION)
  clock = Clock()
  font = Font('Arial Rounded Bold.ttf', 14)
  background_color = (0, 0, 0)
  grid = BackgroundGrid(screen, SCREEN_RESOLUTION, Color(20, 20, 20), 32)

  left_buttons = [
    button(font, screen, (200, 48), callback=lambda: print("hello"), label="click"),
    button(font, screen, (200, 48), callback=lambda: print("hello"), label="click"),
    button(font, screen, (200, 48), callback=lambda: print("hello"), label="click"),
  ]
  right_buttons = [
    button(font, screen, (200, 32), callback=lambda: print("bye"), label="click"),
    button(font, screen, (200, 32), callback=lambda: print("bye"), label="click"),
    checkbox(font, screen, (200, 32), callback=lambda checked: print("A: %s" % checked), label="A"),
    checkbox(font, screen, (200, 32), callback=lambda checked: print("B: %s" % checked), label="B"),
  ]
  left_menu_bar = ListContainer(width="fit_contents", height="fill_parent", screen=screen, children=left_buttons,
                                margin=5, padding=5,
                                orientation=Orientation.VERTICAL,
                                style=Style(background=Color(150, 150, 255), border_color=COLOR_WHITE))
  right_menu_bar = ListContainer(width="fit_contents", height="fit_contents", screen=screen, children=right_buttons,
                                 margin=5, padding=5,
                                 orientation=Orientation.VERTICAL,
                                 style=Style(background=Color(150, 210, 255)))
  container = ListContainer(width=800, height=200, screen=screen, children=[left_menu_bar, right_menu_bar], margin=5,
                            padding=5, orientation=Orientation.HORIZONTAL,
                            style=Style(border_color=COLOR_WHITE, background=Color(0, 0, 150)))
  container.set_pos(Vector2(0, 400))

  while True:
    for event in pygame.event.get():
      handle_exit(event)
      if event.type == pygame.MOUSEBUTTONDOWN:
        container.handle_mouse_click(pygame.mouse.get_pos())
      elif event.type == pygame.MOUSEMOTION:
        container.handle_mouse_motion(pygame.mouse.get_pos())

    elapsed_time = clock.tick()

    container.update(elapsed_time)

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
