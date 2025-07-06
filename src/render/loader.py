# loader.py
from ..utils import Logger, resource_path
import json, cv2
from cv2_enumerate_cameras import enumerate_cameras as ec


class Loader:

    def __init__(self, app):
        self.app = app
        self.logger = Logger("Loader")

    def jsonloader(self):
        try:
            with open(resource_path("config/parameter.json"), "rb") as file:
                return json.load(file)
        except Exception as e:
            self.logger.LogExit("jsonloader", e)
            self.app.running = False

    def open_camera(self):
        try:
            for cam in ec(cv2.CAP_MSMF):
                cap = cv2.VideoCapture(cam.index)
                if cap.isOpened():
                    return cap
            self.app.running = False
        except Exception as e:
            self.logger.LogExit("open_camera", e)
            self.app.running = False
