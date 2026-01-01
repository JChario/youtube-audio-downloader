import yt_dlp

def main():
    print("\n=== YouTube Playlist Downloader ===\n")

    url = input("Paste playlist URL: ").strip()

    if not url:
        print("No URL provided. Exiting.")
        return

    while True:
        print("\nStarting download...\n")

        failed = []

        def hook(d):
            if d['status'] == 'error':
                failed.append(d.get('info_dict', {}).get('webpage_url', 'Unknown URL'))

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
            'ignoreerrors': True,
            'download_archive': 'downloaded.txt',
            'progress_hooks': [hook],
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        print("\n" + "=" * 40)
        print("Done!")

        if failed:
            print(f"\nFailed to download {len(failed)} video(s):")
            for f in failed:
                print(f"  - {f}")

            print("\nOptions:")
            print("  [R] Retry downloading the playlist")
            print("  [Q] Quit")

            choice = input("\nChoice: ").strip().lower()
            if choice == 'r':
                continue
            else:
                break
        else:
            print("All files downloaded successfully.")
            break

if __name__ == "__main__":
    main()
