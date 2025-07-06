# landmarker.py
from ..utils import Logger
import mediapipe as mp
import time


class LandmarkerManager:
    def __init__(self, app):
        self.app = app
        self.logger = Logger("Landmarker")
        self.landmarker = None

    def load_model_options(self, model_path):
        try:
            BaseOptions = mp.tasks.BaseOptions
            FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
            VisionRunningMode = mp.tasks.vision.RunningMode

            return FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=VisionRunningMode.VIDEO,
                num_faces=1,
            )
        except Exception as e:
            self.logger.LogExit("load_model_options", e)
            self.app.running = False

    def create_face_landmarker(self, options):
        try:
            FaceLandmarker = mp.tasks.vision.FaceLandmarker
            return FaceLandmarker.create_from_options(options)
        except Exception as e:
            self.logger.LogExit("create_face_landmarker", e)
            self.app.running = False

    def load_landmarker_task(self, options):
        try:
            landmarker = self.create_face_landmarker(options)
            with self.lock:
                self.landmarker = landmarker
        except Exception as e:
            self.logger.LogExit("load_landmarker_task", e)
            self.app.running = False

    def wait_until_ready(self):
        while True:
            with self.lock:
                if self.landmarker:
                    return self.landmarker
            time.sleep(0.1)
