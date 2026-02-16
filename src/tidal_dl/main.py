#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Main entry point - modernized with argparse."""

import json
import sys

import tidal_dl.aigpy
from tidal_dl import apiKey
from tidal_dl.config import (
    ConfigManager,
)
from tidal_dl.logger import (
    error,
    success,
    info,
    debug,
    logo,
    configure_logging,
)
from tidal_dl.events import (
    changeApiKey,
    changePathSettings,
    changeQualitySettings,
    changeSettings,
    loginByAccessToken,
    loginByConfig,
    loginByWeb,
    start,
)
from tidal_dl.paths import (
    getProfilePath,
    getTokenPath,
)
from tidal_dl.printf import (
    Printf,
)  # Keep temporarily for complex functions
from tidal_dl.settings import (
    SETTINGS,
    TOKEN,
)
from tidal_dl.tidal import TIDAL_API


def sync_legacy_to_modern_config(
    config_manager,
):
    """Sync legacy SETTINGS to modern config."""
    config_manager.settings.download_path = (
        SETTINGS.downloadPath
    )
    config_manager.settings.audio_quality = (
        SETTINGS.audioQuality
    )
    config_manager.settings.video_quality = (
        SETTINGS.videoQuality
    )
    config_manager.settings.check_exist = (
        SETTINGS.checkExist
    )
    config_manager.settings.include_ep = (
        SETTINGS.includeEP
    )
    config_manager.settings.save_covers = (
        SETTINGS.saveCovers
    )
    config_manager.settings.lyric_file = (
        SETTINGS.lyricFile
    )
    config_manager.settings.save_album_info = (
        SETTINGS.saveAlbumInfo
    )
    config_manager.settings.download_videos = (
        SETTINGS.downloadVideos
    )
    config_manager.settings.multi_thread = (
        SETTINGS.multiThread
    )
    config_manager.settings.download_delay = (
        SETTINGS.downloadDelay
    )
    config_manager.settings.use_playlist_folder = (
        SETTINGS.usePlaylistFolder
    )
    config_manager.settings.show_progress = (
        SETTINGS.showProgress
    )
    config_manager.settings.show_track_info = (
        SETTINGS.showTrackInfo
    )
    config_manager.settings.language = (
        SETTINGS.language
    )
    config_manager.settings.api_key_index = (
        SETTINGS.apiKeyIndex
    )
    config_manager.settings.convert_flac = (
        SETTINGS.convertFlac
    )
    config_manager.settings.verbose = (
        SETTINGS.verbose
    )
    config_manager.settings.http_proxy = (
        SETTINGS.httpProxy
    )
    config_manager.settings.https_proxy = (
        SETTINGS.httpsProxy
    )
    config_manager.save_settings()


def sync_modern_to_legacy_config(
    config_manager,
):
    """Sync modern config to legacy SETTINGS."""
    SETTINGS.downloadPath = (
        config_manager.settings.download_path
    )
    SETTINGS.audioQuality = (
        config_manager.settings.audio_quality
    )
    SETTINGS.videoQuality = (
        config_manager.settings.video_quality
    )
    SETTINGS.checkExist = (
        config_manager.settings.check_exist
    )
    SETTINGS.includeEP = (
        config_manager.settings.include_ep
    )
    SETTINGS.saveCovers = (
        config_manager.settings.save_covers
    )
    SETTINGS.lyricFile = (
        config_manager.settings.lyric_file
    )
    SETTINGS.saveAlbumInfo = (
        config_manager.settings.save_album_info
    )
    SETTINGS.downloadVideos = (
        config_manager.settings.download_videos
    )
    SETTINGS.multiThread = (
        config_manager.settings.multi_thread
    )
    SETTINGS.downloadDelay = (
        config_manager.settings.download_delay
    )
    SETTINGS.usePlaylistFolder = (
        config_manager.settings.use_playlist_folder
    )
    SETTINGS.showProgress = (
        config_manager.settings.show_progress
    )
    SETTINGS.showTrackInfo = (
        config_manager.settings.show_track_info
    )
    SETTINGS.language = (
        config_manager.settings.language
    )
    SETTINGS.apiKeyIndex = (
        config_manager.settings.api_key_index
    )
    SETTINGS.convertFlac = (
        config_manager.settings.convert_flac
    )
    SETTINGS.verbose = (
        config_manager.settings.verbose
    )
    SETTINGS.httpProxy = (
        config_manager.settings.http_proxy
    )
    SETTINGS.httpsProxy = (
        config_manager.settings.https_proxy
    )
    SETTINGS.save()


def mainCommand():
    """Handle command-line arguments using argparse."""
    import argparse

    # Load legacy settings first for compatibility
    SETTINGS.read(getProfilePath())

    # Initialize modern config system and load from file
    config_manager = ConfigManager()
    config_manager.load_settings()

    # Sync modern config to legacy (modern config.json takes precedence)
    # This ensures proxies from config.json are loaded into SETTINGS
    sync_modern_to_legacy_config(config_manager)

    # Also sync back to modern to ensure consistency
    sync_legacy_to_modern_config(config_manager)

    parser = argparse.ArgumentParser(
        prog="tidal-dl",
        description="Download music and videos from Tidal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="tidal-dl 2025.12.1",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose/debug output",
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
        "--no-flac-conversion",
        action="store_true",
        help="Disable automatic FLAC conversion for Max quality downloads",
    )

    parser.add_argument(
        "--http-proxy",
        type=str,
        metavar="URL",
        help="HTTP proxy URL (e.g., http://proxy.example.com:8080)",
    )

    parser.add_argument(
        "--https-proxy",
        type=str,
        metavar="URL",
        help="HTTPS proxy URL (e.g., http://proxy.example.com:8080)",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        # argparse handles help/version and exits gracefully
        return

    # Configure logging level based on verbose flag
    configure_logging(
        verbose=args.verbose
    )

    # Update verbose setting in both config systems based on command line arg
    config_manager.settings.verbose = (
        args.verbose
    )
    SETTINGS.verbose = args.verbose
    if args.verbose:
        config_manager.save_settings()

    # Handle special cases
    if args.gui:
        error(
            "GUI mode has been removed. Please use command-line interface."
        )
        return

    # Apply settings from arguments to modern config system
    if args.output:
        config_manager.settings.download_path = (
            args.output
        )
        config_manager.save_settings()

    if args.quality:
        from tidal_dl.enums import (
            AudioQuality,
        )

        try:
            config_manager.settings.audio_quality = AudioQuality[
                args.quality
            ]
            config_manager.save_settings()
        except KeyError:
            error(
                f"Invalid quality: {args.quality}"
            )
            return

    if args.resolution:
        from tidal_dl.enums import (
            VideoQuality,
        )

        try:
            config_manager.settings.video_quality = VideoQuality[
                args.resolution
            ]
            config_manager.save_settings()
        except KeyError:
            error(
                f"Invalid resolution: {args.resolution}"
            )
            return

    if args.http_proxy:
        config_manager.settings.http_proxy = (
            args.http_proxy
        )
        SETTINGS.httpProxy = (
            args.http_proxy
        )
        config_manager.save_settings()

    if args.https_proxy:
        config_manager.settings.https_proxy = (
            args.https_proxy
        )
        SETTINGS.httpsProxy = (
            args.https_proxy
        )
        config_manager.save_settings()

    # Handle JSON mode - can only be used with link option
    if args.json and args.link:
        if not loginByConfig(True):
            error(
                "Login failed. Please authenticate first."
            )
            return
        try:
            etype, obj = (
                TIDAL_API.getByString(
                    args.link
                )
            )
            output = {
                "type": etype.name,
                "data": tidal_dl.aigpy.model.modelToDict(
                    obj
                ),
            }
            print(
                json.dumps(
                    output, indent=4
                )
            )
            return
        except Exception as e:
            error(str(e))
        return
    elif args.json and not args.link:
        error(
            "JSON mode requires a link. Use -j/--json with -l/--link"
        )
        return

    # Handle FLAC conversion options
    if args.no_flac_conversion:
        config_manager.settings.convert_flac = (
            False
        )
        config_manager.save_settings()

    # Validate download path
    if not tidal_dl.aigpy.path.mkdirs(
        config_manager.settings.download_path
    ):
        error(
            "Invalid download path: "
            + config_manager.settings.download_path
        )
        return

    # Handle download request
    if args.link is not None:
        # Sync modern config back to legacy for compatibility with download system
        sync_modern_to_legacy_config(
            config_manager
        )

        if not loginByConfig():
            loginByWeb()
        info(
            "Download path: "
            + config_manager.settings.download_path
        )
        start(args.link)


def main():
    """Main entry point - maintains interactive mode from original."""
    SETTINGS.read(getProfilePath())
    TOKEN.read(getTokenPath())

    # Load modern config and sync to legacy to ensure proxies are loaded
    config_manager = ConfigManager()
    config_manager.load_settings()
    sync_modern_to_legacy_config(config_manager)

    # Configure logging based on stored verbose setting
    configure_logging(
        verbose=getattr(
            SETTINGS, "verbose", False
        )
    )

    TIDAL_API.apiKey = apiKey.getItem(
        SETTINGS.apiKeyIndex
    )

    if len(sys.argv) > 1:
        mainCommand()
        return

    # Interactive mode
    logo()
    Printf.settings()

    if not apiKey.isItemValid(
        SETTINGS.apiKeyIndex
    ):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb()

    Printf.checkVersion()

    while True:
        Printf.choices()
        from tidal_dl.lang.language import (
            LANG,
        )

        choice = Printf.enter(
            LANG.select.PRINT_ENTER_CHOICE
        )
        if choice == "0":
            return
        elif choice == "1":
            if not loginByConfig():
                loginByWeb()
        elif choice == "2":
            loginByWeb()
        elif choice == "3":
            loginByAccessToken()
        elif choice == "4":
            changePathSettings()
        elif choice == "5":
            changeQualitySettings()
        elif choice == "6":
            changeSettings()
        elif choice == "7":
            if changeApiKey():
                loginByWeb()
        else:
            start(choice)


if __name__ == "__main__":
    main()
else:
    # Only import TIDAL_API when this module is imported as a library
    # This avoids side effects when running as a script
    from tidal_dl.tidal import TIDAL_API

    __all__ = ["TIDAL_API"]
