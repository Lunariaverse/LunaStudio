from src import Notification, resource_path, Constract, Image
from collections import namedtuple
import pygame, shutil, sys, os, gc
import live2d.v3 as live2d


class AppSetup:
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
            self.running = False
            sys.exit(1)

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
            self.running = False

    def _check_contract(self):
        contract = Constract()
        if not contract.check():
            Notification().create(
                caption="LunaStudio | Setup Required",
                text="No models found.\nPlease add your model first to 'Media/Model'\nand restart the program.",
                width=600,
            )
            self.running = False
        contract.start()

    def _init_pygame(self):
        point = namedtuple("Point", ["x", "y"])
        self.display_size = point(*self.config_data["display"])
        pygame.init()
        self.screen = pygame.display.set_mode(
            self.display_size, pygame.DOUBLEBUF | pygame.OPENGL
        )
        pygame.display.set_caption("LunaStudio | By Lunaria & Community")
        self.background = Image(f"Media/Assets/{self.config_data['background']}")
        icon = pygame.image.load(resource_path("Assets/LunaStudio.png"))
        pygame.display.set_icon(icon)

    def _init_live2d(self):
        live2d.setLogEnable(self.debugL2D)
        live2d.init()
        live2d.glInit()
        self._load_model()
        gc.collect()
