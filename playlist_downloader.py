import sys
import yt_dlp

def main():
    print("\n=== YouTube Playlist Downloader ===\n")

    url = input("Paste playlist URL: ").strip()

    if not url:
        print("No URL provided. Exiting.")
        return

    print("\nStarting download...\n")

    opts = {
        'format': 'bestaudio/best',
        'extract_audio': True,
        'audio_format': 'mp3',
        'audio_quality': 0,
        'outtmpl': '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        print("\nDone! All files downloaded.")
    except Exception as e:
        print(f"\nError during download: {e}")

if __name__ == "__main__":
    main()
