from utils import Logger, resource_path
from cv2_enumerate_cameras import enumerate_cameras as ec
from .calculation import Calculation
from .math import *
from typing import TYPE_CHECKING
import json
import threading
import cv2
import time
import mediapipe as mp
import numpy as np

if TYPE_CHECKING:
    from .param import Params

landmarker = None


class Mediapipe:
    def __init__(self, app):
        self.app = app
        self.logger = Logger("Mediapipe")
        self.calculation = Calculation()
        self.running = True

    def jsonloader(self):
        try:
            with open(resource_path("config/parameter.json"), "rb") as file:
                return json.load(file)
        except Exception as e:
            self.logger.LogExit("jsonloader", e)
            self.running = self.app.running = False
            return None

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
            self.running = self.app.running = False
            return None

    def create_face_landmarker(self, options):
        try:
            FaceLandmarker = mp.tasks.vision.FaceLandmarker
            return FaceLandmarker.create_from_options(options)
        except Exception as e:
            self.logger.LogExit("create_face_landmarker", e)
            self.running = self.app.running = False
            return None

    def load_landmarker_task(self, options):
        global landmarker
        landmarker = self.create_face_landmarker(options)

    def open_camera(self):
        try:
            for cam in ec(cv2.CAP_MSMF):
                cap = cv2.VideoCapture(cam.index)
                if cap.isOpened():
                    return cap
            return None
        except Exception as e:
            self.logger.LogExit("open_camera", e)
            return None

    def get_landmark_values(self, landmarks, indices):
        return [(landmarks[i].x, landmarks[i].y) for i in indices]

    def get_head_values(self, landmarks, indices):
        return [(landmarks[i].x, landmarks[i].y, landmarks[i].z) for i in indices]

    def process_tracking_values(self, landmarks, data):
        try:
            left_eye = self.get_landmark_values(landmarks, data["LEFT_EYE"])
            right_eye = self.get_landmark_values(landmarks, data["RIGHT_EYE"])
            mouth = self.get_landmark_values(landmarks, data["LIP"])
            mouth_corners = self.get_landmark_values(landmarks, data["LIP_CORNER"])
            iris = self.get_landmark_values(
                landmarks, data["LEFT_EYE_BALL"] + data["RIGHT_EYE_BALL"]
            )
            head = self.get_head_values(landmarks, data["HEAD"])

            return {
                "lEyeOpenRatio": self.calculation.calculate_eye_openness(left_eye),
                "rEyeOpenRatio": self.calculation.calculate_eye_openness(right_eye),
                "mouthOpenRatio": self.calculation.calculate_mouth_openness(mouth),
                "mouthForm": self.calculation.calculate_mouth_form(mouth_corners),
                "roll": self.calculation.calculate_head_pose(head)[0],
                "yaw": self.calculation.calculate_head_pose(head)[1],
                "pitch": self.calculation.calculate_head_pose(head)[2],
                "eyeBallX": self.calculation.calculate_eye_ball_x(iris),
            }
        except Exception as e:
            self.logger.LogExit("process_tracking_values", e)
            self.running = self.app.running = False
            return None

    def update_params(self, params: "Params", values: dict, data):
        try:
            params.EyeLOpen = round(
                linearScale01(
                    values["lEyeOpenRatio"],
                    data["EYE_OPENNESS_MIN"],
                    data["EYE_OPENNESS_MAX"],
                ),
                1,
            )
            params.EyeROpen = round(
                linearScale01(
                    values["rEyeOpenRatio"],
                    data["EYE_OPENNESS_MIN"],
                    data["EYE_OPENNESS_MAX"],
                ),
                1,
            )
            params.MouthOpenY = round(
                linearScale01(
                    values["mouthOpenRatio"],
                    data["MOUTH_OPENNESS_MIN"],
                    data["MOUTH_OPENNESS_MAX"],
                ),
                1,
            )
            params.MouthForm = linearScale01(values["mouthForm"], 0.08, 0.14)
            params.AngleX = clipValue(values["yaw"], -30, 30)
            params.AngleY = clipValue(values["pitch"], -30, 30)
            params.AngleZ = clipValue(values["roll"], -30, 30)
            params.EyeBallX = linearScale_11(values["eyeBallX"], -0.18, 0.18)
        except Exception as e:
            self.logger.LogExit("update_params", e)
            self.running = self.app.running = False

    def capture_task(self, params: "Params" = None, max_devices=3):
        global landmarker
        cap = None

        try:
            data = self.jsonloader()
            if not data:
                return

            model_path = resource_path("render/face_landmarker.task")
            options = self.load_model_options(model_path)
            if not options:
                return

            threading.Thread(target=self.load_landmarker_task, args=(options,)).start()

            cap = self.open_camera()
            if cap is None:
                self.logger.LogExit(
                    "capture_task",
                    "Failed to Detect Camera. Is it plugged in? Try unplugging and replugging.",
                    custom=True,
                )
                self.running = self.app.running = False
                return

            while landmarker is None:
                time.sleep(0.1)

            while self.running and self.app.running:
                ret, frame = cap.read()
                if not ret:
                    self.logger.LogExit("capture_task")
                    self.running = self.app.running = False
                    return

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
            self.logger.LogExit("capture_task", e)
            self.running = self.app.running = False
        finally:
            if cap:
                cap.release()
