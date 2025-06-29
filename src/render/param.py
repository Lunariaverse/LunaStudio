class Params:
    """
    Facial tracking parameters with smoothing:
    - Supports exponential or linear smoothing
    - Bust smoothing (separate factor)
    - Calibration for narrow eye opening range
    """

    PARAMETER_KEYS = [
        "EyeLOpen",
        "EyeROpen",
        "MouthOpenY",
        "MouthForm",
        "AngleX",
        "AngleY",
        "AngleZ",
        "BodyAngleX",
        "BodyAngleY",
        "BodyAngleZ",
        "EyeBallX",
        "BustX",
        "BustY",
    ]

    def __init__(
        self,
        smooth_factor: float = 0.5,
        linear_steps: int = 0,
        bust_smooth: float = 0.7,
        eye_open_min: float = 0.05,
        eye_open_max: float = 0.8,
    ):
        """
        Initialize Params object with smoothing and calibration settings.
        """
        for key in self.PARAMETER_KEYS:
            setattr(self, key, 1.0 if key in ("EyeLOpen", "EyeROpen") else 0.0)

        self.prev = {k: getattr(self, k) for k in self.PARAMETER_KEYS}
        self.smooth_factor = smooth_factor
        self.linear_steps = linear_steps
        self.bust_smooth = bust_smooth
        self.eye_open_min = eye_open_min
        self.eye_open_max = eye_open_max
        self._linear_counters = {k: 0 for k in self.PARAMETER_KEYS}
        self._linear_deltas = {k: 0.0 for k in self.PARAMETER_KEYS}

    @staticmethod
    def _clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
        """
        Clamp a value to the range [lo, hi].
        """
        return max(lo, min(hi, val))

    def smooth_exp(self, target: float, prev: float, factor: float) -> float:
        """
        Apply exponential smoothing: blends previous value with target.
        """
        return prev * factor + target * (1 - factor)

    def start_linear(self, key: str, target: float) -> None:
        """
        Initialize a linear transition for a parameter.

        :param key: Parameter name.
        :param target: Target value.
        """
        if self.linear_steps > 0 and hasattr(self, key):
            current = getattr(self, key)
            delta = (target - current) / self.linear_steps
            self._linear_deltas[key] = delta
            self._linear_counters[key] = self.linear_steps

    def smooth_linear(self, key: str) -> bool:
        """
        Perform one step of linear smoothing.

        :param key: Parameter name.
        :return: True if still smoothing, False if complete.
        """
        if self._linear_counters.get(key, 0) > 0:
            current = getattr(self, key)
            new_val = current + self._linear_deltas.get(key, 0.0)
            setattr(self, key, new_val)
            self._linear_counters[key] -= 1
            return True
        return False

    def update_params(self, new_params: "Params", mode: str = "exp") -> None:
        """
        Update all parameters, applying smoothing.

        :param new_params: Another Params instance containing new target values.
        :param mode: Smoothing mode ('exp' for exponential, 'linear' for linear).
        """
        for key in self.PARAMETER_KEYS:
            if key == "BustX":
                target = getattr(self, "AngleX")
                factor = self.bust_smooth
            elif key == "BustY":
                target = getattr(self, "AngleY")
                factor = self.bust_smooth
            else:
                target = getattr(new_params, key, 0.0)
                factor = self.smooth_factor
                if key in ("EyeLOpen", "EyeROpen"):
                    mapped = (target - self.eye_open_min) / (
                        self.eye_open_max - self.eye_open_min
                    )
                    target = self._clamp(mapped)

            if mode == "linear":
                if target != self.prev.get(key, 0.0):
                    self.start_linear(key, target)
                if not self.smooth_linear(key):
                    setattr(self, key, target)
            else:
                new_val = self.smooth_exp(target, self.prev.get(key, 0.0), factor)
                setattr(self, key, new_val)
            self.prev[key] = getattr(self, key)
