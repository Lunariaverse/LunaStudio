from src import (
    Constract,
    Config,
    resource_path,
    Mediapipe,
    Image,
    Params,
    setup_logger,
)
from live2d.v3.params import StandardParams
from collections import namedtuple
import live2d.v3 as live2d
from pathlib import Path
import threading
import pygame
import shutil
import sys
import os
import time
import traceback


class Notification:
    _font = None

    def __init__(self):
        self.logger = setup_logger("Notification")

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
            icon = pygame.image.load(resource_path("src/media/LunaStudio.png"))
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
                        Live2DApp._close()
                        pygame.quit()
                        sys.exit()

                clock.tick(30)
        except Exception as e:
            self.logger.error(f"[ERROR] Notification failed: {e}")
            traceback.print_exc()


class Live2DApp:
    def __init__(self):
        self.logger = setup_logger("Live2DApp")
        self.config = Config()
        self.config_data = {}
        self.model = None
        self.params = Params()
        self.background = None
        self.display_size = None
        self.running = False
        self._capture_started = False

    def app_init(self):
        try:
            folders = ["media", "media/model", "media/Assets"]
            created = False
            for folder in folders:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    created = True
                    if folder == "media/Assets":
                        shutil.copy(
                            resource_path("src/media/background.jpg"),
                            "media/Assets/background.jpg",
                        )

            if created:
                Notification().create(
                    caption="LunaStudio | Setup Required",
                    text="Folders created. Please add your model to 'media/model'\nand restart the program.",
                    width=600,
                )
                self._close()
                sys.exit()

            contract = Constract()
            if not contract.check():
                Notification().create(
                    caption="LunaStudio | Setup Required",
                    text="No models found.\nPlease add your model first to 'media/model'\nand restart the program.",
                    width=600,
                )
                self._close()
                sys.exit()
            else:
                contract.start()
                self.config_data = self.config.recv()

            self._init_pygame()
            self._init_live2d()

        except Exception as e:
            self.logger.error(f"[app_init] Failed to initialize app: {e}")
            traceback.print_exc()
            self._close()
            sys.exit()

    def _init_pygame(self):
        point = namedtuple("point", ["x", "y"])
        self.display_size = point(*self.config_data["aplication"]["display"])

        pygame.init()
        pygame.display.set_mode(self.display_size, pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("LunaStudio | By Lunaria & Comunity")

        self.background = Image(self.config_data["aplication"]["background"])
        icon = pygame.image.load(resource_path("src/media/LunaStudio.png"))
        pygame.display.set_icon(icon)

    def _init_live2d(self):
        try:
            live2d.setLogEnable(True)
            live2d.init()
            live2d.glInit()
            self._load_model()
        except Exception as e:
            self.logger.error(f"[_init_live2d] Live2D initialization failed: {e}")
            traceback.print_exc()
            self._close()
            sys.exit()

    def _load_model(self):
        try:
            model_list = self.config_data.get("ModelList", {})
            first_key = next(iter(model_list))
            full_path = Path("media") / model_list[first_key]["FullPath"]

            self.model = live2d.LAppModel()
            self.model.LoadModelJson(str(full_path))
            self.model.Resize(*self.display_size)
            self.model.SetAutoBreathEnable(self.config_data.get("Auto Breath", True))
            self.model.SetAutoBlinkEnable(self.config_data.get("Auto Blink", True))
        except Exception as e:
            self.logger.error(f"[_load_model] Failed to load Live2D model: {e}")
            traceback.print_exc()
            self._close()
            sys.exit()

    def start_capture(self):
        if not self._capture_started:
            try:
                threading.Thread(
                    target=Mediapipe().capture_task,
                    args=(self.params, 10),
                    name="CaptureThread",
                    daemon=True,
                ).start()
                self._capture_started = True
            except Exception as e:
                self.logger.error(f"[start_capture] Failed to start capture task: {e}")
                traceback.print_exc()

    def _update_parameters(self):
        try:
            p, m = self.params, self.model
            p.update_params(p)
            m.SetParameterValue(StandardParams.ParamEyeLOpen, p.EyeLOpen, 1)
            m.SetParameterValue(StandardParams.ParamEyeROpen, p.EyeROpen, 1)
            m.SetParameterValue(StandardParams.ParamMouthOpenY, p.MouthOpenY, 1)
            m.SetParameterValue(StandardParams.ParamMouthForm, p.MouthForm, 1)

            head_params = [
                (StandardParams.ParamAngleX, p.AngleX),
                (StandardParams.ParamAngleY, p.AngleY),
                (StandardParams.ParamAngleZ, p.AngleZ),
                (StandardParams.ParamBodyAngleX, p.AngleX),
                (StandardParams.ParamBodyAngleY, p.AngleY),
                (StandardParams.ParamBodyAngleZ, p.AngleZ),
                (StandardParams.ParamBustX, p.BustX),
                (StandardParams.ParamBustY, p.BustY),
                (StandardParams.ParamBaseX, p.BodyAngleX),
                (StandardParams.ParamBaseY, p.BodyAngleY),
                (StandardParams.ParamEyeBallX, p.EyeBallX),
            ]
            for param, value in head_params:
                m.SetParameterValue(param, value, 1)

            yaw, pitch = p.AngleX, p.AngleY
            m.SetParameterValue("ParamBodyLeft", max(0.0, -yaw / 30), 1)
            m.SetParameterValue("ParamBodyRight", max(0.0, yaw / 30), 1)
            m.SetParameterValue("ParamBodyBack", max(0.0, pitch / 30), 1)
            m.SetParameterValue("ParamBodyFront", max(0.0, -pitch / 30), 1)

            m.SetParameterValue("Param14", 1, 1)
        except Exception as e:
            self.logger.error(f"[_update_parameters] Failed to update parameters: {e}")
            traceback.print_exc()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.logger.info("[_handle_events] Smooth Close....")
                self.running = False

    def _render_frame(self):
        try:
            live2d.clearBuffer()
            self.background.Draw()
            self.model.Update()
            self.model.Draw()
            pygame.display.flip()
        except Exception as e:
            self.logger.error(f"[_render_frame] Failed to render frame: {e}")
            traceback.print_exc()

    def run(self):
        try:
            self.app_init()
            self.start_capture()
            self.running = True
            clock = pygame.time.Clock()

            while self.running:
                self._handle_events()
                self._update_parameters()
                self._render_frame()

                if self.config_data["aplication"]["CapFPS"]["capFps"]:
                    clock.tick(self.config_data["aplication"]["CapFPS"]["CapFpsValue"])
                else:
                    time.sleep(0.005)
        except Exception as e:
            self.logger.error(f"[run] Exception in main loop: {e}")
            traceback.print_exc()
        finally:
            self._close()

    @staticmethod
    def _close():
        try:
            live2d.dispose()
            pygame.quit()
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    app = Live2DApp()
    app.run()
