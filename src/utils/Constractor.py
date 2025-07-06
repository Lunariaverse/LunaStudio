from .config import Config, resource_path
from .log import Logger
from pathlib import Path
import json


class Constract:
    def __init__(self):
        self.config = Config()
        self.logger = Logger("Constact")
        self.dir = "media"

    def start(self):
        """
        Initialize assets and model data.
        """
        try:
            self.model3Json()

            data = self.config.recv()
            model_list = data.get("ModelList", {})
            if model_list:
                first_model = next(iter(model_list.values()))
                expressions = first_model.get("extensions", {}).get("expressions", [])
                if expressions:
                    self.prepareModel3Json(expressions)
        except Exception as e:
            self.logger.LogExit("start", e)
            raise

    def check(self):
        """
        Check if at least one *.model3.json exists under media/model
        """
        model_path = Path(self.dir) / "model"
        return (
            any(model_path.glob("**/*.model3.json")) if model_path.is_dir() else False
        )

    def prepareModel3Json(self, expressions_list: list):
        """
        Ensure model3.json includes given expression files under FileReferences.Expressions
        """
        try:
            config_data = self.config.recv()
            model_list = config_data.get("ModelList", {})
            if not model_list:
                return

            key = next(iter(model_list))
            full_path = model_list[key].get("FullPath")
            if not full_path:
                return

            json_path = Path(self.dir) / full_path
            if not json_path.is_file():
                return

            with json_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            file_refs = data.setdefault("FileReferences", {})
            expressions = file_refs.setdefault("Expressions", [])
            existing_names = {expr.get("Name") for expr in expressions}

            new_entries = []
            for filepath in expressions_list:
                if filepath.endswith(".exp3.json"):
                    name = Path(filepath).stem.replace(".exp3", "")
                    if name not in existing_names:
                        new_entries.append({"Name": name, "File": filepath})
                        existing_names.add(name)

            if new_entries:
                expressions.extend(new_entries)
                with json_path.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            self.logger.LogExit("prepareModel3Json", e)
            raise

    def model3Json(self):
        """
        Scan media/model, rebuild ModelList in config with related files.
        """
        try:
            model_path = Path(self.dir) / "model"
            if not model_path.is_dir():
                return False

            new_model_list = {}

            for json_file in model_path.glob("**/*.model3.json"):
                model_name = json_file.parent.name
                new_model_list[model_name] = {
                    "FullPath": json_file.relative_to(self.dir).as_posix(),
                    "model3": json_file.name,
                    "extensions": self.find_related_files(json_file.parent),
                }

            cfg_path = resource_path("config/usercfg.json")
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["ModelList"] = new_model_list

            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True

        except Exception as e:
            self.logger.LogExit("model3Json", e)
            raise

    def find_related_files(self, folder: Path):
        """
        Find related expression and motion files in model folder.
        """
        expressions, motions = [], []
        try:
            for file in folder.glob("**/*"):
                if file.is_file():
                    if file.suffixes == [".exp3", ".json"]:
                        expressions.append(file.relative_to(folder).as_posix())
                    elif file.suffixes == [".motion3", ".json"]:
                        motions.append(file.relative_to(folder).as_posix())
        except Exception as e:
            self.logger.LogExit("find_related_files", e)
            raise
        return {"expressions": expressions, "motions": motions}
