from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import os
import uuid
import json
import threading
import time
import shutil

app = Flask(__name__)
CORS(app)

BASE_PATH = "downloads"
os.makedirs(BASE_PATH, exist_ok=True)

progress_store = {}

# =========================
# CONFIG GLOBAL yt-dlp
# =========================
def base_ydl_opts():

    return {
        "quiet": True,
        "no_warnings": True,

        "extractor_args": {
            "youtube": {
                "player_client": ["web"],
                "skip": ["dash", "hls"]
            }
        },

        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        },

        "nocheckcertificate": True,
        "ignoreerrors": True
    }

# =========================
# HOOK PROGRESSO
# =========================
def get_ydl_opts(progress_id, extra_opts=None):

    def hook(d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()
            progress_store[progress_id] = percent

        elif d["status"] == "finished":
            progress_store[progress_id] = "100"

    opts = base_ydl_opts()
    opts["progress_hooks"] = [hook]

    if extra_opts:
        opts.update(extra_opts)

    return opts

# =========================
# SSE PROGRESSO
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

            if value in ["100", "error"]:
                break

            time.sleep(0.5)

    return Response(stream(), mimetype="text/event-stream")

# =========================
# INFO VIDEO
# =========================
@app.route("/info", methods=["POST"])
def info():

    data = request.get_json() or {}
    url = data.get("url")

    if not url:
        return jsonify({"error": "Link inválido"}), 400

    try:
        with yt_dlp.YoutubeDL(base_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return jsonify({
                "error": "Não foi possível obter informações do vídeo."
            }), 429

        return jsonify({
            "title": info.get("title", "Sem título"),
            "thumbnail": info.get("thumbnail", ""),
            "playlist": "entries" in info
        })

    except Exception as e:
        print("INFO ERROR:", e)
        return jsonify({
            "error": "YouTube bloqueou temporariamente este servidor. Tente novamente em alguns minutos."
        }), 429

# =========================
# DOWNLOAD
# =========================
@app.route("/download", methods=["POST"])
def download():

    data = request.get_json() or {}
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
                    }]
                })

            else:
                opts = get_ydl_opts(progress_id, {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "outtmpl": os.path.join(temp_path, "%(title)s.%(ext)s")
                })

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        except Exception as e:
            print("DOWNLOAD ERROR:", e)
            progress_store[progress_id] = "error"
            return

        # limpa arquivos depois de 10 minutos
        time.sleep(600)
        shutil.rmtree(temp_path, ignore_errors=True)

    threading.Thread(target=worker, daemon=True).start()

    return jsonify({"progress_id": progress_id})

# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
