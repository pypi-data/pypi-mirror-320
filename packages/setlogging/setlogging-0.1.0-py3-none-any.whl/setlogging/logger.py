# Standard library imports
from datetime import datetime, timezone as dt_timezone
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional, Union


class TimezoneFormatter(logging.Formatter):
    """
    Custom formatter to include timezone-aware timestamps in log messages.

    Args:
        fmt: The format string for the log message
        datefmt: The format string for the timestamp
        timezone: Optional specific timezone to use (defaults to local)

    Example:
        formatter = TimezoneFormatter(
            fmt='%(asctime)s [%(timezone)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        timezone: Optional[dt_timezone] = None
    ) -> None:
        super().__init__(fmt, datefmt)
        self.local_timezone = timezone or datetime.now().astimezone().tzinfo

    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        try:
            local_dt = datetime.fromtimestamp(
                record.created, self.local_timezone)
            if datefmt:
                return local_dt.strftime(datefmt)
            else:
                return local_dt.isoformat()
        except Exception as e:
            raise RuntimeError(f"Failed to format time: {str(e)}") from e

    def format(self, record: logging.LogRecord) -> str:
        # Add timezone name to log record
        record.timezone = str(self.local_timezone)
        return super().format(record)


def setup_logging(
    log_level: int = logging.DEBUG,
    log_file: Optional[str] = None,
    max_size_mb: int = 25,  # 25MB
    backup_count: int = 7,
    console_output: bool = True,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    json_format: bool = False,
    indent: Optional[int] = None
) -> logging.Logger:
    """
    Configure logging system with rotating file handler and optional console output.

    Args:
        log_level: Logging level (default: DEBUG)
        log_file: Log file path (default: application.log or application_log.json if json_format is True)
        max_size_mb: Max log file size in MB before rotation (default: 25MB)
        backup_count: Number of backup files to keep (default: 7)
        console_output: Enable console logging (default: True)
        log_format: Custom log format string (optional)
        date_format: Custom date format string (optional)
        json_format: Flag to determine if log format should be JSON (default: False)
        indent: Indentation level for JSON output (default: None)
    """
    try:
        # Parameter validation
        if max_size_mb <= 0:
            raise ValueError("max_size_mb must be positive")
        if backup_count < 0:
            raise ValueError("backup_count must be non-negative")
        if indent is not None and not json_format:
            raise ValueError(
                "indent parameter is only valid when json_format is True")

        # Convert max_size_mb to bytes
        max_bytes = max_size_mb * 1024 * 1024

        # Set default log file based on json_format
        if log_file is None:
            log_file = "application_log.json" if json_format else "application.log"

        # Create log directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create logger
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        # Clear existing handlers
        logger.handlers = []

        # Set up formatter
        if json_format:
            formatter = logging.Formatter(json.dumps({
                "time": "%(asctime)s",
                "name": "%(name)s",
                "level": "%(levelname)s",
                "message": "%(message)s"
            }, indent=indent))
        else:
            formatter = TimezoneFormatter(
                fmt=log_format or '%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s',
                datefmt=date_format or '%Y-%m-%d %H:%M:%S %z'
            )

        # Set up file handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Set up console handler if enabled
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # Log configuration details
        processID = os.getpid()
        logger.info(f"""
===============================
    Logging Configuration
===============================
Level        : {logging.getLevelName(log_level)}
Log File     : {file_handler.baseFilename}
Max File Size: {max_size_mb:.2f} MB
Backup Count : {backup_count}
Console Out  : {console_output}
Timezone     : {datetime.now().astimezone().tzinfo}
ProcessID    : {processID}
===============================
""")

        return logger

    except Exception as e:
        raise RuntimeError(f"Failed to setup logging: {str(e)}") from e


def get_logger(
    name: str = __name__,
    log_level: int = logging.DEBUG,
    log_file: Optional[str] = None,
    max_size_mb: int = 25,  # 25MB
    backup_count: int = 7,
    console_output: bool = True,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    json_format: bool = False,
    indent: Optional[int] = None
) -> logging.Logger:
    """
    Simplified function to set up logging and return a logger instance.

    Args:
        name: Name of the logger.
        log_level: Logging level.
        log_file: Log file name.
        max_size_mb: Max size of log file in MB before rotation.
        backup_count: Number of rotated backups to keep.
        console_output: Enable console logging (default: True)
        log_format: Custom log format string (optional)
        date_format: Custom date format string (optional)
        json_format: Flag to determine if log format should be JSON.
        indent: Indentation level for JSON output.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return setup_logging(
        log_level=log_level,
        log_file=log_file,
        max_size_mb=max_size_mb,  # Pass max_size_mb parameter
        backup_count=backup_count,
        console_output=console_output,
        log_format=log_format,
        date_format=date_format,
        json_format=json_format,
        indent=indent
    )


# Example Usage
if __name__ == "__main__":
    try:
        logger = get_logger(console_output=True)
        logger.info("Basic usage example")

        # JSON format example
        json_logger = get_logger(json_format=True, indent=2)
        json_logger.info("JSON format example")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
