import yt_dlp
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class ErrorLogger:
    def __init__(self):
        self.errors = []

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        self.errors.append(msg)

def download_playlist(url, logger):
    opts = {
        'format': 'bestaudio/best',
        'extract_audio': True,
        'audio_format': 'mp3',
        'audio_quality': 0,
        'outtmpl': os.path.join(SCRIPT_DIR, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
        'ignoreerrors': True,
        'download_archive': os.path.join(SCRIPT_DIR, 'downloaded.txt'),
        'logger': logger,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

def verify_playlist(url):
    """Check how many videos are in playlist vs how many we have in archive"""
    opts = {
        'extract_flat': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        total = len(info.get('entries', []))

    archive_path = os.path.join(SCRIPT_DIR, 'downloaded.txt')
    downloaded = 0
    if os.path.exists(archive_path):
        with open(archive_path, 'r') as f:
            downloaded = len(f.readlines())

    return total, downloaded

def main():
    print("\n=== YouTube Playlist Downloader ===\n")

    url = input("Paste playlist URL: ").strip()

    if not url:
        print("No URL provided. Exiting.")
        return

    while True:
        print("\nStarting download...\n")

        logger = ErrorLogger()
        download_playlist(url, logger)

        print("\n" + "=" * 40)
        print("Download complete!")

        if logger.errors:
            print(f"\nFailed downloads ({len(logger.errors)}):")
            for err in logger.errors:
                print(f"  - {err}")

        print("\nOptions:")
        print("  [V] Verify playlist (check missing songs)")
        print("  [R] Retry download")
        print("  [N] New playlist")
        print("  [Q] Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == 'v':
            print("\nVerifying...")
            total, downloaded = verify_playlist(url)
            missing = total - downloaded
            print(f"  Playlist has {total} videos")
            print(f"  Downloaded: {downloaded}")
            if missing > 0:
                print(f"  Missing: {missing}")
            else:
                print("  All videos accounted for!")
        elif choice == 'r':
            continue
        elif choice == 'n':
            url = input("\nPaste new playlist URL: ").strip()
            if not url:
                print("No URL provided.")
            else:
                continue
        elif choice == 'q':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
