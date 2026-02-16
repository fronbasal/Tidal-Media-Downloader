#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Simple logging replacement for Printf class.
Uses standard Python logging with colored console output.
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(
    logging.Formatter
):
    """Custom formatter with colors for different log levels."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[34m",  # Blue
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "SUCCESS": "\033[32m",  # Green
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        # Add color to the level name
        level_color = self.COLORS.get(
            record.levelname,
            self.COLORS["RESET"],
        )
        reset_color = self.COLORS[
            "RESET"
        ]

        # Create colored level prefix
        if record.levelname == "INFO":
            prefix = f"{level_color}[INFO]{reset_color}"
        elif (
            record.levelname == "ERROR"
        ):
            prefix = f"{level_color}[ERR]{reset_color}"
        elif (
            hasattr(record, "success")
            and record.success
        ):
            prefix = f"{self.COLORS['SUCCESS']}[SUCCESS]{reset_color}"
        else:
            prefix = f"{level_color}[{record.levelname}]{reset_color}"

        # Format the message
        return f"{prefix} {record.getMessage()}"


# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logger(
    name: str = "tidal-dl",
    level: int = logging.INFO,
    verbose: bool = False,
) -> logging.Logger:
    """Set up the global logger with colored console output."""
    global _logger

    if _logger is not None:
        return _logger

    # Set level based on verbose flag
    if verbose:
        level = logging.DEBUG

    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    # Remove any existing handlers
    _logger.handlers.clear()

    # Create console handler
    console_handler = (
        logging.StreamHandler(
            sys.stdout
        )
    )
    console_handler.setLevel(level)

    # Set custom formatter
    formatter = ColoredFormatter()
    console_handler.setFormatter(
        formatter
    )

    # Add handler to logger
    _logger.addHandler(console_handler)

    # Prevent propagation to root logger
    _logger.propagate = False

    return _logger


def get_logger() -> logging.Logger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def configure_logging(
    verbose: bool = False,
) -> None:
    """Configure logging level based on verbose flag."""
    global _logger
    # Force re-initialization of logger
    _logger = None
    setup_logger(verbose=verbose)


# Convenience functions that match Printf interface
def info(message: str) -> None:
    """Log an info message."""
    get_logger().info(message)


def error(message: str) -> None:
    """Log an error message."""
    get_logger().error(message)


def success(message: str) -> None:
    """Log a success message."""
    logger = get_logger()
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        "",
        0,
        message,
        (),
        None,
    )
    record.success = True
    logger.handle(record)


def debug(message: str) -> None:
    """Log a debug message."""
    get_logger().debug(message)


def warning(message: str) -> None:
    """Log a warning message."""
    get_logger().warning(message)


def logo() -> None:
    """Display the application logo."""
    VERSION = "2025.12.1"
    logo_text = f"""
::::::::::: ::::::::::: :::::::::      :::     :::                     :::::::::  :::        
    :+:         :+:     :+:    :+:   :+: :+:   :+:                     :+:    :+: :+:        
    +:+         +:+     +:+    +:+  +:+   +:+  +:+                     +:+    +:+ +:+        
    +#+         +#+     +#+    +:+ +#++:++#++: +#+       +#++:++#++:++ +#+    +:+ +#+        
    +#+         +#+     +#+    +#+ +#+     +#+ +#+                     +#+    +#+ +#+        
    #+#         #+#     #+#    #+# #+#     #+# #+#                     #+#    #+# #+#        
    ###     ########### #########  ###     ### ##########              #########  ########## 
    
        tidal-dl:  v{VERSION} - A simple Tidal media downloader
        og author: Yaronzz (Yaron Huang)
        repo:      https://github.com/fronbasal/Tidal-Media-Downloader
        fork of:   https://github.com/yaronzz/Tidal-Media-Downloader
"""
    print(logo_text)


# Simple table display for track/album info
def display_table(
    title: str, data: dict
) -> None:
    """Display a simple table with track/album information."""
    print(f"\n+{'-' * 50}+")
    print(f"| {title.center(48)} |")
    print(f"+{'-' * 20}+{'-' * 29}+")

    for key, value in data.items():
        key_str = str(key)[
            :18
        ]  # Truncate long keys
        value_str = str(value)[
            :27
        ]  # Truncate long values
        print(
            f"| {key_str:<18} | {value_str:<27} |"
        )

    print(f"+{'-' * 20}+{'-' * 29}+")


def display_track_info(
    track, stream
) -> None:
    """Display track information in a table format."""
    data = {
        "Title": track.title,
        "ID": track.id,
        "Album": (
            track.album.title
            if track.album
            else "N/A"
        ),
        "Version": track.version
        or "None",
        "Explicit": str(track.explicit),
        "Max-Q": getattr(
            stream, "maxQuality", "N/A"
        ),
        "Get-Q": getattr(
            stream, "quality", "N/A"
        ),
        "Get-Codec": getattr(
            stream, "codec", "N/A"
        ),
    }
    display_table(
        "TRACK-PROPERTY", data
    )


def display_album_info(album) -> None:
    """Display album information in a table format."""
    data = {
        "Title": album.title,
        "ID": album.id,
        "Track Number": album.numberOfTracks,
        "Video Number": album.numberOfVideos,
        "Release Date": album.releaseDate,
        "Version": album.version
        or "None",
        "Explicit": str(album.explicit),
    }
    display_table(
        "ALBUM-PROPERTY", data
    )


# For progress bars, we'll use a simple implementation
class ProgressBar:
    """Simple progress bar implementation using carriage returns."""

    def __init__(
        self,
        total: int,
        width: int = 50,
        desc: str = "",
    ):
        self.total = total
        self.width = width
        self.desc = desc
        self.current = 0

    def update(
        self, amount: int = 1
    ) -> None:
        """Update progress by specified amount."""
        self.current = min(
            self.current + amount,
            self.total,
        )
        self._display()

    def set_progress(
        self, current: int
    ) -> None:
        """Set absolute progress value."""
        self.current = min(
            current, self.total
        )
        self._display()

    def _display(self) -> None:
        """Display the progress bar."""
        if self.total == 0:
            return

        percentage = (
            self.current / self.total
        ) * 100
        filled_width = int(
            (self.current / self.total)
            * self.width
        )
        bar = (
            "▓" * filled_width
            + "░"
            * (
                self.width
                - filled_width
            )
        )

        # Format: desc 50%|████████████░░░░░░░░| current/total
        output = f"\r{self.desc}{percentage:3.0f}%|{bar}| {self.current}/{self.total}"
        sys.stdout.write(output)
        sys.stdout.flush()

        # Print newline when complete
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()
