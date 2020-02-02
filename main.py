#!/usr/bin/env python3

import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.time import Clock, set_timer

from button import button
from checkbox import checkbox
from containers import ListContainer, Orientation, AbsolutePosContainer, ScrollContainer, GridContainer
from text import TextField
from ui import BackgroundGrid, Style, Text, Counter, FormattedText

SCREEN_RESOLUTION = (800, 600)
COLOR_WHITE = Color(255, 255, 255)

USEREVENT_EACH_SECOND = pygame.USEREVENT + 1


def main():
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_RESOLUTION)
  clock = Clock()
  set_timer(USEREVENT_EACH_SECOND, 1000)

  font = Font('Arial Rounded Bold.ttf', 14)
  background_color = (0, 0, 0)
  grid = BackgroundGrid(SCREEN_RESOLUTION, Color(20, 20, 20), 32)

  fps_text = FormattedText(font, COLOR_WHITE, "FPS: %i", 0)
  debug_texts = [
    fps_text,
    Text(font, COLOR_WHITE, "debug: 2"),
    Text(font, COLOR_WHITE, "debug: 3"),
  ]
  debug_window = ListContainer(width=200, height="fit_contents", children=debug_texts, margin=5,
                               padding=5, orientation=Orientation.VERTICAL,
                               style=Style(border_color=COLOR_WHITE))

  left_buttons = [
    button(font, (200, 48), callback=lambda: print("hello"), label="click"),
    button(font, (200, 48), callback=lambda: print("hello"), label="click"),
    button(font, (200, 48), callback=lambda: print("hello"), label="click"),
  ]
  counter = Counter((50, 50), FormattedText(font, COLOR_WHITE, "%i", 0),
                    style=Style(background=Color(100, 100, 100)))
  right_buttons = [
    button(font, (200, 32), callback=lambda: counter.increment(), label="Increment (I)", hotkey=pygame.K_i),
    button(font, (200, 32), callback=lambda: counter.decrement(), label="Decrement (D)", hotkey=pygame.K_d),
    checkbox(font, (200, 32), callback=lambda checked: debug_window.set_visible(checked), label="Show debug",
             checked=debug_window.is_visible()),
    checkbox(font, (200, 32), callback=lambda checked: print("B: %s" % checked), label="B"),
    checkbox(font, (200, 32), callback=lambda checked: print("C: %s" % checked), label="C"),
    checkbox(font, (200, 32), callback=lambda checked: print("D: %s" % checked), label="D"),
    checkbox(font, (200, 32), callback=lambda checked: print("E: %s" % checked), label="E"),
    checkbox(font, (200, 32), callback=lambda checked: print("F: %s" % checked), label="F"),
  ]
  left_menu_bar = ListContainer(width="fit_contents", height="fill_parent", children=left_buttons,
                                margin=5, padding=5,
                                orientation=Orientation.VERTICAL,
                                style=Style(background=Color(150, 150, 255), border_color=COLOR_WHITE))
  right_menu_bar = ScrollContainer(height=166, children=right_buttons,
                                   margin=5, padding=5,
                                   orientation=Orientation.VERTICAL,
                                   style=Style(background=Color(150, 210, 255), border_color=COLOR_WHITE))

  text_field = TextField(font, (100, 24), padding=5, max_length=9,
                         style=Style(border_color=COLOR_WHITE))

  grid_children = [
    number_button(font, text_field, "1", pygame.K_1),
    number_button(font, text_field, "2", pygame.K_2),
    number_button(font, text_field, "3", pygame.K_3),
    number_button(font, text_field, "4", pygame.K_4),
    number_button(font, text_field, "5", pygame.K_5),
    number_button(font, text_field, "6", pygame.K_6),
    number_button(font, text_field, "7", pygame.K_7),
    number_button(font, text_field, "8", pygame.K_8),
    number_button(font, text_field, "9", pygame.K_9),
    number_button(font, text_field, "0", pygame.K_0),
    backspace_button(font, text_field)
  ]
  grid_container = GridContainer(children=grid_children, dimensions=(3, 4), padding=5, margin=2,
                                 style=Style(background=Color(150, 130, 100), border_color=COLOR_WHITE))

  hud = ListContainer(width=800, height=200,
                      children=[left_menu_bar, right_menu_bar, counter, grid_container, text_field],
                      margin=5,
                      padding=5, orientation=Orientation.HORIZONTAL,
                      style=Style(border_color=COLOR_WHITE, background=Color(0, 0, 150)))
  container = AbsolutePosContainer(SCREEN_RESOLUTION, [(Vector2(5, 5), debug_window), (Vector2(0, 400), hud)])
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
      elif event.type == USEREVENT_EACH_SECOND:
        fps_text.format_text(int(clock.get_fps()))
      elif event.type == pygame.KEYDOWN:
        container.handle_key_was_pressed(event.key)
    elapsed_time = clock.tick()

    container.update(elapsed_time)

    screen.fill(background_color)
    grid.render(screen)
    container.render(screen)
    pygame.display.flip()


def number_button(font, text_area: TextField, text: str, key):
  return button(font, (32, 32), callback=lambda: text_area.append(text), label=text, hotkey=key)


def backspace_button(font, text_area: TextField):
  return button(font, (32, 32), callback=lambda: text_area.backspace(), label="<-", hotkey=pygame.K_BACKSPACE)


def handle_exit(event):
  if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    pygame.quit()
    exit(0)


if __name__ == '__main__':
  main()
