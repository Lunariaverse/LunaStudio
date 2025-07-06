from .module.calculation import Calculation
from .module.math import *


class ParameterManager:
    def __init__(self, app):
        self.app = app

    def get_landmark_values(self, landmarks, indices):
        return [(landmarks[i].x, landmarks[i].y) for i in indices]

    def get_head_values(self, landmarks, indices):
        return [(landmarks[i].x, landmarks[i].y, landmarks[i].z) for i in indices]

    def process_tracking_values(self, landmarks, data):
        try:
            self.calculation = Calculation()
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
            self.app.running = False
            return None

    def update_params(self, params, values, data):
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
            self.app.running = False
