import live2d.v3 as live2d
import pygame, sys


class RenderMixin:
    def _render_frame(self):
        try:
            live2d.clearBuffer()
            self.background.Draw()
            self.model.Update()
            self.model.Draw()

            pygame.display.flip()
        except Exception as e:
            self.logger.LogExit("_render_frame", e)
            self.running = False

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
