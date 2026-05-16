import sys
from colorama import Fore, Style, Back
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


SECRET = 25  # between INFO (20) and WARNING (30)
logging.addLevelName(SECRET, "SECRET")


COLORS = {
    logging.DEBUG:    Fore.CYAN,
    logging.INFO:     Fore.GREEN,
    SECRET:           Back.YELLOW + Fore.WHITE,
    logging.WARNING:  Fore.YELLOW,
    logging.ERROR:    Fore.RED,
    logging.CRITICAL: Fore.MAGENTA,
}


class AppLogger(logging.Logger):
    def secret(self, message, *args, **kwargs):
        if self.isEnabledFor(SECRET):
            self._log(SECRET, message, args, **kwargs)


# use CustomLogger for all new loggers
logging.setLoggerClass(AppLogger)



class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)




def setup_logger(root_level, filename: str):
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    root = logging.getLogger()
    root.setLevel(root_level)

    fmt = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"

    # handlers
    sh = StreamHandler(sys.stdout)
    sh.setFormatter(ColorFormatter(fmt))

    fh = RotatingFileHandler(
        f"/app/logs/{filename}",
        mode="a",
        maxBytes=5 * 1024 * 1024,  # 5mb
        backupCount=3
    )
    fh.setFormatter(logging.Formatter(fmt))
    fh.setLevel(SECRET)  # SECRET, WARNING, ERROR, CRITICAL

    root.addHandler(sh)
    root.addHandler(fh)


# getter, only exists for type hinting
def getLogger(name: str) -> AppLogger:
    return logging.getLogger(name)

