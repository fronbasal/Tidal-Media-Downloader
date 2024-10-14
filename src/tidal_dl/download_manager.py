#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Download manager - wraps original download.py logic in a cleaner interface."""

import logging
import os
import subprocess
from concurrent.futures import (
    ThreadPoolExecutor,
)

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
from tidal_dl.logger import (
    error,
    success,
    info,
    debug,
    display_track_info,
)
from tidal_dl.settings import SETTINGS
from tidal_dl.enums import AudioQuality
from tidal_dl.printf import (
    Printf,
)  # Keep for now, will replace gradually
from tidal_dl.tidal import *


def _convert_flac_inplace(
    file_path: str,
) -> bool:
    """
    Convert FLAC-in-MP4 to proper FLAC with embedded cover art in place.

    Args:
        file_path: Path to the FLAC-in-MP4 file

    Returns:
        True if conversion succeeded, False otherwise
    """
    try:
        from mutagen import flac, mp4
        from mutagen.flac import Picture

        debug(
            f"Converting FLAC-in-MP4 to proper FLAC: {file_path}"
        )

        # Step 0: Check if the file is actually an MP4 container or a true FLAC file
        # Read first few bytes to check the file signature
        with open(file_path, 'rb') as f:
            header = f.read(12)

        # FLAC files start with "fLaC" (0x664C6143)
        # MP4 files start with ftyp box (typically at offset 4)
        if header[0:4] == b'fLaC':
            debug("File is already a proper FLAC file, no conversion needed")
            return True

        # If it's not a FLAC file, it should be an MP4 container
        # Step 1: Read metadata from original MP4 file
        mp4_file = mp4.MP4(file_path)

        # Step 2: Extract raw FLAC audio using ffmpeg to stdout
        ffmpeg_process = subprocess.run(
            [
                "ffmpeg",
                "-i",
                file_path,
                "-vn",  # No video
                "-c:a",
                "copy",  # Copy audio without re-encoding
                "-f",
                "flac",  # Force FLAC format
                "-",  # Output to stdout
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        flac_audio_data = (
            ffmpeg_process.stdout
        )
        debug(
            f"Extracted {len(flac_audio_data)} bytes of FLAC audio data"
        )

        # Step 3: Write FLAC data back to the same file
        with open(file_path, "wb") as f:
            f.write(flac_audio_data)

        # Step 4: Open the newly created FLAC file and add metadata
        flac_file = flac.FLAC(file_path)

        # Convert MP4 metadata to FLAC format
        if "\xa9nam" in mp4_file.tags:
            flac_file["TITLE"] = (
                mp4_file.tags["\xa9nam"]
            )
        if "\xa9alb" in mp4_file.tags:
            flac_file["ALBUM"] = (
                mp4_file.tags["\xa9alb"]
            )
        if "\xa9ART" in mp4_file.tags:
            flac_file["ARTIST"] = (
                mp4_file.tags["\xa9ART"]
            )
        if "aART" in mp4_file.tags:
            flac_file["ALBUMARTIST"] = (
                mp4_file.tags["aART"]
            )
        if "\xa9day" in mp4_file.tags:
            flac_file["DATE"] = (
                mp4_file.tags["\xa9day"]
            )
        if "\xa9gen" in mp4_file.tags:
            flac_file["GENRE"] = (
                mp4_file.tags["\xa9gen"]
            )
        if "\xa9wrt" in mp4_file.tags:
            flac_file["COMPOSER"] = (
                mp4_file.tags["\xa9wrt"]
            )
        if "cprt" in mp4_file.tags:
            flac_file["COPYRIGHT"] = (
                mp4_file.tags["cprt"]
            )
        if "\xa9lyr" in mp4_file.tags:
            flac_file["LYRICS"] = (
                mp4_file.tags["\xa9lyr"]
            )

        # Handle track/disc numbers
        if "trkn" in mp4_file.tags:
            track_info = mp4_file.tags[
                "trkn"
            ][0]
            if len(track_info) >= 1:
                flac_file[
                    "TRACKNUMBER"
                ] = str(track_info[0])
            if (
                len(track_info) >= 2
                and track_info[1] > 0
            ):
                flac_file[
                    "TRACKTOTAL"
                ] = str(track_info[1])

        if "disk" in mp4_file.tags:
            disc_info = mp4_file.tags[
                "disk"
            ][0]
            if len(disc_info) >= 1:
                flac_file[
                    "DISCNUMBER"
                ] = str(disc_info[0])
            if (
                len(disc_info) >= 2
                and disc_info[1] > 0
            ):
                flac_file[
                    "DISCTOTAL"
                ] = str(disc_info[1])

        # Step 5: Add cover art - prioritize cover.jpg in same directory
        cover_data = None

        # First, try to use cover.jpg from the same directory
        cover_jpg_path = os.path.join(
            os.path.dirname(file_path),
            "cover.jpg",
        )
        if os.path.exists(
            cover_jpg_path
        ):
            try:
                with open(
                    cover_jpg_path, "rb"
                ) as f:
                    cover_data = (
                        f.read()
                    )
                debug(
                    f"Using cover.jpg: {cover_jpg_path}"
                )
            except Exception as e:
                debug(
                    f"Failed to read cover.jpg: {e}"
                )

        # Fallback to embedded cover art in MP4
        if (
            cover_data is None
            and "covr" in mp4_file.tags
        ):
            cover_data = bytes(
                mp4_file.tags["covr"][0]
            )
            debug(
                "Using embedded MP4 cover art"
            )

        # Add cover art to FLAC if we have any
        if cover_data:
            picture = Picture()
            picture.data = cover_data
            picture.type = (
                3  # Cover (front)
            )

            # Determine MIME type
            if (
                cover_data[:4]
                == b"\xff\xd8\xff\xe0"
            ):
                picture.mime = (
                    "image/jpeg"
                )
            elif (
                cover_data[:8]
                == b"\x89PNG\r\n\x1a\n"
            ):
                picture.mime = (
                    "image/png"
                )
            else:
                picture.mime = "image/jpeg"  # Default fallback

            picture.desc = "Cover"
            picture.width = 0  # Will be filled by mutagen
            picture.height = 0  # Will be filled by mutagen
            picture.depth = 0  # Will be filled by mutagen

            # Clear existing pictures and add new one
            flac_file.clear_pictures()
            flac_file.add_picture(
                picture
            )
            debug(
                "Cover art embedded in FLAC"
            )
        else:
            debug(
                "No cover art found to embed"
            )

        # Save the FLAC file with metadata
        flac_file.save()

        debug(
            f"Successfully converted FLAC-in-MP4 to proper FLAC: {file_path}"
        )
        return True

    except Exception as e:
        error(
            f"Failed to convert FLAC: {e}"
        )
        return False


def _is_skip(
    finalpath: str, url: str
) -> bool:
    """Check if file should be skipped."""
    if not SETTINGS.checkExist:
        return False
    curSize = (
        tidal_dl.aigpy.file.getSize(
            finalpath
        )
    )
    if curSize <= 0:
        return False
    netSize = (
        tidal_dl.aigpy.net.getSize(url)
    )
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
    # Debug: Check if file exists before tagging
    if not os.path.exists(filepath):
        raise Exception(
            f"File does not exist: {filepath}"
        )

    obj = tidal_dl.aigpy.tag.TagTool(
        filepath,
        verbose=getattr(SETTINGS, 'verbose', False)
    )

    # Debug: Check if TagTool was created successfully
    if (
        not hasattr(obj, "_handle")
        or obj._handle is None
    ):
        raise Exception(
            f"TagTool failed to initialize for: {filepath}"
        )

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

    # Debug: Log before saving
    debug(
        f"Saving tags with coverpath: {coverpath}"
    )
    result = obj.save(coverpath)
    debug(f"Tag save result: {result}")


def downloadCover(album: Album):
    """Download album cover."""
    if album is None:
        return
    path = os.path.join(
        getAlbumPath(album),
        "cover.jpg"
    )
    url = TIDAL_API.getCoverUrl(
        album.cover, "1280", "1280"
    )
    tidal_dl.aigpy.net.downloadFile(
        url, path
    )


def downloadAlbumInfo(
    album: Album, tracks
):
    """Download album information text file."""
    if album is None:
        return

    path = getAlbumPath(album)
    tidal_dl.aigpy.path.mkdirs(path)

    info_path = os.path.join(path, "AlbumInfo.txt")
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
    tidal_dl.aigpy.file.write(
        info_path, infos, "w+"
    )


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
            error(
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
            error(
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
            success(video.title)
            return True
        else:
            error(
                f"DL Video[{video.title}] failed.{msg}"
            )
            return False, msg
    except Exception as e:
        error(
            f"DL Video[{video.title}] failed.{str(e)}"
        )
        return False, str(e)


def downloadTrack(
    track: Track,
    album: Album = None,
    playlist: Playlist = None,
    userProgress=None,
    partSize=1048576,
):
    """Download a single track."""
    debug(
        f"downloadTrack called for: {track.title}"
    )
    debug(f"album parameter: {album.title if album else 'None'}")
    debug(f"playlist parameter: {playlist.title if playlist else 'None'}")
    debug(f"track ID: {track.id if track else 'None'}")
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
            display_track_info(
                track, stream
            )

        if userProgress is not None:
            userProgress.updateStream(
                stream
            )

        # check exist
        file_already_exists = _is_skip(
            path, stream.url
        )
        if file_already_exists:
            Printf.success(
                tidal_dl.aigpy.path.getFileName(
                    path
                )
                + " (skip:already exists!)"
            )
            # Skip metadata processing for existing files in normal mode (unless verbose)
            if not getattr(SETTINGS, 'verbose', False):
                debug("File exists, skipping metadata processing in normal mode")
                # But still check if FLAC conversion is needed
                # (in case file was downloaded before conversion feature was added)
                skip_to_flac_conversion = True
            else:
                debug("File exists, but re-applying metadata due to verbose mode")
                skip_to_flac_conversion = False
        else:
            skip_to_flac_conversion = False
            # download
            logging.info(
                "[DL Track] name="
                + tidal_dl.aigpy.path.getFileName(
                    path
                )
                + "\nurl="
                + stream.url
            )

            tool = tidal_dl.aigpy.download.DownloadTool(
                path + ".part",
                stream.urls,
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
                error(
                    f"DL Track '{track.title}' failed: {str(err)}"
                )
                return False, str(err)

            # encrypted -> decrypt and remove encrypted file
            _decrypt_if_needed(
                stream,
                path + ".part",
                path,
            )

        # Skip metadata/lyrics processing if file exists and not in verbose mode
        if not skip_to_flac_conversion:
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

            try:
                _set_metadata(
                    track,
                    album,
                    path,
                    contributors,
                    lyrics,
                )
            except Exception as e:
                error(
                    f"Failed to set metadata for '{track.title}': {str(e)}"
                )
                # Continue with download success even if tagging fails

        # Auto-convert FLAC-in-MP4 to proper FLAC for Max quality (unless disabled)
        # Handle case where convertFlac setting might be None (from old config files)
        convert_flac = getattr(SETTINGS, "convertFlac", True)
        if convert_flac is None:
            convert_flac = True

        if (
            path.endswith(".flac")
            and convert_flac
            and SETTINGS.audioQuality
            == AudioQuality.Max
        ):
            if _convert_flac_inplace(
                path
            ):
                debug(
                    f"Converted to proper FLAC: {os.path.basename(path)}"
                )
            else:
                error(
                    "FLAC conversion failed!"
                )

        success(f"Successfully downloaded: {track.title}")

        return True, ""
    except Exception as e:
        error(
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
