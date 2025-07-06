from live2d.v3.params import StandardParams
from live2d.v3 import LAppModel
from pathlib import Path


class ModelMixin:
    def _load_model(self):
        try:
            model_list = self.config_internal.get("ModelList", {})
            first_model_key = next(iter(model_list))
            full_path = Path("media") / model_list[first_model_key]["FullPath"]

            self.model = LAppModel()
            self.model.LoadModelJson(str(full_path))
            self.model.Resize(*self.display_size)
            self.model.SetAutoBreathEnable(self.config_data.get("Auto Breath", True))
            self.model.SetAutoBlinkEnable(self.config_data.get("Auto Blink", True))
        except Exception as e:
            self.logger.LogExit("_load_model", e)
            self.running = False

    def _update_parameters(self):
        try:
            p, m = self.params, self.model
            p.update_params(p)

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

            m.SetParameterValue("Param14", 1, 1)
        except Exception as e:
            self.logger.LogExit("_update_parameters", e)
            self.running = False
