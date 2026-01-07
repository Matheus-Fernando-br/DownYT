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

    except:
        return jsonify({"error": "Link inválido ou não suportado"}), 400


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
                "format": "bestaudio/best",
                "outtmpl": f"{temp_path}/%(title)s.%(ext)s"
            }
        else:
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": f"{temp_path}/%(title)s.%(ext)s",
                "merge_output_format": "mp4"
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # 🔥 PLAYLIST → ZIP
        if "entries" in info:
            zip_path = f"{BASE_PATH}/{uid}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(temp_path):
                    zipf.write(os.path.join(temp_path, file), file)

            shutil.rmtree(temp_path)
            return send_file(zip_path, as_attachment=True)

        # 🔹 VÍDEO ÚNICO
        file = os.listdir(temp_path)[0]
        return send_file(os.path.join(temp_path, file), as_attachment=True)

    except Exception as e:
        shutil.rmtree(temp_path, ignore_errors=True)
        return jsonify({"error": "Erro ao processar o download"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
