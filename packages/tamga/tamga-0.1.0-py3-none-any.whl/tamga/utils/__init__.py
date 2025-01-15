"""Utility functions for Tamga logger."""
import os
import threading
from datetime import datetime
from typing import Optional, TextIO
import pytz

class LogBuffer:
    """Thread-safe buffer for log messages."""
    
    def __init__(self, file_path: str, max_buffer: int = 1024):
        """Initialize buffer."""
        self.file_path = file_path
        self.max_buffer = max_buffer
        self.buffer = []
        self.lock = threading.Lock()
        self._file: Optional[TextIO] = None

    def write(self, message: str) -> None:
        """Write message to buffer and flush if needed."""
        with self.lock:
            self.buffer.append(message)
            if len(self.buffer) >= self.max_buffer:
                self.flush()

    def flush(self) -> None:
        """Flush buffer to file."""
        if not self.buffer:
            return

        with self.lock:
            if not self._file or self._file.closed:
                self._file = open(self.file_path, "a", encoding="utf-8")
            
            self._file.write("".join(self.buffer))
            self._file.flush()
            self.buffer.clear()

    def close(self) -> None:
        """Close file and flush buffer."""
        with self.lock:
            if self.buffer:
                self.flush()
            if self._file and not self._file.closed:
                self._file.close()

class LogRotator:
    """Handle log file rotation."""
    
    def __init__(self, file_path: str, max_bytes: int, backup_count: int):
        """Initialize rotator."""
        self.file_path = file_path
        self.max_bytes = max_bytes
        self.backup_count = backup_count

    def should_rotate(self) -> bool:
        """Check if log file should be rotated."""
        try:
            return os.path.getsize(self.file_path) >= self.max_bytes
        except OSError:
            return False

    def rotate(self) -> None:
        """Rotate log files."""
        if not os.path.exists(self.file_path):
            return

        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.file_path}.{i}"
            dst = f"{self.file_path}.{i + 1}"
            
            if os.path.exists(src):
                os.rename(src, dst)
        
        if os.path.exists(self.file_path):
            os.rename(self.file_path, f"{self.file_path}.1")

def mkdir(path: str) -> None:
    """Create a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def exists(path: str) -> bool:
    """Check if a path exists."""
    return os.path.exists(path)

def currentTime(seconds: bool = False, microSeconds: bool = False, time_format: Optional[str] = None) -> str:
    """Get current time in specified format."""
    if time_format:
        return datetime.now().strftime(time_format)
    
    format_str = "%H:%M"
    if seconds:
        format_str += ":%S"
    if microSeconds:
        format_str += ".%f"
    return datetime.now().strftime(format_str)

def currentDate(date_format: str = "%Y-%m-%d") -> str:
    """Get current date in specified format."""
    return datetime.now().strftime(date_format)

def currentTimeZone() -> str:
    """Get current timezone."""
    return str(datetime.now(pytz.timezone('UTC')).astimezone().tzinfo)

def colorize(text: str, fg: Optional[str] = None, bg: Optional[str] = None, bold: bool = False) -> str:
    """Colorize text with ANSI escape codes."""
    parts = []
    
    if fg:
        parts.append(f"\033[{fg}m")
    if bg:
        parts.append(f"\033[{bg}m")
    if bold:
        parts.append("\033[1m")
    
    parts.append(text)
    parts.append("\033[0m" * len([p for p in parts if p.startswith("\033[")]))
    
    return "".join(parts) 