import os
import uuid
import threading
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import json
import time

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

progress_dict = {}

# ==============================
# COOKIES VIA ENV (RENDER SAFE)
# ==============================
COOKIE_FILE = "/tmp/cookies.txt"

def ensure_cookie_file():
    cookies = os.environ.get("YOUTUBE_COOKIES")
    if cookies:
        with open(COOKIE_FILE, "w") as f:
            f.write(cookies)

ensure_cookie_file()


# ==============================
# CONFIG YT-DLP
# ==============================
def get_ydl_opts(extra_opts=None):

    opts = {
        "quiet": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,

        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        },

        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },

        "cookiefile": COOKIE_FILE if os.path.exists(COOKIE_FILE) else None
    }

    if extra_opts:
        opts.update(extra_opts)

    return opts


# ==============================
# INFO VIDEO
# ==============================
@app.route("/info", methods=["POST"])
def info():
    try:
        data = request.json
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL inválida"}), 400

        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return jsonify({"error": "Não foi possível obter info"}), 400

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration")
        })

    except Exception as e:
        print("ERRO INFO:", e)
        return jsonify({"error": "YouTube bloqueou ou vídeo inválido"}), 400


# ==============================
# DOWNLOAD THREAD
# ==============================
def download_thread(url, type_, progress_id):

    def hook(d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()
            try:
                progress_dict[progress_id] = float(percent)
            except:
                pass

        elif d["status"] == "finished":
            progress_dict[progress_id] = 100

    filename = os.path.join(DOWNLOAD_FOLDER, f"{progress_id}.%(ext)s")

    if type_ == "mp3":

        ydl_opts = get_ydl_opts({
            "format": "bestaudio/best",
            "outtmpl": filename,
            "progress_hooks": [hook],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        })

    else:

        ydl_opts = get_ydl_opts({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": filename,
            "progress_hooks": [hook]
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("ERRO DOWNLOAD:", e)
        progress_dict[progress_id] = 100


# ==============================
# START DOWNLOAD
# ==============================
@app.route("/download", methods=["POST"])
def download():

    data = request.json
    url = data.get("url")
    type_ = data.get("type", "mp4")

    if not url:
        return jsonify({"error": "URL inválida"}), 400

    progress_id = str(uuid.uuid4())
    progress_dict[progress_id] = 0

    thread = threading.Thread(
        target=download_thread,
        args=(url, type_, progress_id),
        daemon=True
    )
    thread.start()

    return jsonify({"progress_id": progress_id})


# ==============================
# PROGRESS SSE
# ==============================
@app.route("/progress/<progress_id>")
def progress(progress_id):

    def generate():
        last = -1

        while True:
            progress = progress_dict.get(progress_id, 0)

            if progress != last:
                yield f"data: {json.dumps({'progress': progress})}\n\n"
                last = progress

            if progress >= 100:
                break

            time.sleep(0.7)

    return Response(generate(), mimetype="text/event-stream")


# ==============================
# START SERVER
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
