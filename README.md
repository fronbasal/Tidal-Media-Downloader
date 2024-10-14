# Tidal-Media-Downloader

> **MAJOR REWRITE NOTICE**: This fork has undergone a complete architectural refactoring to follow modern Python best practices. While it aims for 100% CLI compatibility with the original, **there may be breaking changes**! Also ships without the GUI.

**Tidal-Media-Downloader** is a command-line tool for downloading music and videos from Tidal with metadata tagging support.

## Installation

## Quick Start

```bash
# Interactive mode (legacy behavior maintained)
tidal-dl

# Download a track
tidal-dl -l "https://tidal.com/browse/track/70973230"

# Download with quality setting
tidal-dl -l "https://tidal.com/browse/track/70973230" -q Master

# Get JSON metadata
tidal-dl -l "https://tidal.com/browse/track/70973230" -j

# Download playlist
tidal-dl -l "https://tidal.com/browse/playlist/UUID"

# Set output directory
tidal-dl -o "/path/to/downloads" -l "URL"
```

## Features

- ✅ Download albums, tracks, videos, playlists, artist catalogs
- ✅ Automatic metadata tagging (album art, artist, title, etc.)
- ✅ Multiple quality options: Normal, High, HiFi, Master, Max
- ✅ Video resolution selection: P240, P360, P480, P720, P1080
- ✅ Configurable path formatting with templates
- ✅ Multi-threaded downloads (optional)
- ✅ Progress indicators
- ✅ Check for existing files before downloading
- ✅ Lyrics download (.lrc files)
- ✅ Album info text files

## Command-Line Options

```
usage: tidal-dl [-h] [-v] [-l URL] [-o PATH] [-q QUALITY] [-r RESOLUTION] 
                [-j] [-n]

Download music and videos from Tidal

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -l URL, --link URL    Tidal URL, ID, or file path to download
  -o PATH, --output PATH
                        Download destination path
  -q QUALITY, --quality QUALITY
                        Audio quality: Normal, High, HiFi, Master, Max
  -r RESOLUTION, --resolution RESOLUTION
                        Video resolution: P240, P360, P480, P720, P1080
  -j, --json            Output item metadata as JSON (requires --link)
  -n, --non-interactive
                        Non-interactive mode with JSON output
```

## Configuration

Configuration is stored in `~/.tidal-dl/settings.json`. You can modify:

- Download path
- Audio/video quality defaults
- Path naming templates
- Behavior flags (check existing, save covers, etc.)

### Path Format Templates

#### Album Folder Format
```
{ArtistName}/{Flag} {AlbumTitle} [{AlbumID}] [{AlbumYear}]
```

#### Track File Format
```
{TrackNumber} - {ArtistName} - {TrackTitle}{ExplicitFlag}
```

#### Available Tags

| Tag               | Description                          | Example                    |
|-------------------|--------------------------------------|----------------------------|
| {ArtistName}      | Primary artist                       | The Beatles                |
| {AlbumArtistName} | Album artist                         | The Beatles                |
| {Flag}            | Quality flags (M/A/E)               | [M] (Master)               |
| {AlbumID}         | Tidal album ID                       | 55163243                   |
| {AlbumYear}       | Release year                         | 1963                       |
| {AlbumTitle}      | Album name                           | Please Please Me           |
| {TrackNumber}     | Track number                         | 01                         |
| {TrackTitle}      | Track name                           | I Saw Her Standing There   |
| {ExplicitFlag}    | Explicit content indicator           | (Explicit)                 |
| {AudioQuality}    | Audio quality                        | LOSSLESS                   |
| {Duration}        | Track/album duration                 | 3:45                       |

## Authentication

On first run, you'll need to authenticate:

1. Run `tidal-dl` 
2. Follow the URL provided to authorize the app
3. Credentials are saved for future use in `~/.tidal-dl/token.json`

You can also login with an access token:
```bash
tidal-dl
# Choose option 3: Login by access token
```

## What's Different in This Refactor?

### Improved
- 🎯 **Modern Python**: Type hints, dataclasses, proper OOP patterns
- 🎯 **Better Error Handling**: Specific exception types, proper logging
- 🎯 **Clean Architecture**: Separation of concerns (API, Download, Config, CLI)
- 🎯 **Maintainability**: PEP 8 compliant, documented, testable
- 🎯 **Packaging**: Proper `pyproject.toml`, automated releases

### Removed
- ❌ **GUI Interface**: Use original repo for GUI version
- ❌ **Multi-language Support**: English only (for now)
- ❌ **Colored Terminal Output**: Standard logging instead

### Compatibility
- ✅ All CLI arguments work identically to original
- ✅ Config file format migration supported
- ✅ Same download behavior and file naming
- ⚠️ Interactive menu simplified (no color, English only)

## Development

### Project Structure
```
tidal-dl/
├── src/
│   └── tidal_dl/
│       ├── __init__.py
│       ├── api_client.py      # Tidal API wrapper
│       ├── app.py             # Application orchestrator
│       ├── cli.py             # CLI argument parsing
│       ├── config.py          # Configuration management
│       ├── download_manager.py # Download logic
│       ├── path_builder.py    # Path formatting
│       ├── models.py          # Data models
│       ├── enums.py           # Enumerations
│       └── decryption.py      # Audio decryption
├── tests/                     # Unit tests
├── pyproject.toml            # Modern Python packaging
├── setup.py                  # Backward compatibility
└── README.md
```

### Running Tests
```bash
pip install -e ".[dev]"
pytest
```

### Building
```bash
python -m build
```

## Known Issues

- Interactive menu lacks colored output (planned)
- Multi-language support not yet re-implemented
- Some edge cases in path formatting may differ slightly

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `flake8` and `mypy` pass
5. Submit a pull request

## License

Apache License 2.0 - See [LICENSE](LICENSE) file

## Credits

- Original: [yaronzz/Tidal-Media-Downloader](https://github.com/yaronzz/Tidal-Media-Downloader)
- This fork: [fronbasal/Tidal-Media-Downloader](https://github.com/fronbasal/Tidal-Media-Downloader)

## Disclaimer

This tool is for educational purposes only. Please respect artists and support them by purchasing their music. Tidal is a trademark of Aspiro AB.

