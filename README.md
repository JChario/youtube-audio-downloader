# YouTube Playlist Downloader

A simple command-line tool to download YouTube playlists as MP3 files.

## Requirements

- Python 3
- yt-dlp
- ffmpeg

## Installation

1. Install yt-dlp:
```
pip install yt-dlp
```

2. Install ffmpeg:
```
winget install Gyan.FFmpeg
```
Restart your terminal after installing ffmpeg.

## Usage

Run `download.bat` (Windows) or:
```
python playlist_downloader.py
```

Paste your playlist URL when prompted. Files will be saved in a folder named after the playlist.

## Features

- Skips already downloaded songs (tracks in `downloaded.txt`)
- Continues if a video is unavailable
- Reports failed downloads at the end

## License

MIT
