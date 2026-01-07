from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

@app.route("/info", methods=["POST"])
def info():
    url = request.json["url"]

    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    if "entries" in info:
        return jsonify({
            "playlist": True,
            "title": info["title"],
            "thumbnail": info["entries"][0]["thumbnail"],
            "count": len(info["entries"]),
            "duration": "--:--"
        })

    return jsonify({
        "playlist": False,
        "title": info["title"],
        "thumbnail": info["thumbnail"],
        "duration": f"{info['duration']//60}:{info['duration']%60:02d}"
    })

@app.route("/download")
def download():
    url = request.args.get("url")
    tipo = request.args.get("type")
    uid = str(uuid.uuid4())

    if tipo == "audio":
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": f"{DOWNLOAD_PATH}/{uid}.mp3",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }]
        }
        file = f"{DOWNLOAD_PATH}/{uid}.mp3"
    else:
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": f"{DOWNLOAD_PATH}/{uid}.mp4"
        }
        file = f"{DOWNLOAD_PATH}/{uid}.mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(file, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
