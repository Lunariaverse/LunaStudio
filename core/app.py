from src import Logger, Config, LayerManager, Params, Capture
import pygame, time, gc, threading, sys
import live2d.v3 as live2d

from core.capture import CaptureMixin
from core.render import RenderMixin
from core.model import ModelMixin
from core.setup import AppSetup


class Live2DApp(AppSetup, CaptureMixin, ModelMixin, RenderMixin):
    def __init__(self, debugL2D=False):
        self.LayerManager = LayerManager()
        self.logger = Logger("Live2DApp")
        self.Capture = Capture(app=self)
        self.config_internal = {}
        self.display_size = None
        self.debugL2D = debugL2D
        self.background = None
        self.params = Params()
        self.config = Config()
        self.config_data = {}
        self.running = True
        self.model = None

    def run(self):
        try:
            self.app_init()
            self.start_capture()
            clock = pygame.time.Clock()
            gc.collect()

            while self.running:
                self._handle_events()
                self._update_parameters()
                self._render_frame()

                if self.config_data["CapFPS"]["capFps"]:
                    clock.tick(self.config_data["CapFPS"]["CapFpsValue"])
                else:
                    time.sleep(0.005)
        except Exception as e:
            self.logger.LogExit("run", e)
            self.running = False

        finally:
            print("[Main] Threads before exit:", threading.enumerate())
            print("[Main] running flag: ", self.running)
            self.running = False
            live2d.dispose()
            pygame.quit()
            print("[Main] dispose complete")
            print("[Main] running flag: ", self.running)
            print("[Main] Threads after exit:", threading.enumerate())
            sys.exit(0)
