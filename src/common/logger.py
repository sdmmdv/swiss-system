import logging
import os
import sys
import inspect
from pathlib import Path

def get_logger(name: str = None) -> logging.Logger:
    """
    Return a configured logger instance.
    Format: [HH:MM:SS] [script-name] LEVEL: message
    Automatically uses the calling script's filename, even if run as __main__.
    """
    if name is None or name == "__main__":
        # Get the filename of the module that called get_logger()
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        if module and hasattr(module, "__file__"):
            name = Path(module.__file__).stem
        else:
            name = Path(sys.argv[0]).stem or "app"

    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S"
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
