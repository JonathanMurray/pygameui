#!/usr/bin/env python3

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.time import Clock

from containers import ListContainer, Orientation
from ui import BackgroundGrid, Button, Text, Style

SCREEN_RESOLUTION = (800, 600)
COLOR_WHITE = Color(255, 255, 255, 0)


def main():
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_RESOLUTION)
  clock = Clock()
  font = Font('Arial Rounded Bold.ttf', 14)
  background_color = (0, 0, 0)
  grid = BackgroundGrid(screen, SCREEN_RESOLUTION, Color(20, 20, 20, 0), 32)

  left_buttons = [
    button(font, screen, (200, 48), callback=lambda: print("hello"), text="click"),
    button(font, screen, (200, 48), callback=lambda: print("hello"), text="click"),
    button(font, screen, (200, 48), callback=lambda: print("hello"), text="click"),
  ]
  right_buttons = [
    button(font, screen, (200, 32), callback=lambda: print("bye"), text="click"),
    button(font, screen, (200, 32), callback=lambda: print("bye"), text="click"),
    button(font, screen, (200, 32), callback=lambda: print("bye"), text="click"),
  ]
  left_menu_bar = ListContainer(width="fit_contents", height="fill_parent", screen=screen, children=left_buttons,
                                margin=5, padding=5,
                                orientation=Orientation.VERTICAL,
                                style=Style(background=(150, 150, 255, 0), border_color=COLOR_WHITE))
  right_menu_bar = ListContainer(width="fit_contents", height="fit_contents", screen=screen, children=right_buttons,
                                 margin=5, padding=5,
                                 orientation=Orientation.VERTICAL,
                                 style=Style(background=(150, 210, 255, 0)))
  container = ListContainer(width=800, height=200, screen=screen, children=[left_menu_bar, right_menu_bar], margin=5,
                            padding=5, orientation=Orientation.HORIZONTAL,
                            style=Style(border_color=COLOR_WHITE, background=(0, 0, 150, 0)))
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


def button(font, screen, size, callback, text: str):
  return Button(size=size, screen=screen, callback=callback,
                text=Text(screen, font, COLOR_WHITE, text),
                style=Style(background=Color(50, 50, 100, 0), border_color=Color(150, 150, 150, 0)),
                style_hovered=Style(background=Color(80, 80, 120), border_color=Color(180, 180, 180, 0)),
                style_onclick=Style(background=Color(80, 80, 120), border_color=Color(200, 255, 200, 0),
                                    border_width=2))


def handle_exit(event):
  if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    pygame.quit()
    exit(0)


if __name__ == '__main__':
  main()
