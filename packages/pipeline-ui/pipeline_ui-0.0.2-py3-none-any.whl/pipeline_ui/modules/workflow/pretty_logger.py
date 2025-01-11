import logging
from io import StringIO
from devtools import debug

class PrettyLogger:
    def __init__(self, name='pretty_logger', level=logging.DEBUG, format_str='%(message)s'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(level)
            formatter = logging.Formatter(format_str)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug_obj(self, obj, msg=''):
        if self.logger.level == logging.DEBUG:
            string_buffer = StringIO()
            debug(obj, file=string_buffer)
            pretty_output = string_buffer.getvalue()
            string_buffer.close()

            if msg:
                self.logger.debug(f"{msg}\n{pretty_output}")
            else:
                self.logger.debug(pretty_output)

    def debug(self, msg, *args):
        self.logger.debug(msg, *args)
