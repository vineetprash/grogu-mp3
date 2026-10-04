"""Local YouTube / YT Music -> MP3 server. Binds to localhost only."""
import io, re, shutil, subprocess, tempfile
from pathlib import Path
from urllib.parse import quote, urlparse
from flask import Flask, jsonify, request, send_file, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")
HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}

@app.get("/")
def index():
    return send_from_directory("static", "index.html")

@app.post("/api/convert")
def convert():
    url = (request.get_json(silent=True) or {}).get("url", "").strip()
    host = urlparse(url).hostname or ""
    if host not in HOSTS:
        return jsonify(error="Paste a youtube.com, music.youtube.com or youtu.be link."), 400
    if not shutil.which("ffmpeg"):
        return jsonify(error="ffmpeg isn't installed or isn't on your PATH."), 500

    tmp = Path(tempfile.mkdtemp(prefix="ytmp3-"))
    try:
        proc = subprocess.run(
            ["yt-dlp", "--no-playlist", "-x", "--audio-format", "mp3", "--audio-quality", "0",
             "--embed-metadata", "--embed-thumbnail", "--convert-thumbnails", "jpg",
             "--restrict-filenames", "-o", str(tmp / "%(title).150B.%(ext)s"), url],
            capture_output=True, text=True, timeout=600)
        files = list(tmp.glob("*.mp3"))
        if proc.returncode != 0 or not files:
            msg = (proc.stderr.strip().splitlines() or ["Conversion failed."])[-1]
            return jsonify(error=re.sub(r"^ERROR:\s*", "", msg)), 422
        data = io.BytesIO(files[0].read_bytes())
        name = files[0].name
    except subprocess.TimeoutExpired:
        return jsonify(error="Timed out after 10 minutes."), 504
    except FileNotFoundError:
        return jsonify(error="yt-dlp isn't installed. Run: pip install -r requirements.txt"), 500
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    resp = send_file(data, mimetype="audio/mpeg", download_name=name)
    resp.headers["X-Filename"] = quote(name)
    resp.headers["Access-Control-Expose-Headers"] = "X-Filename"
    return resp

if __name__ == "__main__":
    print("Open http://localhost:5173")
    app.run(host="0.0.0.0", port=5173)
