#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Path builder - maintains 100% compatibility with original paths.py logic."""

import datetime
import os
from pathlib import Path

import tidal_dl.aigpy
from tidal_dl.enums import (
    AudioQuality,
    Type,
)
from tidal_dl.model import (
    Album,
    Playlist,
    StreamUrl,
    Track,
    Video,
)
from tidal_dl.settings import SETTINGS
from tidal_dl.tidal import TIDAL_API


def __fixPath__(name: str) -> str:
    """Remove invalid path characters."""
    return tidal_dl.aigpy.path.replaceLimitChar(
        name, "-"
    ).strip()


def __getYear__(
    releaseDate: str,
) -> str:
    """Extract year from release date."""
    if (
        releaseDate is None
        or releaseDate == ""
    ):
        return ""
    return tidal_dl.aigpy.string.getSubOnlyEnd(
        releaseDate, "-"
    )


def __getDurationStr__(
    seconds: int,
) -> str:
    """Convert seconds to duration string."""
    time_string = str(
        datetime.timedelta(
            seconds=seconds
        )
    )
    if time_string.startswith("0:"):
        time_string = time_string[2:]
    return time_string


def __getExtension__(
    stream: StreamUrl,
) -> str:
    """Determine file extension from stream."""
    if ".flac" in stream.url:
        return ".flac"
    if ".mp4" in stream.url:
        if (
            "ac4" in stream.codec
            or "mha1" in stream.codec
        ):
            return ".mp4"
        elif "flac" in stream.codec:
            return ".flac"
        return ".m4a"
    return ".m4a"


def getAlbumPath(album: Album) -> str:
    """Get directory path for album - 100% compatible with original."""
    artistName = __fixPath__(
        TIDAL_API.getArtistsName(
            album.artists
        )
    )
    albumArtistName = (
        __fixPath__(album.artist.name)
        if album.artist is not None
        else ""
    )

    # album folder pre: [ME]
    flag = TIDAL_API.getFlag(
        album, Type.Album, True, ""
    )
    if (
        SETTINGS.audioQuality
        != AudioQuality.Master
        and SETTINGS.audioQuality
        != AudioQuality.Max
    ):
        flag = flag.replace("M", "")
    if flag != "":
        flag = "[" + flag + "] "

    albumName = __fixPath__(album.title)
    year = __getYear__(
        album.releaseDate
    )

    # retpath
    retpath = SETTINGS.albumFolderFormat
    if (
        retpath is None
        or len(retpath) <= 0
    ):
        retpath = SETTINGS.getDefaultPathFormat(
            Type.Album
        )
    retpath = retpath.replace(
        R"{ArtistName}", artistName
    )
    retpath = retpath.replace(
        R"{AlbumArtistName}",
        albumArtistName,
    )
    retpath = retpath.replace(
        R"{Flag}", flag
    )
    retpath = retpath.replace(
        R"{AlbumID}", str(album.id)
    )
    retpath = retpath.replace(
        R"{AlbumYear}", year
    )
    retpath = retpath.replace(
        R"{AlbumTitle}", albumName
    )
    retpath = retpath.replace(
        R"{AudioQuality}",
        album.audioQuality or "",
    )
    retpath = retpath.replace(
        R"{DurationSeconds}",
        str(album.duration),
    )
    retpath = retpath.replace(
        R"{Duration}",
        __getDurationStr__(
            album.duration
        ),
    )
    retpath = retpath.replace(
        R"{NumberOfTracks}",
        str(album.numberOfTracks),
    )
    retpath = retpath.replace(
        R"{NumberOfVideos}",
        str(album.numberOfVideos),
    )
    retpath = retpath.replace(
        R"{NumberOfVolumes}",
        str(album.numberOfVolumes),
    )
    retpath = retpath.replace(
        R"{ReleaseDate}",
        str(album.releaseDate),
    )
    retpath = retpath.replace(
        R"{RecordType}",
        album.type or "",
    )
    retpath = retpath.replace(
        R"{None}", ""
    )
    retpath = retpath.strip()
    return os.path.join(
        SETTINGS.downloadPath, retpath
    )


def getPlaylistPath(
    playlist: Playlist,
) -> str:
    """Get directory path for playlist."""
    playlistName = __fixPath__(
        playlist.title
    )

    retpath = (
        SETTINGS.playlistFolderFormat
    )
    if (
        retpath is None
        or len(retpath) <= 0
    ):
        retpath = SETTINGS.getDefaultPathFormat(
            Type.Playlist
        )
    retpath = retpath.replace(
        R"{PlaylistUUID}",
        str(playlist.uuid),
    )
    retpath = retpath.replace(
        R"{PlaylistName}", playlistName
    )
    return os.path.join(
        SETTINGS.downloadPath, retpath
    )


def getTrackPath(
    track: Track,
    stream: StreamUrl,
    album=None,
    playlist=None,
) -> str:
    """Get file path for track - 100% compatible with original."""
    base = "./"
    number = str(
        track.trackNumber
    ).rjust(2, "0")

    if album is not None:
        base = getAlbumPath(album)
        if album.numberOfVolumes > 1:
            base += f"/CD{str(track.volumeNumber)}"

    if (
        playlist is not None
        and SETTINGS.usePlaylistFolder
    ):
        base = getPlaylistPath(playlist)
        number = str(
            track.trackNumberOnPlaylist
        ).rjust(2, "0")

    # artist
    artists = __fixPath__(
        TIDAL_API.getArtistsName(
            track.artists
        )
    )
    artist = (
        __fixPath__(track.artist.name)
        if track.artist is not None
        else ""
    )

    # title
    title = __fixPath__(track.title)
    if not tidal_dl.aigpy.string.isNull(
        track.version
    ):
        title += f" ({__fixPath__(track.version)})"

    # explicit
    explicit = (
        "(Explicit)"
        if track.explicit
        else ""
    )

    # album and year
    albumName = (
        __fixPath__(album.title)
        if album is not None
        else ""
    )
    year = (
        __getYear__(album.releaseDate)
        if album is not None
        else ""
    )

    # extension
    extension = __getExtension__(stream)

    retpath = SETTINGS.trackFileFormat
    if (
        retpath is None
        or len(retpath) <= 0
    ):
        retpath = SETTINGS.getDefaultPathFormat(
            Type.Track
        )
    retpath = retpath.replace(
        R"{TrackNumber}", number
    )
    retpath = retpath.replace(
        R"{ArtistName}", artist
    )
    retpath = retpath.replace(
        R"{ArtistsName}", artists
    )
    retpath = retpath.replace(
        R"{TrackTitle}", title
    )
    retpath = retpath.replace(
        R"{ExplicitFlag}", explicit
    )
    retpath = retpath.replace(
        R"{AlbumYear}", year
    )
    retpath = retpath.replace(
        R"{AlbumTitle}", albumName
    )
    retpath = retpath.replace(
        R"{AudioQuality}",
        track.audioQuality or "",
    )
    retpath = retpath.replace(
        R"{DurationSeconds}",
        str(track.duration),
    )
    retpath = retpath.replace(
        R"{Duration}",
        __getDurationStr__(
            track.duration
        ),
    )
    retpath = retpath.replace(
        R"{TrackID}", str(track.id)
    )
    retpath = retpath.strip()
    return (
        f"{base}/{retpath}{extension}"
    )


def getVideoPath(
    video: Video,
    album=None,
    playlist=None,
) -> str:
    """Get file path for video - 100% compatible with original."""
    base = os.path.join(
        SETTINGS.downloadPath, "Video"
    )
    number = str(
        video.trackNumber
    ).rjust(2, "0")

    if album is not None:
        base = getAlbumPath(album)
    if (
        playlist is not None
        and SETTINGS.usePlaylistFolder
    ):
        base = getPlaylistPath(playlist)
        number = str(
            video.trackNumberOnPlaylist
        ).rjust(2, "0")

    # artist
    artists = __fixPath__(
        TIDAL_API.getArtistsName(
            video.artists
        )
    )
    artist = (
        __fixPath__(video.artist.name)
        if video.artist is not None
        else ""
    )

    # title
    title = __fixPath__(video.title)
    if not tidal_dl.aigpy.string.isNull(
        video.version
    ):
        title += f" ({__fixPath__(video.version)})"

    # explicit
    explicit = (
        "(Explicit)"
        if video.explicit
        else ""
    )

    # album and year
    albumName = (
        __fixPath__(album.title)
        if album is not None
        else ""
    )
    year = (
        __getYear__(album.releaseDate)
        if album is not None
        else ""
    )

    retpath = SETTINGS.videoFileFormat
    if (
        retpath is None
        or len(retpath) <= 0
    ):
        retpath = SETTINGS.getDefaultPathFormat(
            Type.Video
        )
    retpath = retpath.replace(
        R"{VideoNumber}", number
    )
    retpath = retpath.replace(
        R"{ArtistName}", artist
    )
    retpath = retpath.replace(
        R"{ArtistsName}", artists
    )
    retpath = retpath.replace(
        R"{VideoTitle}", title
    )
    retpath = retpath.replace(
        R"{ExplicitFlag}", explicit
    )
    retpath = retpath.replace(
        R"{AlbumYear}", year
    )
    retpath = retpath.replace(
        R"{AlbumTitle}", albumName
    )
    retpath = retpath.replace(
        R"{VideoID}", str(video.id)
    )
    retpath = retpath.strip()
    return f"{base}/{retpath}.mp4"
