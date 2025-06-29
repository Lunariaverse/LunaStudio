from .math import euclideanDistance
from ..utils.log import setup_logger
import numpy as np


class Calculation:
    def __init__(self):
        self.logger = setup_logger("Calculation")

    def calculate_eye_openness(self, points):
        """
        Calculate eye openness ratio.
        :param points: list of 6 facial landmarks [(x1, y1), ..., (x6, y6)]
        :return: vertical-to-horizontal eye aspect ratio (EAR)
        """
        try:
            vertical = (
                euclideanDistance(points[1], points[5])
                + euclideanDistance(points[2], points[4])
            ) / 2
            horizontal = euclideanDistance(points[0], points[3])
            return vertical / horizontal if horizontal != 0 else 0.0
        except Exception as e:
            self.logger.error(f"[calculate_eye_openness] failed: {e}")
            return 0.0

    def calculate_mouth_openness(self, points):
        """
        Calculate mouth openness using same EAR-like formula.
        """
        return self.calculate_eye_openness(points)

    def calculate_mouth_form(self, points):
        """
        Calculate mouth width (distance between mouth corners).
        :param points: list of two points [(x1, y1), (x2, y2)]
        :return: distance as float
        """
        try:
            return euclideanDistance(points[0], points[1])
        except Exception as e:
            self.logger.error(f"[calculate_mouth_openness] failed: {e}")
            return 0.0

    def calculate_head_pose(self, points):
        """
        Calculate head rotation angles: roll, yaw, pitch.
        :param points: list of 9 points:
            [left eye left, left eye right, right eye left, right eye right,
            nose, face left, face right, face center top, face center bottom]
        :return: (roll_angle, yaw_angle, pitch_angle) in degrees
        """
        try:
            # Eye centers
            left_eye_center = (
                (points[0][0] + points[1][0]) / 2,
                (points[0][1] + points[1][1]) / 2,
            )
            right_eye_center = (
                (points[2][0] + points[3][0]) / 2,
                (points[2][1] + points[3][1]) / 2,
            )

            # Roll (tilt left/right)
            delta_y = right_eye_center[1] - left_eye_center[1]
            delta_x = right_eye_center[0] - left_eye_center[0]
            roll_angle = (
                np.degrees(np.arctan(delta_y / delta_x)) if delta_x != 0 else 0.0
            )

            # Yaw (turn left/right)
            nose_x = points[4][0]
            face_left_x = points[5][0]
            face_right_x = points[6][0]
            perp_left = abs(nose_x - face_left_x)
            perp_right = abs(face_right_x - nose_x)
            denominator = perp_right + perp_left
            yaw_angle = (
                np.degrees(np.arcsin((perp_right - perp_left) / denominator))
                if denominator != 0
                else 0.0
            )

            # Pitch (nod up/down)
            face_center_top = points[7]
            face_center_bottom = points[8]
            delta_y = face_center_top[1] - face_center_bottom[1]
            delta_z = face_center_bottom[2] - face_center_top[2]
            pitch_angle = (
                np.degrees(np.arctan(delta_z / delta_y)) if delta_y != 0 else 0.0
            )

            return roll_angle, yaw_angle, pitch_angle

        except Exception as e:
            self.logger.error(f"[calculate_head_pose] failed: {e}")
            return 0.0, 0.0, 0.0

    def calculate_body_angle_x(self, body_center_x, left_shoulder, right_shoulder):
        """
        Calculate body rotation angle (yaw) based on shoulder positions.
        :param body_center_x: float, center x coordinate
        :param left_shoulder, right_shoulder: objects with .x attribute
        :return: angle in degrees
        """
        try:
            perp_left = abs(left_shoulder.x - body_center_x)
            perp_right = abs(right_shoulder.x - body_center_x)
            denominator = perp_right + perp_left
            return (
                np.degrees(np.arcsin((perp_right - perp_left) / denominator))
                if denominator != 0
                else 0.0
            )
        except Exception as e:
            self.logger.error(f"[calculate_body_angle_x] failed: {e}")
            return 0.0

    def calculate_eye_ball_x(self, points):
        """
        Calculate horizontal iris movement: average of left and right eyeball X.
        :param points: list of 6 points:
            [left iris, left eye inner corner, left eye outer corner,
            right iris, right eye inner corner, right eye outer corner]
        :return: float in roughly range (-1, 1)
        """
        try:
            # Left eye
            left_center_x = (points[2][0] + points[1][0]) / 2
            denominator_left = points[2][0] - points[1][0]
            left_eye_ball_x = (
                ((points[0][0] - left_center_x) / denominator_left * 2)
                if denominator_left != 0
                else 0.0
            )

            # Right eye
            right_center_x = (points[5][0] + points[4][0]) / 2
            denominator_right = points[5][0] - points[4][0]
            right_eye_ball_x = (
                ((points[3][0] - right_center_x) / denominator_right * 2)
                if denominator_right != 0
                else 0.0
            )

            return (left_eye_ball_x + right_eye_ball_x) / 2
        except Exception as e:
            self.logger.error(f"[calculate_eye_ball_x]  failed: {e}")
            return 0.0
