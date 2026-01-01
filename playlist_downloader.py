import yt_dlp
import os
import sys
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(SCRIPT_DIR, 'cookies.txt')

# Enable ANSI escape codes on Windows
if sys.platform == 'win32':
    os.system('')

def get_cookie_opts():
    """Return cookie options if cookies.txt exists"""
    if os.path.exists(COOKIES_FILE):
        return {'cookiefile': COOKIES_FILE}
    return {}

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
        **get_cookie_opts(),
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
    info_opts = {'extract_flat': True, 'quiet': True, **get_cookie_opts()}
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
    print("Fetching playlist info...")
    opts = {'extract_flat': True, 'quiet': True, **get_cookie_opts()}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        playlist_title = info.get('title', 'Unknown Playlist')
        entries = info.get('entries', [])
        total = len(entries)

    archive_path = os.path.join(SCRIPT_DIR, 'downloaded.txt')
    downloaded_ids = set()
    if os.path.exists(archive_path):
        with open(archive_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    downloaded_ids.add(parts[1])

    missing = []
    for entry in entries:
        if entry is None:
            continue
        video_id = entry.get('id')
        if video_id and video_id not in downloaded_ids:
            missing.append(entry.get('title', video_id))

    print(f"\nPlaylist: {playlist_title}")
    print(f"  Total tracks: {total}")
    print(f"  Downloaded: {total - len(missing)}")

    if missing:
        print(f"  Missing: {len(missing)}")
        print("\nMissing tracks:")
        for title in missing[:10]:
            print(f"  - {title}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
    else:
        print("  All tracks downloaded!")

    return len(missing) == 0

def update_metadata(url):
    """Update metadata for existing MP3 files"""
    import subprocess
    import urllib.request
    import tempfile

    print("Fetching playlist info...")

    # Get playlist with flat extraction (faster, no auth needed)
    info_opts = {'extract_flat': True, 'quiet': True, **get_cookie_opts()}
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        playlist_title = info.get('title', 'Unknown Playlist')
        entries = info.get('entries', [])
        total = len(entries)

    playlist_dir = os.path.join(SCRIPT_DIR, playlist_title)

    if not os.path.exists(playlist_dir):
        print(f"Playlist folder not found: {playlist_dir}")
        return

    print(f"Playlist: {playlist_title}")
    print(f"Updating metadata for {total} tracks...\n")

    # Print initial lines
    print("")
    print("")

    updated = 0
    for i, entry in enumerate(entries, 1):
        if entry is None:
            continue

        title = entry.get('title', 'Unknown')
        artist = entry.get('uploader', entry.get('channel', 'Unknown Artist'))
        video_id = entry.get('id', '')
        # Construct thumbnail URL from video ID
        thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ''
        track_num = str(i).zfill(3)

        clear_lines(2)
        print(f"[{i}/{total}] {title[:50]}...")
        print("Updating metadata...")
        sys.stdout.flush()

        # Find matching MP3 file
        mp3_file = None
        for f in os.listdir(playlist_dir):
            if f.endswith('.mp3') and f.startswith(f"{track_num} - "):
                mp3_file = os.path.join(playlist_dir, f)
                break

        # Also try with 2-digit prefix
        if not mp3_file:
            track_num_2 = str(i).zfill(2)
            for f in os.listdir(playlist_dir):
                if f.endswith('.mp3') and f.startswith(f"{track_num_2} - "):
                    mp3_file = os.path.join(playlist_dir, f)
                    break

        if not mp3_file:
            continue

        try:
            # Download thumbnail to temp file
            thumb_file = None
            if thumbnail_url:
                thumb_file = os.path.join(tempfile.gettempdir(), f"thumb_{i}.jpg")
                try:
                    urllib.request.urlretrieve(thumbnail_url, thumb_file)
                except:
                    thumb_file = None

            # Create temp output file
            temp_output = mp3_file + ".temp.mp3"

            # Build ffmpeg command
            cmd = ['ffmpeg', '-y', '-i', mp3_file]

            if thumb_file and os.path.exists(thumb_file):
                cmd.extend(['-i', thumb_file])
                cmd.extend(['-map', '0:a', '-map', '1:0'])
                cmd.extend(['-c:v', 'mjpeg'])
                cmd.extend(['-disposition:v', 'attached_pic'])

            cmd.extend(['-c:a', 'copy'])
            cmd.extend(['-id3v2_version', '3'])
            cmd.extend(['-metadata', f'title={title}'])
            cmd.extend(['-metadata', f'artist={artist}'])
            cmd.extend(['-metadata', f'album={playlist_title}'])
            cmd.extend(['-metadata', f'track={i}/{total}'])
            cmd.append(temp_output)

            # Run ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and os.path.exists(temp_output):
                os.remove(mp3_file)
                os.rename(temp_output, mp3_file)
                updated += 1
            else:
                if os.path.exists(temp_output):
                    os.remove(temp_output)

            # Cleanup thumbnail
            if thumb_file and os.path.exists(thumb_file):
                os.remove(thumb_file)

        except Exception as e:
            pass

    clear_lines(2)
    print(f"Metadata update complete! Updated {updated}/{total} files.")
    print("")

def show_cookie_help():
    print("\n" + "=" * 50)
    print("AUTHENTICATION REQUIRED")
    print("=" * 50)
    print("\nYouTube is blocking requests. To fix this:")
    print("\n1. Install 'Get cookies.txt LOCALLY' extension in Brave")
    print("2. Go to youtube.com (make sure you're logged in)")
    print("3. Click the extension and export cookies")
    print("4. Save as 'cookies.txt' in:")
    print(f"   {SCRIPT_DIR}")
    print("\nThen try again.")
    print("=" * 50)

def main():
    print("\n=== YouTube Playlist Downloader ===\n")

    if os.path.exists(COOKIES_FILE):
        print("[Using cookies.txt for authentication]\n")

    while True:
        print("Main Menu:")
        print("  [D] Download playlist")
        print("  [V] Verify playlist")
        print("  [M] Update metadata")
        print("  [Q] Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == 'd':
            url = input("\nPaste playlist URL: ").strip()
            if not url:
                print("No URL provided.")
                continue

            try:
                # Get total first
                info_opts = {'extract_flat': True, 'quiet': True, **get_cookie_opts()}
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

                print("")

            except Exception as e:
                if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
                    show_cookie_help()
                else:
                    print(f"\nError: {e}")
                print("")

        elif choice == 'v':
            url = input("\nPaste playlist URL: ").strip()
            if not url:
                print("No URL provided.")
                continue
            try:
                verify_playlist(url)
            except Exception as e:
                if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
                    show_cookie_help()
                else:
                    print(f"\nError: {e}")
            print("")

        elif choice == 'm':
            url = input("\nPaste playlist URL: ").strip()
            if not url:
                print("No URL provided.")
                continue
            try:
                update_metadata(url)
            except Exception as e:
                if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
                    show_cookie_help()
                else:
                    print(f"\nError: {e}")
            print("")

        elif choice == 'q':
            break

        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    main()
