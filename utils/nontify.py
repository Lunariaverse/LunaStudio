from .config import resource_path
from .log import Logger
import pygame
import traceback
import sys


class Notification:
    _font = None

    def __init__(self):
        self.logger = Logger("Notification")

    def create(
        self,
        caption,
        text,
        width=400,
        padding=20,
        bg_color=(30, 30, 30),
        text_color=(255, 255, 255),
        font_size=28,
    ):
        try:
            pygame.init()
            if not Notification._font:
                Notification._font = pygame.font.SysFont(None, font_size)

            font = Notification._font
            lines = text.split("\n")
            line_height = font.get_height()
            height = line_height * len(lines) + padding * 2
            icon = pygame.image.load(resource_path("Assets/LunaStudio.png"))
            pygame.display.set_icon(icon)
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(caption)

            running = True
            clock = pygame.time.Clock()

            while running:
                screen.fill(bg_color)

                for idx, line in enumerate(lines):
                    text_surface = font.render(line, True, text_color)
                    text_rect = text_surface.get_rect(
                        center=(
                            width // 2,
                            padding + idx * line_height + line_height // 2,
                        )
                    )
                    screen.blit(text_surface, text_rect)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        sys.exit()

                clock.tick(30)
        except Exception as e:
            self.logger.LogExit("create", e)
            sys.exit()
