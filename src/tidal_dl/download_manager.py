#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Download manager - wraps original download.py logic in a cleaner interface."""

import logging
import os
from concurrent.futures import (
    ThreadPoolExecutor,
)

import tidal_dl.aigpy
from tidal_dl.decryption import (
    decrypt_file,
    decrypt_security_token,
)
from tidal_dl.model import (
    Album,
    Playlist,
    Track,
    Video,
)
from tidal_dl.path_builder import (
    getAlbumPath,
    getTrackPath,
    getVideoPath,
)
from tidal_dl.printf import Printf
from tidal_dl.settings import SETTINGS
from tidal_dl.tidal import TIDAL_API


def _is_skip(
    finalpath: str, url: str
) -> bool:
    """Check if file should be skipped."""
    if not SETTINGS.checkExist:
        return False
    curSize = tidal_dl.aigpy.file.getSize(
        finalpath
    )
    if curSize <= 0:
        return False
    netSize = tidal_dl.aigpy.net.getSize(url)
    return curSize >= netSize


def _decrypt_if_needed(
    stream, srcPath: str, descPath: str
):
    """Decrypt file if encryption key is present."""
    if tidal_dl.aigpy.string.isNull(
        stream.encryptionKey
    ):
        os.replace(srcPath, descPath)
    else:
        key, nonce = (
            decrypt_security_token(
                stream.encryptionKey
            )
        )
        decrypt_file(
            srcPath,
            descPath,
            key,
            nonce,
        )
        os.remove(srcPath)


def _parse_contributors(
    roleType: str, contributors
):
    """Parse contributors by role."""
    if contributors is None:
        return None
    try:
        ret = []
        for item in contributors[
            "items"
        ]:
            if item["role"] == roleType:
                ret.append(item["name"])
        return ret
    except Exception:
        return None


def _set_metadata(
    track: Track,
    album: Album,
    filepath: str,
    contributors,
    lyrics: str,
):
    """Set metadata tags on audio file."""
    obj = tidal_dl.aigpy.tag.TagTool(filepath)
    obj.album = track.album.title
    obj.title = track.title
    if not tidal_dl.aigpy.string.isNull(
        track.version
    ):
        obj.title += (
            " (" + track.version + ")"
        )

    obj.artist = list(
        map(
            lambda artist: artist.name,
            track.artists,
        )
    )
    obj.copyright = track.copyRight
    obj.tracknumber = track.trackNumber
    obj.discnumber = track.volumeNumber
    obj.composer = _parse_contributors(
        "Composer", contributors
    )
    obj.isrc = track.isrc

    obj.albumartist = list(
        map(
            lambda artist: artist.name,
            album.artists,
        )
    )
    obj.date = album.releaseDate
    obj.totaldisc = (
        album.numberOfVolumes
    )
    obj.lyrics = lyrics
    if obj.totaldisc <= 1:
        obj.totaltrack = (
            album.numberOfTracks
        )
    coverpath = TIDAL_API.getCoverUrl(
        album.cover, "1280", "1280"
    )
    obj.save(coverpath)


def downloadCover(album: Album):
    """Download album cover."""
    if album is None:
        return
    path = (
        getAlbumPath(album)
        + "/cover.jpg"
    )
    url = TIDAL_API.getCoverUrl(
        album.cover, "1280", "1280"
    )
    tidal_dl.aigpy.net.downloadFile(url, path)


def downloadAlbumInfo(
    album: Album, tracks
):
    """Download album information text file."""
    if album is None:
        return

    path = getAlbumPath(album)
    tidal_dl.aigpy.path.mkdirs(path)

    path += "/AlbumInfo.txt"
    infos = ""
    infos += "[ID]          %s\n" % (
        str(album.id)
    )
    infos += "[Title]       %s\n" % (
        str(album.title)
    )
    infos += "[Artists]     %s\n" % (
        TIDAL_API.getArtistsName(
            album.artists
        )
    )
    infos += "[ReleaseDate] %s\n" % (
        str(album.releaseDate)
    )
    infos += "[SongNum]     %s\n" % (
        str(album.numberOfTracks)
    )
    infos += "[Duration]    %s\n" % (
        str(album.duration)
    )
    infos += "\n"

    for index in range(
        0, album.numberOfVolumes
    ):
        volumeNumber = index + 1
        infos += f"===========CD {volumeNumber}=============\n"
        for item in tracks:
            if (
                item.volumeNumber
                != volumeNumber
            ):
                continue
            infos += "{:<8}".format(
                "[%d]"
                % item.trackNumber
            )
            infos += "%s\n" % item.title
    tidal_dl.aigpy.file.write(path, infos, "w+")


def downloadVideo(
    video: Video,
    album: Album = None,
    playlist: Playlist = None,
):
    """Download a single video."""
    try:
        import requests

        stream = (
            TIDAL_API.getVideoStreamUrl(
                video.id,
                SETTINGS.videoQuality,
            )
        )
        path = getVideoPath(
            video, album, playlist
        )

        Printf.video(video, stream)
        logging.info(
            "[DL Video] name="
            + tidal_dl.aigpy.path.getFileName(
                path
            )
            + "\nurl="
            + stream.m3u8Url
        )

        m3u8content = requests.get(
            stream.m3u8Url
        ).content
        if m3u8content is None:
            Printf.err(
                f"DL Video[{video.title}] getM3u8 failed."
            )
            return (
                False,
                "GetM3u8 failed.",
            )

        urls = tidal_dl.aigpy.m3u8.parseTsUrls(
            m3u8content
        )
        if len(urls) <= 0:
            Printf.err(
                f"DL Video[{video.title}] getTsUrls failed."
            )
            return (
                False,
                "GetTsUrls failed.",
            )

        check, msg = (
            tidal_dl.aigpy.m3u8.downloadByTsUrls(
                urls, path
            )
        )
        if check:
            Printf.success(video.title)
            return True
        else:
            Printf.err(
                f"DL Video[{video.title}] failed.{msg}"
            )
            return False, msg
    except Exception as e:
        Printf.err(
            f"DL Video[{video.title}] failed.{str(e)}"
        )
        return False, str(e)


def downloadTrack(
    track: Track,
    album=None,
    playlist=None,
    userProgress=None,
    partSize=1048576,
):
    """Download a single track."""
    try:
        stream = TIDAL_API.getStreamUrl(
            track.id,
            SETTINGS.audioQuality,
        )
        path = getTrackPath(
            track,
            stream,
            album,
            playlist,
        )

        if (
            SETTINGS.showTrackInfo
            and not SETTINGS.multiThread
        ):
            Printf.track(track, stream)

        if userProgress is not None:
            userProgress.updateStream(
                stream
            )

        # check exist
        if _is_skip(path, stream.url):
            Printf.success(
                tidal_dl.aigpy.path.getFileName(
                    path
                )
                + " (skip:already exists!)"
            )
            return True, ""

        # download
        logging.info(
            "[DL Track] name="
            + tidal_dl.aigpy.path.getFileName(
                path
            )
            + "\nurl="
            + stream.url
        )

        tool = (
            tidal_dl.aigpy.download.DownloadTool(
                path + ".part",
                stream.urls,
            )
        )
        tool.setUserProgress(
            userProgress
        )
        tool.setPartSize(partSize)
        check, err = tool.start(
            SETTINGS.showProgress
            and not SETTINGS.multiThread
        )
        if not check:
            Printf.err(
                f"DL Track '{track.title}' failed: {str(err)}"
            )
            return False, str(err)

        # encrypted -> decrypt and remove encrypted file
        _decrypt_if_needed(
            stream, path + ".part", path
        )

        # contributors
        try:
            contributors = TIDAL_API.getTrackContributors(
                track.id
            )
        except Exception:
            contributors = None

        # lyrics
        try:
            lyrics = (
                TIDAL_API.getLyrics(
                    track.id
                ).subtitles
            )
            if SETTINGS.lyricFile:
                lrcPath = (
                    path.rsplit(".", 1)[
                        0
                    ]
                    + ".lrc"
                )
                tidal_dl.aigpy.file.write(
                    lrcPath, lyrics, "w"
                )
        except Exception:
            lyrics = ""

        _set_metadata(
            track,
            album,
            path,
            contributors,
            lyrics,
        )
        Printf.success(track.title)

        return True, ""
    except Exception as e:
        Printf.err(
            f"DL Track '{track.title}' failed: {str(e)}"
        )
        return False, str(e)


def downloadTracks(
    tracks,
    album: Album = None,
    playlist: Playlist = None,
):
    """Download multiple tracks."""

    def __getAlbum__(item: Track):
        album = TIDAL_API.getAlbum(
            item.album.id
        )
        if (
            SETTINGS.saveCovers
            and not SETTINGS.usePlaylistFolder
        ):
            downloadCover(album)
        return album

    if not SETTINGS.multiThread:
        for index, item in enumerate(
            tracks
        ):
            itemAlbum = album
            if itemAlbum is None:
                itemAlbum = (
                    __getAlbum__(item)
                )
                item.trackNumberOnPlaylist = (
                    index + 1
                )
            downloadTrack(
                item,
                itemAlbum,
                playlist,
            )
    else:
        thread_pool = (
            ThreadPoolExecutor(
                max_workers=5
            )
        )
        for index, item in enumerate(
            tracks
        ):
            itemAlbum = album
            if itemAlbum is None:
                itemAlbum = (
                    __getAlbum__(item)
                )
                item.trackNumberOnPlaylist = (
                    index + 1
                )
            thread_pool.submit(
                downloadTrack,
                item,
                itemAlbum,
                playlist,
            )
        thread_pool.shutdown(wait=True)


def downloadVideos(
    videos, album: Album, playlist=None
):
    """Download multiple videos."""
    for item in videos:
        downloadVideo(
            item, album, playlist
        )
