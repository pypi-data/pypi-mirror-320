import logging
from datetime import datetime
import inspect
from logging.handlers import RotatingFileHandler


class Logger:
    """
    A singleton logger class to handle logging across the application.
    """
    _instance = None  # Singleton instance

    def __new__(cls, log_file_prefix: str = "bigquery_notebook_logs"):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(log_file_prefix)
        return cls._instance

    def _initialize(self, log_file_prefix: str):
        """
        Initializes the logger with a file handler and stream handler.

        Args:
            log_file_prefix (str): Prefix for the log file name.
        """
        today_string = datetime.today().strftime('%Y_%m_%d')
        self.log_file_path = f"{log_file_prefix}_{today_string}.log"
    
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)  # Capture all log levels
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Rotating file handler to limit file size
        file_handler = RotatingFileHandler(
            self.log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)  # Write all logs to the file
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Print INFO and higher logs to the console
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message: str):
        """Logs an info-level message."""
        self.logger.info(message)

    def error(self, message: str):
        """Logs an error-level message."""
        self.logger.error(message)

    def warning(self, message: str):
        """Logs a warning-level message."""
        self.logger.warning(message)

    def debug(self, message: str):
        """Logs a debug-level message."""
        self.logger.debug(message)

    def critical(self, message: str):
        """Logs a critical-level message."""
        self.logger.critical(message)

    def log_form_parameters(self):
        """
        Dynamically identifies and logs all form parameters defined using # @param.
        """
        self.logger.info("========== FORM PARAMETERS ==========")

        # Get the current frame and extract all variables
        current_frame = inspect.currentframe()
        variables = current_frame.f_back.f_locals  # Get variables from the caller's frame

        # Use regex to extract # @param variables
        import re
        source_code = inspect.getsource(current_frame.f_back)
        param_pattern = r"(\w+)\s*=\s*.*#\s*@param"
        param_matches = re.findall(param_pattern, source_code)

        # Log only variables defined with # @param
        for param in param_matches:
            if param in variables:
                self.logger.info(f"{param}: {variables[param]}")

        self.logger.info("=====================================")

    def get_log_file_path(self) -> str:
        """
        Returns the path to the current log file.

        Returns:
            str: The path of the current log file.
        """
        return self.log_file_path
