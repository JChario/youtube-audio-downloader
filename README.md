# YouTube Playlist Downloader

A simple command-line tool to download YouTube playlists as MP3 files with metadata.

## Download

### Option 1: Standalone Executable (Easiest)
Download `YouTubePlaylistDownloader.exe` from [Releases](https://github.com/JChario/youtube-audio-downloader/releases)

> **Note:** Windows may show a SmartScreen warning because the exe is unsigned. Click "More info" → "Run anyway". This is safe - the code is open source.

You still need FFmpeg installed:
```
winget install Gyan.FFmpeg
```

### Option 2: Run with Python
1. Install requirements:
```
pip install yt-dlp
winget install Gyan.FFmpeg
```

2. Run:
```
python playlist_downloader.py
```
Or double-click `download.bat`

## Features

- Download entire playlists as high-quality MP3
- Compact progress display
- Skip already downloaded tracks
- Verify playlist completion
- Update metadata on existing files
- Embed thumbnails as album art

## Usage

1. Run the app
2. Choose an option from the menu:
   - **[D] Download** - Download a new playlist
   - **[V] Verify** - Check if all tracks are downloaded
   - **[M] Metadata** - Update metadata for existing files
   - **[Q] Quit**
3. Paste your playlist URL

Files are saved in a folder named after the playlist.

## Authentication (if needed)

If YouTube blocks requests, export your cookies:
1. Install "Get cookies.txt LOCALLY" browser extension
2. Go to youtube.com (logged in)
3. Export cookies and save as `cookies.txt` in the app folder

## License

MIT
