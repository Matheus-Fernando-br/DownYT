import os
import uuid
import subprocess
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

UPLOAD_FOLDER = "temp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

conversions = {}

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.mp4")
    output_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.mp3")

    file.save(input_path)

    conversions[file_id] = {
        "input": input_path,
        "output": output_path,
        "progress": 0,
        "done": False
    }

    return jsonify({"file_id": file_id})


@app.route("/convert/<file_id>", methods=["POST"])
def convert(file_id):
    data = conversions.get(file_id)

    if not data:
        return jsonify({"error": "Arquivo não encontrado"}), 404

    input_file = data["input"]
    output_file = data["output"]

    command = [
        "ffmpeg",
        "-i", input_file,
        "-vn",
        "-ab", "192k",
        output_file,
        "-y"
    ]

    process = subprocess.Popen(
        command,
        stderr=subprocess.PIPE,
        text=True
    )

    for line in process.stderr:
        if "time=" in line:
            data["progress"] = min(data["progress"] + 5, 95)

    process.wait()

    data["progress"] = 100
    data["done"] = True

    return jsonify({"status": "converted"})


@app.route("/progress/<file_id>")
def progress(file_id):
    data = conversions.get(file_id)

    if not data:
        return jsonify({"error": "Não encontrado"}), 404

    return jsonify({
        "progress": data["progress"],
        "done": data["done"]
    })


@app.route("/download/<file_id>")
def download(file_id):
    data = conversions.get(file_id)

    if not data or not os.path.exists(data["output"]):
        return jsonify({"error": "Arquivo não existe"}), 404

    return send_file(data["output"], as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
