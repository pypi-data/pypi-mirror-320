# Standard Library
import ctypes
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

# Third party
from django.conf import settings
from django.utils.timezone import get_default_timezone


# Fix Logging_folder place (local and alwaysdata)
if settings.DEBUG:
    LOGGING_FOLDER = "/tmp/log/kapt-travel/"
else:
    LOGGING_FOLDER = "%s/admin/logs/kapt-travel/" % os.environ["HOME"]

# Verify if folder exist
if not os.path.isdir(LOGGING_FOLDER):
    os.makedirs(LOGGING_FOLDER)

# The default timezone to consider during date operations
DEFAULT_TZ = get_default_timezone()


class ScriptError(Exception):
    def __init__(self, msg, obj):
        self.msg = msg
        self.object = obj

    def __str__(self):
        if self.object is not None:
            return (
                str(self.object.__class__.__name__)
                + " n "
                + str(self.object.id)
                + " : "
                + self.msg
            )
        else:
            return self.msg


class ColorizingStreamHandler(logging.StreamHandler):
    # color names to indices
    color_map = {
        "black": 0,
        "red": 1,
        "green": 2,
        "yellow": 3,
        "blue": 4,
        "magenta": 5,
        "cyan": 6,
        "white": 7,
    }

    # levels to (background, foreground, bold/intense)
    if os.name == "nt":
        level_map = {
            logging.DEBUG: (None, "blue", True),
            logging.INFO: (None, "white", False),
            logging.WARNING: (None, "yellow", True),
            logging.ERROR: (None, "red", True),
            logging.CRITICAL: ("red", "white", True),
        }
    else:
        level_map = {
            logging.DEBUG: (None, "blue", False),
            logging.INFO: (None, "green", False),
            logging.WARNING: (None, "yellow", False),
            logging.ERROR: (None, "red", False),
            logging.CRITICAL: ("red", "white", True),
        }
    csi = "\x1b["
    reset = "\x1b[0m"

    @property
    def is_tty(self):
        isatty = getattr(self.stream, "isatty", None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, "terminator", "\n"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    if os.name != "nt":

        def output_colorized(self, message):
            self.stream.write(message)

    else:
        import re

        ansi_esc = re.compile(r"\x1b\[((?:\d+)(?:;(?:\d+))*)m")

        nt_color_map = {
            0: 0x00,  # black
            1: 0x04,  # red
            2: 0x02,  # green
            3: 0x06,  # yellow
            4: 0x01,  # blue
            5: 0x05,  # magenta
            6: 0x03,  # cyan
            7: 0x07,  # white
        }

        def output_colorized(self, message):
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, "fileno", None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2):  # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(";")]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08  # foreground intensity on
                            elif p == 0:  # reset to default color
                                color = 0x07
                            else:
                                pass  # error condition ignored
                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append("1")
            if params:
                message = "".join(
                    (self.csi, ";".join(params), "m", message, self.reset)
                )
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            parts = message.split("\n", 1)
            parts[0] = self.colorize(parts[0], record)
            message = "\n".join(parts)
        return message


# set up logging to file with rotation every day from 00:00 - Backup for 30 days
logFileHandler = TimedRotatingFileHandler(
    filename=LOGGING_FOLDER + "import_kapt_apidae.log", when="midnight", backupCount=30
)
logFileHandler.setLevel(logging.INFO)
logFormatter = logging.Formatter(
    "%(asctime)s %(name)-12s: %(levelname)-8s %(message)s", datefmt="%d/%m/%y %H:%M:%S"
)
logFileHandler.setFormatter(logFormatter)
logger = logging.getLogger(__name__)
logger.addHandler(logFileHandler)


# set up logging to stdout with colors
ttyHandler = ColorizingStreamHandler()
ttyHandler.setFormatter(logFormatter)
ttyHandler.setLevel(logging.INFO)
logger.addHandler(ttyHandler)

# set up level of logger to the minimum its handler
logger.setLevel(logging.INFO)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)


def print_progress(iteration, total, prefix="", suffix="", decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = "*" * filled_length + "-" * (bar_length - filled_length)
    sys.stdout.write("\r{} |{}| {}{} {}".format(prefix, bar, percents, "%", suffix)),
    if iteration == total:
        space = " " * (bar_length + 50)
        sys.stdout.write("\r{} ✔ {}\n".format(prefix, space))
    sys.stdout.flush()
