import os
import uuid
import threading
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import yt_dlp
import json
import time
import glob

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

progress_dict = {}
file_dict = {}

# ==============================
# CONFIG yt-dlp (INSTAGRAM)
# ==============================
def get_ydl_opts(extra_opts=None):

    opts = {
        "quiet": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,

        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        }
    }

    if extra_opts:
        opts.update(extra_opts)

    return opts


# ==============================
# INFO POST
# ==============================
@app.route("/info", methods=["POST"])
def info():

    try:
        data = request.json
        url = data.get("url")

        if not url or "instagram.com" not in url:
            return jsonify({"error": "Link inválido do Instagram"}), 400

        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title", "Instagram Post"),
            "thumbnail": info.get("thumbnail")
        })

    except Exception as e:
        print("INFO ERROR:", e)
        return jsonify({"error": "Não foi possível obter informações do post."}), 400


# ==============================
# DOWNLOAD THREAD
# ==============================
def download_thread(url, progress_id):

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

    ydl_opts = get_ydl_opts({
        "format": "best",
        "outtmpl": filename,
        "progress_hooks": [hook]
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # salva arquivo final
        files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{progress_id}.*"))
        if files:
            file_dict[progress_id] = files[0]

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        progress_dict[progress_id] = 100


# ==============================
# START DOWNLOAD
# ==============================
@app.route("/download", methods=["POST"])
def download():

    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL inválida"}), 400

    progress_id = str(uuid.uuid4())
    progress_dict[progress_id] = 0

    thread = threading.Thread(
        target=download_thread,
        args=(url, progress_id),
        daemon=True
    )
    thread.start()

    return jsonify({"progress_id": progress_id})


# ==============================
# DOWNLOAD FILE
# ==============================
@app.route("/file/<progress_id>")
def file(progress_id):

    path = file_dict.get(progress_id)

    if not path:
        return jsonify({"error": "Arquivo não encontrado"}), 404

    return send_file(path, as_attachment=True)


# ==============================
# SSE PROGRESS
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
