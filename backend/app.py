from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import zipfile
import shutil

app = Flask(__name__)
CORS(app)

BASE_PATH = "downloads"
os.makedirs(BASE_PATH, exist_ok=True)

# 🔹 BUSCAR INFO
@app.route("/info", methods=["POST"])
def info():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Link não informado"}), 400

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        if "entries" in info:
            return jsonify({
                "playlist": True,
                "title": info["title"],
                "thumbnail": info["entries"][0]["thumbnail"]
            })

        return jsonify({
            "playlist": False,
            "title": info["title"],
            "thumbnail": info["thumbnail"]
        })

    except Exception:
        return jsonify({"error": "Link inválido ou não suportado"}), 400


# 🔹 DOWNLOAD + ZIP
@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    tipo = data.get("type")

    if not url or tipo not in ["audio", "video"]:
        return jsonify({"error": "Parâmetros inválidos"}), 400

    uid = str(uuid.uuid4())
    temp_path = f"{BASE_PATH}/{uid}"
    os.makedirs(temp_path, exist_ok=True)

    try:
        if tipo == "audio":
            ydl_opts = {
                "format": "bestaudio",
                "outtmpl": f"{temp_path}/%(title)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }]
            }
        else:
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": f"{temp_path}/%(title)s.%(ext)s"
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # 🔥 SE FOR PLAYLIST → ZIP
        if "entries" in info:
            zip_path = f"{BASE_PATH}/{uid}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        zipf.write(full_path, arcname=file)

            shutil.rmtree(temp_path)
            return send_file(zip_path, as_attachment=True)

        # 🔹 VÍDEO ÚNICO
        files = os.listdir(temp_path)
        file_path = os.path.join(temp_path, files[0])
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        shutil.rmtree(temp_path, ignore_errors=True)
        return jsonify({"error": "Erro ao processar o download"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
