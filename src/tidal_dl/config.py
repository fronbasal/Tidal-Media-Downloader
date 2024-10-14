#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Configuration management for Tidal-DL."""

import base64
import json
from dataclasses import (
    asdict,
    dataclass,
    field,
    fields,
)
from pathlib import Path
from typing import Optional

from tidal_dl.enums import (
    AudioQuality,
    Type,
    VideoQuality,
)


@dataclass
class PathFormats:
    """Path format configuration."""

    album_folder: str = (
        R"{ArtistName}/{Flag} {AlbumTitle} [{AlbumID}] [{AlbumYear}]"
    )
    playlist_folder: str = (
        R"Playlist/{PlaylistName} [{PlaylistUUID}]"
    )
    track_file: str = (
        R"{TrackNumber} - {ArtistName} - {TrackTitle}{ExplicitFlag}"
    )
    video_file: str = (
        R"{VideoNumber} - {ArtistName} - {VideoTitle}{ExplicitFlag}"
    )

    @classmethod
    def get_default_format(
        cls, item_type: Type
    ) -> str:
        """Get default format for a given type."""
        defaults = cls()
        if item_type == Type.Album:
            return defaults.album_folder
        elif item_type == Type.Playlist:
            return (
                defaults.playlist_folder
            )
        elif item_type == Type.Track:
            return defaults.track_file
        elif item_type == Type.Video:
            return defaults.video_file
        return ""


@dataclass
class Settings:
    """Application settings."""

    # Download settings
    download_path: str = "./download/"
    audio_quality: AudioQuality = (
        AudioQuality.Normal
    )
    video_quality: VideoQuality = (
        VideoQuality.P360
    )

    # Behavior settings
    check_exist: bool = True
    include_ep: bool = True
    save_covers: bool = True
    lyric_file: bool = False
    save_album_info: bool = False
    download_videos: bool = True
    multi_thread: bool = False
    download_delay: bool = True
    use_playlist_folder: bool = True
    show_progress: bool = True
    show_track_info: bool = True
    convert_flac: bool = True  # Auto-convert FLAC-in-MP4 to proper FLAC (Max quality only)

    # Interface settings
    language: int = 0
    api_key_index: int = 0
    verbose: bool = False  # Enable debug/verbose logging

    # Path formats
    path_formats: PathFormats = field(
        default_factory=PathFormats
    )

    def __post_init__(self):
        """Ensure enums are properly typed."""
        if isinstance(
            self.audio_quality, str
        ):
            self.audio_quality = (
                self._get_audio_quality(
                    self.audio_quality
                )
            )
        if isinstance(
            self.video_quality, str
        ):
            self.video_quality = (
                self._get_video_quality(
                    self.video_quality
                )
            )
        if not isinstance(
            self.path_formats,
            PathFormats,
        ):
            if isinstance(
                self.path_formats, dict
            ):
                self.path_formats = PathFormats(
                    **self.path_formats
                )
            else:
                self.path_formats = (
                    PathFormats()
                )

    @staticmethod
    def _get_audio_quality(
        value: str,
    ) -> AudioQuality:
        """Convert string to AudioQuality enum."""
        try:
            return AudioQuality[value]
        except (KeyError, TypeError):
            return AudioQuality.Normal

    @staticmethod
    def _get_video_quality(
        value: str,
    ) -> VideoQuality:
        """Convert string to VideoQuality enum."""
        try:
            return VideoQuality[value]
        except (KeyError, TypeError):
            return VideoQuality.P360

    def to_dict(self) -> dict:
        """Convert settings to dictionary for serialization."""
        data = asdict(self)
        data["audio_quality"] = (
            self.audio_quality.name
        )
        data["video_quality"] = (
            self.video_quality.name
        )
        return data

    @classmethod
    def from_dict(
        cls, data: dict
    ) -> "Settings":
        """Create Settings from dictionary."""
        # Handle legacy format
        legacy_mapping = {
            "downloadPath": "download_path",
            "audioQuality": "audio_quality",
            "videoQuality": "video_quality",
            "checkExist": "check_exist",
            "includeEP": "include_ep",
            "saveCovers": "save_covers",
            "lyricFile": "lyric_file",
            "apiKeyIndex": "api_key_index",
            "showProgress": "show_progress",
            "showTrackInfo": "show_track_info",
            "saveAlbumInfo": "save_album_info",
            "downloadVideos": "download_videos",
            "multiThread": "multi_thread",
            "downloadDelay": "download_delay",
            "usePlaylistFolder": "use_playlist_folder",
            "convertFlac": "convert_flac",
            "albumFolderFormat": "album_folder",
            "playlistFolderFormat": "playlist_folder",
            "trackFileFormat": "track_file",
            "videoFileFormat": "video_file",
        }

        normalized = {}
        for key, value in data.items():
            new_key = (
                legacy_mapping.get(
                    key, key
                )
            )
            normalized[new_key] = value

        # Extract path formats
        path_format_keys = {
            "album_folder",
            "playlist_folder",
            "track_file",
            "video_file",
        }
        path_formats_data = {
            k: normalized.pop(k)
            for k in path_format_keys
            if k in normalized
        }
        if path_formats_data:
            normalized[
                "path_formats"
            ] = path_formats_data

        valid_fields = {
            f.name for f in fields(cls)
        }
        return cls(
            **{
                k: v
                for k, v in normalized.items()
                if k in valid_fields
            }
        )


@dataclass
class TokenSettings:
    """Authentication token settings."""

    user_id: Optional[str] = None
    country_code: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_after: int = 0

    @staticmethod
    def _encode(data: str) -> bytes:
        """Encode string to base64."""
        return base64.b64encode(
            data.encode("utf-8")
        )

    @staticmethod
    def _decode(data: bytes) -> str:
        """Decode base64 to string."""
        try:
            return base64.b64decode(
                data
            ).decode("utf-8")
        except Exception:
            return str(data)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(
        cls, data: dict
    ) -> "TokenSettings":
        """Create TokenSettings from dictionary."""
        # Handle legacy format
        legacy_mapping = {
            "userid": "user_id",
            "countryCode": "country_code",
            "accessToken": "access_token",
            "refreshToken": "refresh_token",
            "expiresAfter": "expires_after",
        }

        normalized = {
            legacy_mapping.get(k, k): v
            for k, v in data.items()
        }
        valid_fields = {
            f.name for f in fields(cls)
        }
        return cls(
            **{
                k: v
                for k, v in normalized.items()
                if k in valid_fields
            }
        )


class ConfigManager:
    """Manages application configuration."""

    def __init__(
        self,
        config_dir: Optional[
            Path
        ] = None,
    ):
        """Initialize configuration manager."""
        if config_dir is None:
            config_dir = (
                Path.home()
                / ".tidal-dl"
            )
        self.config_dir = Path(
            config_dir
        )
        self.config_dir.mkdir(
            parents=True, exist_ok=True
        )

        self.settings_path = (
            self.config_dir
            / "settings.json"
        )
        self.token_path = (
            self.config_dir
            / "token.json"
        )

        self.settings = Settings()
        self.token = TokenSettings()

    def load_settings(self) -> Settings:
        """Load settings from file."""
        try:
            if (
                self.settings_path.exists()
            ):
                content = (
                    self.settings_path.read_text()
                )
                data = json.loads(
                    content
                )
                self.settings = (
                    Settings.from_dict(
                        data
                    )
                )
        except Exception as e:
            print(
                f"Warning: Could not load settings: {e}"
            )
            self.settings = Settings()
        return self.settings

    def save_settings(self):
        """Save settings to file."""
        try:
            data = (
                self.settings.to_dict()
            )
            content = json.dumps(
                data, indent=2
            )
            self.settings_path.write_text(
                content
            )
        except Exception as e:
            print(
                f"Error: Could not save settings: {e}"
            )

    def load_token(
        self,
    ) -> TokenSettings:
        """Load token from file."""
        try:
            if self.token_path.exists():
                content = (
                    self.token_path.read_bytes()
                )
                decoded = TokenSettings._decode(
                    content
                )
                data = json.loads(
                    decoded
                )
                self.token = TokenSettings.from_dict(
                    data
                )
        except Exception as e:
            print(
                f"Warning: Could not load token: {e}"
            )
            self.token = TokenSettings()
        return self.token

    def save_token(self):
        """Save token to file."""
        try:
            data = self.token.to_dict()
            content = json.dumps(data)
            encoded = (
                TokenSettings._encode(
                    content
                )
            )
            self.token_path.write_bytes(
                encoded
            )
        except Exception as e:
            print(
                f"Error: Could not save token: {e}"
            )

    def get_profile_path(self) -> str:
        """Get profile configuration path."""
        return str(self.settings_path)

    def get_token_path(self) -> str:
        """Get token configuration path."""
        return str(self.token_path)
