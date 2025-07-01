from logging.handlers import RotatingFileHandler
import traceback, logging


class Logger:
    _formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _file_handler = RotatingFileHandler(
        "LunaStudio.log", maxBytes=5_000_000, backupCount=3
    )
    _file_handler.setFormatter(_formatter)
    _console_handler = logging.StreamHandler()
    _console_handler.setFormatter(_formatter)

    def __init__(self, HandlerName: str):
        self.logging = self.setup_logger(HandlerName)

    def LogExit(self, context: str, e, custom: bool = False):
        if custom:
            tb_str = str(e)
        else:
            tb_str = traceback.format_exc()
        self.logging.error(
            "[%s] Exception: %s\n%s",
            context,
            e,
            f"==============================================================\nmore Information:\n{tb_str}\n==============================================================",
        )

    @classmethod
    def setup_logger(cls, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        if not logger.handlers:
            logger.addHandler(cls._console_handler)
            logger.addHandler(cls._file_handler)
        return logger
