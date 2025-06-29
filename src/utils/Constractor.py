from .config import Config, resource_path
from .log import setup_logger
from pathlib import Path
import json
import traceback


class Constract:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger("Constact")
        self.dir = "media"

    def start(self):
        """
        Initialize assets and model data.
        """
        try:
            self.assets()
            self.model3Json()

            data = self.config.recv()
            model_list = data.get("ModelList", {})
            if model_list:
                first_model = next(iter(model_list.values()))
                expressions = first_model.get("extensions", {}).get("expressions", [])
                if expressions:
                    self.prepareModel3Json(expressions)
        except Exception as e:
            print(f"[ERROR] start() failed: {e}")
            traceback.print_exc()

    def check(self):
        """
        Check if at least one *.model3.json exists under media/model
        """
        model_path = Path(self.dir) / "model"
        return (
            any(model_path.glob("**/*.model3.json")) if model_path.is_dir() else False
        )

    def assets(self):
        """
        Scan media/Assets folder for image files and update config["assets"]
        """
        try:
            assets_folder = Path(self.dir) / "Assets"
            assets = []

            if assets_folder.exists():
                for file in assets_folder.rglob("*"):
                    if file.is_file() and file.suffix.lower() in {
                        ".jpg",
                        ".jpeg",
                        ".png",
                    }:
                        assets.append(file.relative_to(self.dir).as_posix())
            else:
                self.logger.warning(
                    f"[assets] Assets folder not found: {assets_folder}"
                )
            self.config.update(new_data=assets, key="assets")

        except Exception as e:
            self.logger.error(f"[assets] Trying Read Assets File, failed: {e}")

            traceback.print_exc()

    def prepareModel3Json(self, expressions_list: list):
        """
        Ensure model3.json includes given expression files under FileReferences.Expressions
        """
        try:
            config_data = self.config.recv()
            model_list = config_data.get("ModelList", {})
            if not model_list:
                self.logger.warning("[prepareModel3Json] No ModelList in config")
                return

            key = next(iter(model_list))
            full_path = model_list[key].get("FullPath")
            if not full_path:
                self.logger.warning(
                    f"[prepareModel3Json] No FullPath for model '{key}'"
                )
                return

            json_path = Path(self.dir) / full_path
            if not json_path.is_file():
                self.logger.warning(
                    f"[prepareModel3Json] Model3 JSON not found: {json_path}"
                )

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
            self.logger.error(
                f"[prepareModel3Json] Fail Prepareing .model.json, failed: {e}"
            )
            traceback.print_exc()

    def model3Json(self):
        """
        Scan media/model, rebuild ModelList in config with related files.
        """
        try:
            model_path = Path(self.dir) / "model"
            if not model_path.is_dir():
                self.logger.warning(
                    f"[model3Json] Model folder not found: {model_path}"
                )
                return False

            new_model_list = {}

            for json_file in model_path.glob("**/*.model3.json"):
                model_name = json_file.parent.name
                new_model_list[model_name] = {
                    "FullPath": json_file.relative_to(self.dir).as_posix(),
                    "model3": json_file.name,
                    "extensions": self.find_related_files(json_file.parent),
                }

            cfg_path = resource_path("src/config/usercfg.json")
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["ModelList"] = new_model_list

            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True

        except Exception as e:
            self.logger.error(f"[model3Json] model3Json() failed: {e}")
            traceback.print_exc()
            return False

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
            self.logger.error(f"[find_related_files] failed in {folder}: {e}")
            traceback.print_exc()

        return {"expressions": expressions, "motions": motions}
