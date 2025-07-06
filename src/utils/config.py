import os, threading, json, sys
from .log import Logger


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Config:
    """
    Config handler for usercfg.json and parameter.json.
    """

    def __init__(self):
        self.logger = Logger("Config")
        self._lock = threading.Lock()

    def user(self):
        """Load user config safely."""
        try:
            with open("Media/Config/config.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as e:
            self.logger.LogExit("recv", e)
            raise
        except Exception as e:
            self.logger.LogExit("recv", e)
            raise

    def recv(self):
        """Load user config internal safely."""
        try:
            with open(
                resource_path("config/usercfg.json"), "r", encoding="utf-8"
            ) as file:
                return json.load(file)
        except FileNotFoundError as e:
            self.logger.LogExit("recv", e)
            raise
        except Exception as e:
            self.logger.LogExit("recv", e)
            raise

    def update(self, new_data, key):
        """
        Update data[key] with new_data (dict merge).
        Creates key if it doesn't exist.
        """
        with self._lock:
            try:
                path = resource_path("config/usercfg.json")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                else:
                    data = {}

                if isinstance(data.get(key), dict) and isinstance(new_data, dict):
                    data[key].update(new_data)
                else:
                    data[key] = new_data

                with open(path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4)

            except Exception as e:
                self.logger.LogExit("update", e)
                raise

    def updateParameter(self, new_data):
        """Update parameter.json (top-level merge)."""
        with self._lock:
            try:
                path = resource_path("config/parameter.json")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                else:
                    data = {}

                if isinstance(new_data, dict):
                    data.update(new_data)
                else:
                    return

                with open(path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4)

            except Exception as e:
                self.logger.LogExit("updateParameter", e)
                raise
