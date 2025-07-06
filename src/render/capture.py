from .loader import Loader
from .landmarker import LandmarkerManager
from .parameter import ParameterManager
from cv2_enumerate_cameras import enumerate_cameras as ec
from ..utils import Logger, resource_path
from typing import TYPE_CHECKING
import cv2
import numpy as np
import mediapipe as mp
import threading
import time

if TYPE_CHECKING:
    from .module.param import Params


class Capture(Loader, LandmarkerManager, ParameterManager):
    def __init__(self, app):
        self.app = app
        self.logger = Logger("Capture")
        self.lock = threading.Lock()
        self.LandmarkerManager = LandmarkerManager(app=app)
        self.ParameterManager = ParameterManager(app=app)
        self.loader = Loader(app=app)

    def start_capture(self, params: "Params" = None):

        try:
            data = self.jsonloader()
            if not data:
                self.logger.LogExit(
                    "start_capture",
                    "Failed to read parameter.json, did you delate it?",
                    custom=True,
                )
                self.app.running = False

            model_path = resource_path("src/render/model/face_landmarker.task")
            options = self.load_model_options(model_path)
            if not options:
                self.logger.LogExit(
                    "start_capture",
                    "Failed to Open Model, I dont know where",
                    custom=True,
                )
                self.app.running = False

            threading.Thread(target=self.load_landmarker_task, args=(options,)).start()

            cap = self.open_camera()
            if cap is None:
                self.logger.LogExit(
                    "start_capture", "Failed to Detect Camera.", custom=True
                )
                self.app.running = False

            landmarker = self.wait_until_ready()

            while self.app.running:
                ret, frame = cap.read()
                if not ret:
                    self.logger.LogExit(
                        "start_capture", "Failed to read frame", custom=True
                    )
                    self.app.running = False
                    break

                frame = cv2.flip(frame, 1)
                np_frame = np.array(frame)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_frame)

                results = landmarker.detect_for_video(mp_image, int(time.time() * 1000))

                if results and results.face_landmarks:
                    landmarks = results.face_landmarks[0]
                    values = self.process_tracking_values(landmarks, data)
                    if values and params:
                        self.update_params(params, values, data)

                time.sleep(0.01)

        except Exception as e:
            self.logger.LogExit("start_capture", e)
            self.app.running = False
        finally:
            if cap:
                cap.release()
