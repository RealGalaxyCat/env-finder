import sys
from colorama import Fore, Style, Back
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


SECRET_FOUND = 25  # between INFO (20) and WARNING (30)
logging.addLevelName(SECRET_FOUND, "SECRET_FOUND")


COLORS = {
    logging.DEBUG:    Fore.CYAN,
    logging.INFO:     Fore.GREEN,
    SECRET_FOUND:     Back.YELLOW + Fore.WHITE,
    logging.WARNING:  Fore.YELLOW,
    logging.ERROR:    Fore.RED,
    logging.CRITICAL: Fore.MAGENTA,
}


class AppLogger(logging.Logger):
    def secret(self, message, *args, **kwargs):
        if self.isEnabledFor(SECRET_FOUND):
            self._log(SECRET_FOUND, message, args, **kwargs)


# use CustomLogger for all new loggers
logging.setLoggerClass(AppLogger)



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
        maxBytes=5 * 1024 * 1024,  # 5mb
        backupCount=3
    )
    fh.setFormatter(logging.Formatter(fmt))


    root.addHandler(sh)
    root.addHandler(fh)


# getter, only exists for type hinting
def getLogger(name: str) -> AppLogger:
    return logging.getLogger(name)

