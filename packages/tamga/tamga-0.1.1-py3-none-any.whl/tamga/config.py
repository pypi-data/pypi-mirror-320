"""Configuration variables for Tamga logger."""
import os
from typing import Dict, Optional

class Config:
    """Configuration class for Tamga logger."""
    
    def __init__(
        self,
        app_name: str = "Tamga",
        app_version: str = "0.1.0",
        log_dir: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        enable_console: bool = True,
        enable_file_logging: bool = True,
        log_level: str = "INFO",
        date_format: str = "%Y-%m-%d",
        time_format: str = "%H:%M:%S",
        enable_colors: bool = True,
        breaker_text: str = "-" * 100,
    ):
        """Initialize configuration."""
        self.APP_NAME = app_name
        self.APP_VERSION = app_version
        self.ENABLE_CONSOLE = enable_console
        self.ENABLE_FILE_LOGGING = enable_file_logging
        self.LOG_LEVEL = log_level
        self.DATE_FORMAT = date_format
        self.TIME_FORMAT = time_format
        self.ENABLE_COLORS = enable_colors
        self.BREAKER_TEXT = breaker_text
        self.MAX_FILE_SIZE = max_file_size
        self.BACKUP_COUNT = backup_count

        # Set log directory
        self.LOG_FOLDER_ROOT = log_dir or os.path.join(os.getcwd(), "logs")
        self.LOG_FILE_ROOT = os.path.join(self.LOG_FOLDER_ROOT, "all.log")
        self.LOG_DANGER_FILE_ROOT = os.path.join(self.LOG_FOLDER_ROOT, "danger.log")
        self.LOG_SUCCESS_FILE_ROOT = os.path.join(self.LOG_FOLDER_ROOT, "success.log")
        self.LOG_WARNING_FILE_ROOT = os.path.join(self.LOG_FOLDER_ROOT, "warning.log")
        self.LOG_INFO_FILE_ROOT = os.path.join(self.LOG_FOLDER_ROOT, "info.log")
        self.LOG_APP_FILE_ROOT = os.path.join(self.LOG_FOLDER_ROOT, "app.log")
        self.LOG_SQL_FILE_ROOT = os.path.join(self.LOG_FOLDER_ROOT, "sql.log")

        # ANSI color codes
        self.COLORS: Dict[str, Dict[str, str]] = {
            "app_name": {"fg": "38;2;244;63;94"},
            "brackets": {"fg": "38;2;115;115;115"},
            "date": {"fg": "38;2;217;70;239"},
            "time": {"fg": "38;2;236;72;153"},
            "timezone": {"fg": "38;2;168;85;247"},
            "danger": {
                "fg": "38;2;220;38;38",
                "bg": "48;2;248;113;113",
                "text": "38;2;239;68;68",
            },
            "success": {
                "fg": "38;2;22;163;74",
                "bg": "48;2;74;222;128",
                "text": "38;2;34;197;94",
            },
            "warning": {
                "fg": "38;2;234;88;12",
                "bg": "48;2;251;146;60",
                "text": "38;2;249;115;22",
            },
            "info": {
                "fg": "38;2;37;99;235",
                "bg": "48;2;96;165;250",
                "text": "38;2;59;130;246",
            },
            "app": {
                "fg": "38;2;8;145;178",
                "bg": "48;2;32;211;238",
                "text": "38;2;6;182;212",
            },
            "sql": {
                "fg": "38;2;13;148;136",
                "bg": "48;2;45;212;191",
                "text": "38;2;20;184;166",
            },
            "breaker": {"fg": "38;2;115;155;155"},
        }

# Default configuration
DEFAULT_CONFIG = Config() 