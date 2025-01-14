import sys
import datetime
import inspect
import os

class VSCodeLogger:
    COLORS = {
        'INFO': '\033[94m',     # Blue
        'DEBUG': '\033[96m',    # Cyan
        'WARNING': '\033[93m',  # Yellow
        'SUCCESS': '\033[92m',  # Green
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'RESET': '\033[0m'      # Reset color
    }

    def __init__(self, name):
        self.name = name
        self.file_logging = False
        self.log_file = None

    def _gradient_text(self, text):
        gradient = [
            '\033[38;2;128;128;128m', # Medium gray
            '\033[38;2;96;96;96m',    # Medium-dark gray
            '\033[38;2;64;64;64m',    # Dark gray
            '\033[38;2;32;32;32m',    # Very dark gray
            '\033[38;2;0;0;0m',       # Black
        ]
        
        result = ""
        for i, char in enumerate(text):
            color_index = min(i, len(gradient) - 1)
            result += f"{gradient[color_index]}{char}"
        return result + self.COLORS['RESET']

    def _log(self, level, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caller = inspect.currentframe().f_back.f_back
        filename = os.path.basename(caller.f_code.co_filename)
        lineno = caller.f_lineno
        func_name = caller.f_code.co_name

        gradient_time = self._gradient_text(current_time)

        log_message = (
            f"{gradient_time} ~ "
            f"{self.COLORS[level]}{level}{self.COLORS['RESET']} | "
            f"{self.name}:{func_name}:{lineno} - "
            f"{self.COLORS[level]}{message}{self.COLORS['RESET']}"
        )
        
        print(log_message, file=sys.stderr)

        if self.file_logging:
            file_message = f"{current_time},{self.name},{level},{func_name}:{lineno},{message}\n"
            self.log_file.write(file_message)
            self.log_file.flush()

    def configure_file_logging(self, filename, filemode='a'):
        """
        Configure file logging for the logger.
        
        :param filename: The name of the log file
        :param filemode: The mode to open the file (default is 'a' for append)
        """
        self.file_logging = True
        self.log_file = open(filename, filemode)

    def close_file_logging(self):
        """
        Close the file logging if it's active.
        """
        if self.file_logging and self.log_file:
            self.log_file.close()
            self.file_logging = False
            self.log_file = None

    def info(self, message):
        self._log('INFO', message)

    def debug(self, message):
        self._log('DEBUG', message)

    def warning(self, message):
        self._log('WARNING', message)

    def success(self, message):
        self._log('SUCCESS', message)

    def error(self, message):
        self._log('ERROR', message)

    def critical(self, message):
        self._log('CRITICAL', message)

def get_logger(name):
    return VSCodeLogger(name)