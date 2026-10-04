# Grogu MP3

Local PWA: paste a YouTube / YT Music link, get an MP3. Conversion runs on your machine via yt-dlp + ffmpeg.

## Setup
1. Install ffmpeg (`brew install ffmpeg` / `winget install ffmpeg` / `sudo apt install ffmpeg`)
2. `pip install -r requirements.txt`
3. `python server.py`
4. Open http://localhost:5173 and, optionally, use the browser's Install button.

## Notes
- The server binds to 127.0.0.1 only, so it isn't reachable from other devices.
- Keep yt-dlp current (`pip install -U yt-dlp`); YouTube changes often break old versions.
- Single videos only (`--no-playlist`). Remove that flag in server.py to allow playlists (you'd need to zip the results).
- Only download content you own or have permission to use. Downloading from YouTube generally violates its Terms of Service.
