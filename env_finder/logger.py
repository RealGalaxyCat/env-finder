import sys
from colorama import Fore, Style
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


COLORS = {
    logging.DEBUG:    Fore.CYAN,
    logging.INFO:     Fore.GREEN,
    logging.WARNING:  Fore.YELLOW,
    logging.ERROR:    Fore.RED,
    logging.CRITICAL: Fore.MAGENTA,
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)




def setup_logger(root_level, filename: str):
    root = logging.getLogger()
    root.setLevel(root_level)

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # handlers
    sh = StreamHandler(sys.stdout)
    sh.setFormatter(ColorFormatter(fmt))

    fh = RotatingFileHandler(
        f"/app/logs/{filename}",
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    fh.setFormatter(logging.Formatter(fmt))


    root.addHandler(sh)
    root.addHandler(fh)