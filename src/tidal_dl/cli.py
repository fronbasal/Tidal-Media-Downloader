#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Command-line interface for Tidal-DL."""

import argparse
import sys
from typing import Optional

from tidal_dl.config import (
    ConfigManager,
)
from tidal_dl.enums import (
    AudioQuality,
    VideoQuality,
)


class TidalCLI:
    """Command-line interface handler."""

    VERSION = "2025.10.1"

    def __init__(
        self,
        config_manager: ConfigManager,
    ):
        """Initialize CLI handler."""
        self.config = config_manager
        self.parser = (
            self._create_parser()
        )

    def _create_parser(
        self,
    ) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog="tidal-dl",
            description="Download music and videos from Tidal",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"%(prog)s {self.VERSION}",
        )

        parser.add_argument(
            "-g",
            "--gui",
            action="store_true",
            help="Launch graphical user interface",
        )

        parser.add_argument(
            "-l",
            "--link",
            type=str,
            metavar="URL",
            help="Tidal URL, ID, or file path to download",
        )

        parser.add_argument(
            "-o",
            "--output",
            type=str,
            metavar="PATH",
            help="Download destination path",
        )

        parser.add_argument(
            "-q",
            "--quality",
            type=str,
            choices=[
                "Normal",
                "High",
                "HiFi",
                "Master",
                "Max",
            ],
            help="Audio quality for tracks",
        )

        parser.add_argument(
            "-r",
            "--resolution",
            type=str,
            choices=[
                "P240",
                "P360",
                "P480",
                "P720",
                "P1080",
            ],
            help="Video resolution",
        )

        parser.add_argument(
            "-j",
            "--json",
            action="store_true",
            help="Output item metadata as JSON (requires --link)",
        )

        parser.add_argument(
            "-n",
            "--non-interactive",
            action="store_true",
            help="Non-interactive mode with JSON output (requires --json and --link)",
        )

        return parser

    def parse_args(
        self,
        args: Optional[list] = None,
    ) -> argparse.Namespace:
        """Parse command-line arguments."""
        if args is None:
            args = sys.argv[1:]
        return self.parser.parse_args(
            args
        )

    def apply_args_to_config(
        self, args: argparse.Namespace
    ):
        """Apply parsed arguments to configuration."""
        if args.output:
            self.config.settings.download_path = (
                args.output
            )
            self.config.save_settings()

        if args.quality:
            self.config.settings.audio_quality = AudioQuality[
                args.quality
            ]
            self.config.save_settings()

        if args.resolution:
            self.config.settings.video_quality = VideoQuality[
                args.resolution
            ]
            self.config.save_settings()

    def print_help(self):
        """Print help message."""
        self.parser.print_help()
