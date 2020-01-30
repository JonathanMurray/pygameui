#!/usr/bin/env python3

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.time import Clock

from ui import BackgroundGrid, Component, VerticalListContainer, Button, Text, Style

SCREEN_RESOLUTION = (800, 600)
COLOR_WHITE = Color(255, 255, 255, 0)


def main():
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_RESOLUTION)
  clock = Clock()
  font = Font('Arial Rounded Bold.ttf', 14)
  background_color = (0, 0, 0)
  grid = BackgroundGrid(screen, SCREEN_RESOLUTION, Color(20, 20, 20, 0), 32)

  button2 = button(font, screen, (200, 100), lambda: print("C"), "Click C")
  div = Component(size=(200, 100), screen=screen, style=Style(background=COLOR_WHITE))
  button3 = button(font, screen, (200, 100), lambda: print("B"), "Click B")
  container = VerticalListContainer(500, screen, [button2, div, button3], 5, 20, border=COLOR_WHITE,
                                    background=(0, 0, 150, 0))
  container.set_pos(Vector2(0, 0))

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
                style=Style(background=Color(50, 50, 100, 0), border=Color(150, 150, 150, 0)),
                style_hovered=Style(background=Color(50, 50, 100), border=Color(180, 180, 180, 0)),
                style_onclick=Style(background=Color(50, 50, 100), border=Color(200, 255, 200, 0)))


def handle_exit(event):
  if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    pygame.quit()
    exit(0)


if __name__ == '__main__':
  main()
