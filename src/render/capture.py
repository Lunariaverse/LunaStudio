from ..utils.config import resource_path
from ..utils.log import setup_logger
from typing import TYPE_CHECKING
from .calculation import Calculation
import mediapipe as mp
from .math import *
import numpy as np
import traceback
import threading
import cv2
import time
import json

if TYPE_CHECKING:
    from .param import Params


# Global landmarker shared with thread
landmarker = None


class Mediapipe:
    def __init__(self):
        self.logging = setup_logger("Mediapipe")
        self.calculation = Calculation()

    def jsonloader(self):
        try:
            with open(resource_path("src/config/parameter.json"), "rb") as file:
                return json.load(file)
        except Exception as e:
            self.logging.error(f"[jsonloader] Failed to load JSON config: {e}")
            traceback.print_exc()
            return {}

    def load_model_options(self, model_path):
        try:
            BaseOptions = mp.tasks.BaseOptions
            VisionRunningMode = mp.tasks.vision.RunningMode
            FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
            return FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=VisionRunningMode.VIDEO,
                num_faces=1,
            )
        except Exception as e:
            self.logging.error(
                f"[load_model_options] Failed to create FaceLandmarkerOptions: {e}"
            )
            traceback.print_exc()
            return None

    def create_face_landmarker(self, options):
        try:
            FaceLandmarker = mp.tasks.vision.FaceLandmarker
            return FaceLandmarker.create_from_options(options)
        except Exception as e:
            self.logging.error(
                f"[create_face_landmarker] Failed to create FaceLandmarker: {e}"
            )
            traceback.print_exc()
            return None

    def load_landmarker_task(self, options):
        global landmarker
        landmarker = self.create_face_landmarker(options)

    def open_camera(self, prefer_index=0, fallback_max=3):
        cap = cv2.VideoCapture(prefer_index)
        if cap.isOpened():
            return cap

        self.logging.warning(
            "[open_camera] Default index failed, trying fallback indices..."
        )
        for device_index in range(1, fallback_max):
            cap = cv2.VideoCapture(device_index)
            if cap.isOpened():
                return cap
        return None

    def get_landmark_values(self, landmarks, indices):
        return [(landmarks[i].x, landmarks[i].y) for i in indices]

    def get_head_values(self, landmarks, indices):
        return [(landmarks[i].x, landmarks[i].y, landmarks[i].z) for i in indices]

    def process_tracking_values(self, landmarks, Data):
        try:
            leftEyePoints = self.get_landmark_values(landmarks, Data["LEFT_EYE"])
            rightEyePoints = self.get_landmark_values(landmarks, Data["RIGHT_EYE"])
            mouthPoints = self.get_landmark_values(landmarks, Data["LIP"])
            mouthCorners = self.get_landmark_values(landmarks, Data["LIP_CORNER"])
            irisPoints = self.get_landmark_values(
                landmarks, Data["LEFT_EYE_BALL"] + Data["RIGHT_EYE_BALL"]
            )
            headPoints = self.get_head_values(landmarks, Data["HEAD"])

            return {
                "lEyeOpenRatio": self.calculation.calculate_eye_openness(leftEyePoints),
                "rEyeOpenRatio": self.calculation.calculate_eye_openness(
                    rightEyePoints
                ),
                "mouthOpenRatio": self.calculation.calculate_mouth_openness(
                    mouthPoints
                ),
                "mouthForm": self.calculation.calculate_mouth_form(mouthCorners),
                "roll": self.calculation.calculate_head_pose(headPoints)[0],
                "yaw": self.calculation.calculate_head_pose(headPoints)[1],
                "pitch": self.calculation.calculate_head_pose(headPoints)[2],
                "eyeBallX": self.calculation.calculate_eye_ball_x(irisPoints),
            }
        except Exception as e:
            self.logging.error(
                f"[process_tracking_values] Failed to process tracking values: {e}"
            )
            traceback.print_exc()
            return {}

    def update_params(self, params: "Params", values: dict, Data):
        try:
            params.EyeLOpen = round(
                linearScale01(
                    values["lEyeOpenRatio"],
                    Data["EYE_OPENNESS_MIN"],
                    Data["EYE_OPENNESS_MAX"],
                ),
                1,
            )
            params.EyeROpen = round(
                linearScale01(
                    values["rEyeOpenRatio"],
                    Data["EYE_OPENNESS_MIN"],
                    Data["EYE_OPENNESS_MAX"],
                ),
                1,
            )
            params.MouthOpenY = round(
                linearScale01(
                    values["mouthOpenRatio"],
                    Data["MOUTH_OPENNESS_MIN"],
                    Data["MOUTH_OPENNESS_MAX"],
                ),
                1,
            )
            params.MouthForm = linearScale01(values["mouthForm"], 0.08, 0.14)
            params.AngleX = clipValue(values["yaw"], -30, 30)
            params.AngleY = clipValue(values["pitch"], -30, 30)
            params.AngleZ = clipValue(values["roll"], -30, 30)
            params.EyeBallX = linearScale_11(values["eyeBallX"], -0.18, 0.18)
        except Exception as e:
            self.logging.error(f"[update_params] Failed to update params: {e}")
            traceback.print_exc()

    def capture_task(self, params: "Params" = None, max_devices=3):
        global landmarker
        start_time = time.time()
        Data = self.jsonloader()

        model_path = resource_path("src/render/face_landmarker.task")
        options = self.load_model_options(model_path)
        if not options:
            self.logging.error("[capture_task] Model options invalid. Task cancelled.")
            return

        # Start background thread to load landmarker
        loader_thread = threading.Thread(
            target=self.load_landmarker_task, args=(options,)
        )
        loader_thread.start()

        cap = self.open_camera(0, max_devices)
        if cap is None:
            self.logging.error("[capture_task] Could not open webcam.")
            return

        while landmarker is None:
            time.sleep(0.1)

        self.logging.info(
            f"[capture_task] Setup complete in {round(time.time() - start_time, 2)} seconds."
        )

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    self.logging.error(
                        "[capture_task] Failed to read frame from camera.",
                        exc_info=True,
                    )
                    break

                frame = cv2.flip(frame, 1)
                np_frame = np.array(frame)

                try:
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_frame)
                    results = landmarker.detect_for_video(
                        mp_image, int(time.time() * 1000)
                    )

                    if results and results.face_landmarks:
                        landmarks = results.face_landmarks[0]
                        values = self.process_tracking_values(landmarks, Data)
                        if params and values:
                            self.update_params(params, values, Data)

                except Exception as e:
                    self.logging.error(f"[capture_task] Failed to process frame: {e}")
                    traceback.print_exc()
                time.sleep(0.01)

        except Exception as e:
            self.logging.error(
                f"[capture_task] Error in capture loop: {e}", exc_info=True
            )
            traceback.print_exc()
        finally:
            if cap:
                cap.release()
