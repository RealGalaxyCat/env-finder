import sys
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler



def setup_logger(root_level, filename: str):
    root = logging.getLogger()
    root.setLevel(root_level)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    sh = StreamHandler(sys.stdout)
    fh = RotatingFileHandler(
        f"/app/logs/{filename}",
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )

    sh.setFormatter(formatter)
    fh.setFormatter(formatter)

    root.addHandler(sh)
    root.addHandler(fh)