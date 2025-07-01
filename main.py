import os
import sys
import time
import shutil
import threading
from pathlib import Path
from collections import namedtuple

import pygame
import live2d.v3 as live2d
from live2d.v3.params import StandardParams

from utils import Notification, Constract, Config, Logger, resource_path
from render import Mediapipe, Image, Params


class Live2DApp:
    def __init__(self):
        self.logger = Logger("Live2DApp")
        self.config = Config()
        self.config_data = {}
        self.config_internal = {}
        self.model = None
        self.params = Params()
        self.background = None
        self.display_size = None
        self._capture_started = False
        self.mediapipe = Mediapipe(app=self)
        self.running = False

    def app_init(self):
        try:
            self._setup_directories()
            self._check_contract()
            self.config_data = self.config.user()
            self.config_internal = self.config.recv()
            self._init_pygame()
            self._init_live2d()
        except Exception as e:
            self.logger.LogExit("app_init", e)
            sys.exit()

    def _setup_directories(self):
        folders = ["Media", "Media/Model", "Media/Assets", "Media/Config"]
        copy_files = [
            (resource_path("Assets/config.json"), "Media/Config/config.json"),
            (resource_path("Assets/background.jpg"), "Media/Assets/background.jpg"),
        ]

        created = False
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                created = True

        for src, dst in copy_files:
            shutil.copy(src, dst)

        if created:
            Notification().create(
                caption="LunaStudio | Setup Required",
                text="Folders created. Please add your model to 'Media/Model'\nand restart the program.",
                width=600,
            )
            self._close()
            sys.exit()

    def _check_contract(self):
        contract = Constract()
        if not contract.check():
            Notification().create(
                caption="LunaStudio | Setup Required",
                text="No models found.\nPlease add your model first to 'Media/Model'\nand restart the program.",
                width=600,
            )
            self._close()
            sys.exit()
        contract.start()

    def _init_pygame(self):
        try:
            point = namedtuple("Point", ["x", "y"])
            self.display_size = point(*self.config_data["display"])

            pygame.init()
            pygame.display.set_mode(self.display_size, pygame.DOUBLEBUF | pygame.OPENGL)
            pygame.display.set_caption("LunaStudio | By Lunaria & Community")

            self.background = Image(f"Media/Assets/{self.config_data['background']}")
            icon = pygame.image.load(resource_path("Assets/LunaStudio.png"))
            pygame.display.set_icon(icon)
        except Exception as e:
            self.logger.LogExit("_init_pygame", e)
            sys.exit()

    def _init_live2d(self):
        try:
            live2d.setLogEnable(True)
            live2d.init()
            live2d.glInit()
            self._load_model()
        except Exception as e:
            self.logger.LogExit("_init_live2d", e)
            sys.exit()

    def _load_model(self):
        try:
            model_list = self.config_internal.get("ModelList", {})
            first_model_key = next(iter(model_list))
            full_path = Path("media") / model_list[first_model_key]["FullPath"]

            self.model = live2d.LAppModel()
            self.model.LoadModelJson(str(full_path))
            self.model.Resize(*self.display_size)
            self.model.SetAutoBreathEnable(self.config_data.get("Auto Breath", True))
            self.model.SetAutoBlinkEnable(self.config_data.get("Auto Blink", True))
        except Exception as e:
            self.logger.LogExit("_load_model", e)
            sys.exit()

    def start_capture(self):
        if not self._capture_started:
            try:
                threading.Thread(
                    target=self.mediapipe.capture_task,
                    args=(self.params, 3),
                    name="CaptureThread",
                    daemon=True,
                ).start()
                self._capture_started = True
            except Exception as e:
                self.logger.LogExit("start_capture", e)
                sys.exit()

    def _update_parameters(self):
        try:
            p, m = self.params, self.model
            p.update_params(p)

            # Facial and body params
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

            m.SetParameterValue("Param14", 1, 1)  # Always-on param
        except Exception as e:
            self.logger.LogExit("_update_parameters", e)
            sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _render_frame(self):
        try:
            live2d.clearBuffer()
            self.background.Draw()
            self.model.Update()
            self.model.Draw()
            pygame.display.flip()
        except Exception as e:
            self.logger.LogExit("_render_frame", e)
            sys.exit()

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

                if self.config_data["CapFPS"]["capFps"]:
                    clock.tick(self.config_data["CapFPS"]["CapFpsValue"])
                else:
                    time.sleep(0.005)
        except Exception as e:
            self.logger.LogExit("run", e)
            sys.exit()
        finally:
            self._close()

    @staticmethod
    def _close():
        try:
            live2d.dispose()
            pygame.quit()
        except Exception:
            sys.exit()


if __name__ == "__main__":
    Live2DApp().run()
