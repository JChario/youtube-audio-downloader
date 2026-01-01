import yt_dlp
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Enable ANSI escape codes on Windows
if sys.platform == 'win32':
    os.system('')

def clear_lines(n):
    for _ in range(n):
        sys.stdout.write('\033[F\033[K')

class ProgressTracker:
    def __init__(self, total):
        self.errors = []
        self.total = total
        self.current = 0
        self.current_title = ""
        self.status = "Starting..."

    def set_current(self, index, title):
        self.current = index
        self.current_title = title[:50] + "..." if len(title) > 50 else title
        self.status = "Downloading..."
        self.display()

    def display(self, bar="--------------------", percent="0%", speed="", eta=""):
        clear_lines(4)
        print(f"Track: {self.current}/{self.total}")
        print(f"Title: {self.current_title}")
        print(f"  [{bar}] {percent} {speed} {eta}")
        print(f"Status: {self.status}")
        sys.stdout.flush()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()

            try:
                pct = float(percent.replace('%', ''))
                filled = int(pct / 5)
                bar = '#' * filled + '-' * (20 - filled)
            except:
                bar = '-' * 20

            self.status = "Downloading..."
            self.display(bar, percent, speed, f"ETA: {eta}" if eta else "")

        elif d['status'] == 'finished':
            self.status = "Converting to MP3..."
            self.display("####################", "100%", "", "")

    def postprocessor_hook(self, d):
        if d['status'] == 'finished':
            self.status = "Done!"
            self.display("####################", "100%", "", "")

def download_playlist(url, tracker):
    opts = {
        'format': 'bestaudio/best',
        'extract_audio': True,
        'audio_format': 'mp3',
        'audio_quality': 0,
        'outtmpl': os.path.join(SCRIPT_DIR, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
            },
        ],
        'writethumbnail': True,
        'ignoreerrors': True,
        'download_archive': os.path.join(SCRIPT_DIR, 'downloaded.txt'),
        'progress_hooks': [tracker.progress_hook],
        'postprocessor_hooks': [tracker.postprocessor_hook],
        'quiet': True,
        'no_warnings': True,
    }

    # Get playlist info
    print("Fetching playlist info...")
    info_opts = {'extract_flat': True, 'quiet': True}
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        playlist_title = info.get('title', 'Unknown Playlist')
        entries = info.get('entries', [])

    print(f"Playlist: {playlist_title}\n")

    # Print initial display lines
    print("")
    print("")
    print("")
    print("")

    for i, entry in enumerate(entries, 1):
        if entry is None:
            continue
        video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
        title = entry.get('title', 'Unknown')

        tracker.set_current(i, title)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            tracker.errors.append(f"{title}")
            tracker.status = f"Error!"
            tracker.display()

def verify_playlist(url):
    opts = {'extract_flat': True, 'quiet': True}
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

        # Get total first
        info_opts = {'extract_flat': True, 'quiet': True}
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            total = len(info.get('entries', []))

        tracker = ProgressTracker(total)
        download_playlist(url, tracker)

        print("\n" + "=" * 40)
        print("Download complete!")

        if tracker.errors:
            print(f"\nFailed downloads ({len(tracker.errors)}):")
            for err in tracker.errors:
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
