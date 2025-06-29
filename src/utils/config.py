from .log import setup_logger
import traceback
import threading
import json
import sys
import os


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
        self.logger = setup_logger("Config")
        self._lock = threading.Lock()

    def recv(self):
        """Load user config safely."""
        try:
            with open(
                resource_path("src/config/usercfg.json"), "r", encoding="utf-8"
            ) as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.error(f"[recv] File Not Found")
            return
        except Exception as e:
            self.logger.error(f"[recv] Failed to load usercfg.json: {e}")
            traceback.print_exc()
            return

    def update(self, new_data, key):
        """
        Update data[key] with new_data (dict merge).
        Creates key if it doesn't exist.
        """
        with self._lock:
            try:
                path = resource_path("src/config/usercfg.json")
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
                self.logger.error(f"[update] Failed to update usercfg.json: {e}")
                traceback.print_exc()

    def recvParameter(self):
        """Load parameter config safely."""
        try:
            with open(
                resource_path("src/config/parameter.json"), "r", encoding="utf-8"
            ) as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.error("[recvParameter] parameter.json not found")
            return
        except Exception as e:
            self.logger.error(f"[recvParameter] Failed to load parameter.json: {e}")
            traceback.print_exc()
            return

    def updateParameter(self, new_data):
        """Update parameter.json (top-level merge)."""
        with self._lock:
            try:
                path = resource_path("src/config/parameter.json")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                else:
                    data = {}

                if isinstance(new_data, dict):
                    data.update(new_data)
                else:
                    self.logger.warning(
                        "[updateParameter] new_data is not a dict, skipping update."
                    )
                    return

                with open(path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4)

            except Exception as e:
                self.logger.error(
                    f"[updateParameter] Failed to update parameter.json: {e}"
                )
                traceback.print_exc()
