import os
import uuid
import threading
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import yt_dlp
import json
import time
import glob
import zipfile

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

progress_dict = {}
file_dict = {}

# ======================
# CONFIG YTDLP
# ======================
def get_ydl_opts(extra=None):

    opts = {
        "quiet": True,
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        }
    }

    if extra:
        opts.update(extra)

    return opts


# ======================
# INFO POST
# ======================
@app.route("/info", methods=["POST"])
def info():

    try:
        url = request.json.get("url")

        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)

        thumb = info.get("thumbnail")

        if not thumb and "entries" in info:
            thumb = info["entries"][0].get("thumbnail")

        return jsonify({
            "title": info.get("title", "Instagram Post"),
            "thumbnail": thumb
        })

    except Exception as e:
        print(e)
        return jsonify({"error": "Não foi possível ler o post"}), 400


# ======================
# DOWNLOAD THREAD
# ======================
def download_thread(url, pid):

    def hook(d):

        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()

            try:
                progress_dict[pid] = float(percent)
            except:
                pass

        elif d["status"] == "finished":
            progress_dict[pid] = 100

    folder = os.path.join(DOWNLOAD_FOLDER, pid)
    os.makedirs(folder, exist_ok=True)

    ydl_opts = get_ydl_opts({
        "outtmpl": f"{folder}/%(title)s.%(ext)s",
        "progress_hooks": [hook]
    })

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # verifica quantos arquivos baixou
        files = glob.glob(f"{folder}/*")

        # se tiver mais de 1 -> zipa
        if len(files) > 1:
            zip_path = f"{folder}.zip"

            with zipfile.ZipFile(zip_path, "w") as zipf:
                for f in files:
                    zipf.write(f, os.path.basename(f))

            file_dict[pid] = zip_path

        else:
            file_dict[pid] = files[0]

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        progress_dict[pid] = 100


# ======================
# START DOWNLOAD
# ======================
@app.route("/download", methods=["POST"])
def download():

    url = request.json.get("url")

    pid = str(uuid.uuid4())
    progress_dict[pid] = 0

    threading.Thread(
        target=download_thread,
        args=(url, pid),
        daemon=True
    ).start()

    return jsonify({"progress_id": pid})


# ======================
# FILE
# ======================
@app.route("/file/<pid>")
def file(pid):

    path = file_dict.get(pid)

    if not path:
        return "Arquivo não encontrado", 404

    return send_file(path, as_attachment=True)


# ======================
# SSE PROGRESS
# ======================
@app.route("/progress/<pid>")
def progress(pid):

    def generate():

        last = -1

        while True:

            progress = progress_dict.get(pid, 0)

            if progress != last:
                yield f"data: {json.dumps({'progress': progress})}\n\n"
                last = progress

            if progress >= 100:
                break

            time.sleep(0.7)

    return Response(generate(), mimetype="text/event-stream")


# ======================
# START SERVER
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
