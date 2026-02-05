from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import yt_dlp
import os
import uuid
import shutil
import json
import threading
import time

app = Flask(__name__)
CORS(app)

BASE_PATH = "downloads"
os.makedirs(BASE_PATH, exist_ok=True)

# Guarda progresso em memória
progress_store = {}

# =========================
# yt-dlp com hook de progresso
# =========================
def get_ydl_opts(progress_id, extra_opts=None):

    def progress_hook(d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()
            progress_store[progress_id] = percent

        elif d["status"] == "finished":
            progress_store[progress_id] = "100"

    opts = {
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_hook],
    }

    if extra_opts:
        opts.update(extra_opts)

    return opts


# =========================
# SSE – envia progresso
# =========================
@app.route("/progress/<pid>")
def progress(pid):

    def stream():
        last = None
        while True:
            value = progress_store.get(pid, "0")

            if value != last:
                yield f"data: {json.dumps({'progress': value})}\n\n"
                last = value

            if value == "100":
                break

            time.sleep(0.5)

    return Response(stream(), mimetype="text/event-stream")


# =========================
# INFO (buscar dados)
# =========================
@app.route("/info", methods=["POST"])
def info():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Link inválido"}), 400

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "playlist": "entries" in info
        })

    except Exception as e:
        print("INFO ERROR:", e)
        return jsonify({"error": "Link inválido ou bloqueado"}), 400


# =========================
# DOWNLOAD (inicia download)
# =========================
@app.route("/download", methods=["POST"])
def download():

    data = request.get_json()
    url = data.get("url")
    tipo = data.get("type")

    if not url or tipo not in ["audio", "video"]:
        return jsonify({"error": "Parâmetros inválidos"}), 400

    progress_id = str(uuid.uuid4())
    progress_store[progress_id] = "0"

    temp_path = os.path.join(BASE_PATH, progress_id)
    os.makedirs(temp_path, exist_ok=True)

    def worker():
        try:
            if tipo == "audio":
                opts = get_ydl_opts(progress_id, {
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(temp_path, "%(title)s.%(ext)s"),
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }],
                })
            else:
                opts = get_ydl_opts(progress_id, {
                    "format": "bestvideo+bestaudio/best",
                    "outtmpl": os.path.join(temp_path, "%(title)s.%(ext)s"),
                    "merge_output_format": "mp4",
                })

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        except Exception as e:
            print("DOWNLOAD ERROR:", e)
            progress_store[progress_id] = "0"

    threading.Thread(target=worker).start()

    return jsonify({"progress_id": progress_id})


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
