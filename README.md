# Tidal-Media-Downloader

**Tidal-Media-Downloader** is fork of the command-line tool for downloading music and videos from Tidal with metadata tagging support.

## Command-Line Options

```
usage: tidal-dl [-h] [-V] [-v] [-g] [-l URL] [-o PATH] [-q {Normal,High,HiFi,Master,Max}] [-r {P240,P360,P480,P720,P1080}] [-j] [--no-flac-conversion]

Download music and videos from Tidal

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         enable verbose/debug output
  -g, --gui             Launch graphical user interface
  -l, --link URL        Tidal URL, ID, or file path to download
  -o, --output PATH     Download destination path
  -q, --quality {Normal,High,HiFi,Master,Max}
                        Audio quality for tracks
  -r, --resolution {P240,P360,P480,P720,P1080}
                        Video resolution
  -j, --json            Output item metadata as JSON (requires --link)
  --no-flac-conversion  Disable automatic FLAC conversion for Max quality downloads
```

## License

Apache License 2.0 - See [LICENSE](LICENSE) file

## Disclaimer

This tool is for educational purposes only. Please respect artists and support them by purchasing their music. Tidal is a trademark of Aspiro AB.

