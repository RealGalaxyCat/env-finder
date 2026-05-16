import sys
import copy
import datetime
from colorama import Fore, Style, Back
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


SECRET = 25  # between INFO (20) and WARNING (30)
logging.addLevelName(SECRET, "SECRET")


COLORS = {
    logging.DEBUG:    Fore.CYAN,
    logging.INFO:     Back.CYAN + Fore.BLACK,
    SECRET:           Back.YELLOW + Fore.WHITE,
    logging.WARNING:  Fore.YELLOW,
    logging.ERROR:    Back.RED + Fore.WHITE,
    logging.CRITICAL: Fore.MAGENTA,
}


class AppLogger(logging.Logger):
    def secret(self, message, *args, **kwargs):
        if self.isEnabledFor(SECRET):
            self._log(SECRET, message, args, **kwargs)


# use CustomLogger for all new loggers
logging.setLoggerClass(AppLogger)



# ~~~~~~~~~~ # Formatters # ~~~~~~~~~~ #

UTC_PLUS_2 = datetime.timezone(datetime.timedelta(hours=2))

def utc2_time(*args):
    return datetime.datetime.now(UTC_PLUS_2).timetuple()


class PlainFormatter(logging.Formatter):
    converter = utc2_time


class ColorFormatter(logging.Formatter):
    converter = utc2_time

    def format(self, record):
        record = copy.copy(record)
        color = COLORS.get(record.levelno, "")
        padded = record.levelname.ljust(8)  # pad first, then colorize
        record.levelname = f"{color}{padded}{Style.RESET_ALL}"
        return super().format(record)




def setup_logger(root_level, filename: str):
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    root = logging.getLogger()
    root.setLevel(root_level)

    fmt_file = "[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s"
    fmt_console = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"

    # handlers
    sh = StreamHandler(sys.stdout)
    sh.setFormatter(ColorFormatter(fmt_console))

    fh = RotatingFileHandler(
        f"/app/logs/{filename}",
        mode="a",
        maxBytes=5 * 1024 * 1024,  # 5mb
        backupCount=3
    )
    fh.setFormatter(PlainFormatter(fmt_file))
    fh.setLevel(SECRET)  # SECRET, WARNING, ERROR, CRITICAL

    root.addHandler(sh)
    root.addHandler(fh)


# getter, only exists for type hinting
def getLogger(name: str) -> AppLogger:
    return logging.getLogger(name)

