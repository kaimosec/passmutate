import logging
import datetime


class LogFormatter(logging.Formatter):
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    reset = '\x1b[0m'

    def __init__(self):
        super().__init__()
        self.colors = {
            logging.INFO: self.blue,
            logging.WARNING: self.yellow,
            logging.ERROR: self.red
        }

    def format(self, record):
        now = datetime.datetime.now()
        if record.levelno in self.colors:
            start_color = self.colors[record.levelno]
            end_color = self.reset
        else:
            start_color = ''
            end_color = ''

        fmt = "[{}] {}%(levelname)s{}: %(message)s".format(
            now.strftime("%x %H:%M"),
            start_color,
            end_color
        )
        formatter = logging.Formatter(fmt)
        return formatter.format(record)
