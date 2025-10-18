#!/usr/bin/env python3
"""
FLAC Converter for Tidal Media Downloader

This module provides utilities to convert FLAC-in-MP4 files to proper FLAC files
with preserved metadata and cover art.
"""

import os
import subprocess
import shutil
from mutagen import flac, mp4
from mutagen.flac import Picture
from tidal_dl.logger import info, error, debug


def extract_flac_with_metadata(mp4_flac_path: str, output_path: str = None) -> str:
    """
    Extract FLAC audio from MP4 container and preserve all metadata and cover art.
    
    Args:
        mp4_flac_path: Path to the FLAC-in-MP4 file
        output_path: Optional output path. If None, replaces .flac extension with _proper.flac
    
    Returns:
        Path to the converted FLAC file
    """
    if output_path is None:
        base = mp4_flac_path.rsplit('.', 1)[0]
        output_path = f"{base}_proper.flac"
    
    try:
        # Step 1: Extract raw FLAC audio using ffmpeg to stdout (in-memory)
        debug(f"Extracting FLAC audio from {mp4_flac_path}")
        ffmpeg_process = subprocess.run([
            'ffmpeg', '-i', mp4_flac_path,
            '-vn',  # No video
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-f', 'flac',  # Force FLAC format
            '-'  # Output to stdout
        ], check=True, capture_output=True)
        
        flac_audio_data = ffmpeg_process.stdout
        debug(f"Extracted {len(flac_audio_data)} bytes of FLAC audio data")
        
        # Step 2: Write FLAC data to final output file
        with open(output_path, 'wb') as f:
            f.write(flac_audio_data)
        
        # Step 3: Read metadata from original MP4 file
        mp4_file = mp4.MP4(mp4_flac_path)
        
        # Step 4: Open the newly created FLAC file and add metadata
        flac_file = flac.FLAC(output_path)
        
        # Convert MP4 metadata to FLAC format
        if '\xa9nam' in mp4_file.tags:
            flac_file['TITLE'] = mp4_file.tags['\xa9nam']
        if '\xa9alb' in mp4_file.tags:
            flac_file['ALBUM'] = mp4_file.tags['\xa9alb']
        if '\xa9ART' in mp4_file.tags:
            flac_file['ARTIST'] = mp4_file.tags['\xa9ART']
        if 'aART' in mp4_file.tags:
            flac_file['ALBUMARTIST'] = mp4_file.tags['aART']
        if '\xa9day' in mp4_file.tags:
            flac_file['DATE'] = mp4_file.tags['\xa9day']
        if '\xa9gen' in mp4_file.tags:
            flac_file['GENRE'] = mp4_file.tags['\xa9gen']
        if '\xa9wrt' in mp4_file.tags:
            flac_file['COMPOSER'] = mp4_file.tags['\xa9wrt']
        if 'cprt' in mp4_file.tags:
            flac_file['COPYRIGHT'] = mp4_file.tags['cprt']
        if '\xa9lyr' in mp4_file.tags:
            flac_file['LYRICS'] = mp4_file.tags['\xa9lyr']
        
        # Handle track/disc numbers
        if 'trkn' in mp4_file.tags:
            track_info = mp4_file.tags['trkn'][0]
            if len(track_info) >= 1:
                flac_file['TRACKNUMBER'] = str(track_info[0])
            if len(track_info) >= 2 and track_info[1] > 0:
                flac_file['TRACKTOTAL'] = str(track_info[1])
        
        if 'disk' in mp4_file.tags:
            disc_info = mp4_file.tags['disk'][0]
            if len(disc_info) >= 1:
                flac_file['DISCNUMBER'] = str(disc_info[0])
            if len(disc_info) >= 2 and disc_info[1] > 0:
                flac_file['DISCTOTAL'] = str(disc_info[1])
        
        # Step 4: Add cover art - prioritize cover.jpg in same directory
        cover_data = None
        
        # First, try to use cover.jpg from the same directory
        cover_jpg_path = os.path.join(os.path.dirname(mp4_flac_path), 'cover.jpg')
        if os.path.exists(cover_jpg_path):
            try:
                with open(cover_jpg_path, 'rb') as f:
                    cover_data = f.read()
                debug(f"Using cover.jpg: {cover_jpg_path}")
            except Exception as e:
                error(f"Failed to read cover.jpg: {e}")
        
        # Fallback to embedded cover art in MP4
        if cover_data is None and 'covr' in mp4_file.tags:
            cover_data = bytes(mp4_file.tags['covr'][0])
            debug("Using embedded MP4 cover art")
        
        # Add cover art to FLAC if we have any
        if cover_data:
            # Create FLAC picture block
            picture = Picture()
            picture.data = cover_data
            picture.type = 3  # Cover (front)
            
            # Determine MIME type
            if cover_data[:4] == b'\xff\xd8\xff\xe0':
                picture.mime = 'image/jpeg'
            elif cover_data[:8] == b'\x89PNG\r\n\x1a\n':
                picture.mime = 'image/png'
            else:
                picture.mime = 'image/jpeg'  # Default fallback
            
            picture.desc = 'Cover'
            picture.width = 0  # Will be filled by mutagen
            picture.height = 0  # Will be filled by mutagen
            picture.depth = 0  # Will be filled by mutagen
            
            # Clear existing pictures and add new one
            flac_file.clear_pictures()
            flac_file.add_picture(picture)
            debug("Cover art embedded in FLAC")
        else:
            debug("No cover art found to embed")
        
        # Save the FLAC file with metadata
        flac_file.save()
        
        debug(f"Successfully converted {mp4_flac_path} to {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        error(f"FFmpeg failed: {e}")
        # Clean up output file if it was partially created
        if os.path.exists(output_path):
            os.remove(output_path)
        raise
    except Exception as e:
        error(f"Conversion failed: {e}")
        # Clean up output file if it was partially created
        if os.path.exists(output_path):
            os.remove(output_path)
        raise
