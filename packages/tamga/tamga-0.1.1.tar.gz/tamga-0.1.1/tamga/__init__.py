"""
Tamga - A beautiful and customizable logger for Python web applications.
"""

import threading
from typing import Dict, Optional

from tamga.utils import (
    mkdir,
    exists,
    currentTime,
    currentDate,
    currentTimeZone,
    LogBuffer,
    LogRotator,
    colorize,
)
from tamga.config import Config, DEFAULT_CONFIG

class Log:
    """A beautiful and customizable logger for Python web applications."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the logger."""
        self.config = config or DEFAULT_CONFIG
        self._lock = threading.Lock()
        self._buffers: Dict[str, LogBuffer] = {}
        self._rotators: Dict[str, LogRotator] = {}
        
        if not exists(self.config.LOG_FOLDER_ROOT):
            mkdir(self.config.LOG_FOLDER_ROOT)
        
        # Initialize buffers and rotators for each log file
        log_files = [
            self.config.LOG_FILE_ROOT,
            self.config.LOG_DANGER_FILE_ROOT,
            self.config.LOG_SUCCESS_FILE_ROOT,
            self.config.LOG_WARNING_FILE_ROOT,
            self.config.LOG_INFO_FILE_ROOT,
            self.config.LOG_APP_FILE_ROOT,
            self.config.LOG_SQL_FILE_ROOT,
        ]
        
        for file_path in log_files:
            self._buffers[file_path] = LogBuffer(file_path)
            self._rotators[file_path] = LogRotator(
                file_path,
                self.config.MAX_FILE_SIZE,
                self.config.BACKUP_COUNT
            )

    def _format_header(self) -> str:
        """Format the log header with app name, date, time, and timezone."""
        if not self.config.ENABLE_COLORS:
            return (
                f"{self.config.APP_NAME}@{self.config.APP_VERSION}"
                f"[{currentDate(self.config.DATE_FORMAT)}"
                f"|{currentTime(seconds=True, time_format=self.config.TIME_FORMAT)}"
                f"|{currentTimeZone()}]"
            )
        
        return (
            f"{colorize(f'{self.config.APP_NAME}@{self.config.APP_VERSION}', fg=self.config.COLORS['app_name']['fg'])}"
            f"{colorize('[', fg=self.config.COLORS['brackets']['fg'])}"
            f"{colorize(currentDate(self.config.DATE_FORMAT), fg=self.config.COLORS['date']['fg'])}"
            f"{colorize('|', fg=self.config.COLORS['brackets']['fg'])}"
            f"{colorize(currentTime(seconds=True, time_format=self.config.TIME_FORMAT), fg=self.config.COLORS['time']['fg'])}"
            f"{colorize('|', fg=self.config.COLORS['brackets']['fg'])}"
            f"{colorize(currentTimeZone(), fg=self.config.COLORS['timezone']['fg'])}"
            f"{colorize(']', fg=self.config.COLORS['brackets']['fg'])}"
        )

    def _write_log(self, log_type: str, message: str, file_path: str) -> None:
        """Write log message to console and file."""
        with self._lock:
            # Check if we need to rotate the log file
            rotator = self._rotators[file_path]
            if rotator.should_rotate():
                rotator.rotate()

            # Format the log message
            timestamp = (
                f"[{currentDate(self.config.DATE_FORMAT)}"
                f"|{currentTime(seconds=True, microSeconds=True, time_format=self.config.TIME_FORMAT)}"
                f"|{currentTimeZone()}]"
            )
            
            # Write to console if enabled
            if self.config.ENABLE_CONSOLE:
                header = self._format_header()
                if self.config.ENABLE_COLORS:
                    log_colors = self.config.COLORS[log_type.lower()]
                    type_text = colorize(f" {log_type.upper()} ", fg=log_colors["fg"], bg=log_colors["bg"], bold=True)
                    message_text = colorize(f" {message}", fg=log_colors["text"])
                    print(f"{header} {type_text}{message_text}")
                else:
                    print(f"{header} [{log_type.upper()}] {message}")

            # Write to files if enabled
            if self.config.ENABLE_FILE_LOGGING:
                # Write to main log file
                main_log_msg = f"{timestamp}\t{log_type.upper()} | {message}\n"
                self._buffers[self.config.LOG_FILE_ROOT].write(main_log_msg)
                
                # Write to specific log file
                specific_log_msg = f"{timestamp}\t{message}\n"
                self._buffers[file_path].write(specific_log_msg)

    def danger(self, message: str = "NONE") -> None:
        """Log a danger message."""
        self._write_log("danger", message, self.config.LOG_DANGER_FILE_ROOT)

    def success(self, message: str = "NONE") -> None:
        """Log a success message."""
        self._write_log("success", message, self.config.LOG_SUCCESS_FILE_ROOT)

    def warning(self, message: str = "NONE") -> None:
        """Log a warning message."""
        self._write_log("warning", message, self.config.LOG_WARNING_FILE_ROOT)

    def info(self, message: str = "NONE") -> None:
        """Log an info message."""
        self._write_log("info", message, self.config.LOG_INFO_FILE_ROOT)

    def app(self, message: str = "NONE") -> None:
        """Log an app message."""
        self._write_log("app", message, self.config.LOG_APP_FILE_ROOT)

    def sql(self, message: str = "NONE") -> None:
        """Log a SQL message."""
        self._write_log("sql", message, self.config.LOG_SQL_FILE_ROOT)

    def breaker(self) -> None:
        """Print a breaker line."""
        if self.config.ENABLE_CONSOLE:
            if self.config.ENABLE_COLORS:
                print(colorize(self.config.BREAKER_TEXT, fg=self.config.COLORS["breaker"]["fg"]))
            else:
                print(self.config.BREAKER_TEXT)
        
        if self.config.ENABLE_FILE_LOGGING:
            self._buffers[self.config.LOG_FILE_ROOT].write(self.config.BREAKER_TEXT + "\n")

    def __enter__(self):
        """Context manager enter."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close all log buffers."""
        for buffer in self._buffers.values():
            buffer.close() 