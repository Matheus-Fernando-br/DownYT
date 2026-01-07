from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import zipfile
import shutil

app = Flask(__name__)
CORS(app)

# Define o diretório base para downloads. `exist_ok=True` evita erros se a pasta já existir.
BASE_PATH = "downloads"
os.makedirs(BASE_PATH, exist_ok=True)

# --- Rota para buscar informações do vídeo/playlist ---
@app.route("/info", methods=["POST"])
def info():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Link não informado"}), 400

    try:
        # Opções para o yt-dlp, incluindo o arquivo de cookies para evitar bloqueios.
        ydl_opts = {
            "quiet": True,
            "cookiefile": "cookies.txt",
            "skip_download": True, # Garante que nada seja baixado nesta etapa
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Verifica se é uma playlist
        if "entries" in info:
            return jsonify({
                "playlist": True,
                "title": info.get("title", "Título da Playlist Desconhecido"),
                "thumbnail": info["entries"][0].get("thumbnail")
            })

        # Se for um vídeo único
        return jsonify({
            "playlist": False,
            "title": info.get("title", "Título do Vídeo Desconhecido"),
            "thumbnail": info.get("thumbnail")
        })

    except Exception as e:
        # Em caso de erro, retorna uma mensagem genérica. O log do servidor terá o erro real.
        print(f"Erro ao extrair informações: {e}") # Log para depuração no servidor
        return jsonify({"error": "Link inválido ou não suportado"}), 400


# --- Rota para processar o download ---
@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    tipo = data.get("type")

    if not url or tipo not in ["audio", "video"]:
        return jsonify({"error": "Parâmetros inválidos"}), 400

    # Cria um diretório temporário único para este download
    uid = str(uuid.uuid4())
    temp_path = os.path.join(BASE_PATH, uid)
    os.makedirs(temp_path, exist_ok=True)

    try:
        if tipo == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(temp_path, '%(title)s.%(ext)s'),
                "cookiefile": "cookies.txt",
                # Pós-processador para garantir a conversão para MP3 com alta qualidade
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }],
            }
        else: # tipo == "video"
            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": os.path.join(temp_path, '%(title)s.%(ext)s'),
                "merge_output_format": "mp4",
                "cookiefile": "cookies.txt",
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Se for uma playlist, compacta tudo em um arquivo .zip
        if "entries" in info:
            playlist_title = info.get("title", "playlist").replace(" ", "_")
            zip_filename = f"{playlist_title}.zip"
            zip_path = os.path.join(BASE_PATH, f"{uid}.zip")
            
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(temp_path):
                    zipf.write(os.path.join(temp_path, file), arcname=file)
            
            # Envia o arquivo zip para o usuário
            return send_file(zip_path, as_attachment=True, download_name=zip_filename)

        # Se for um vídeo único, envia o arquivo diretamente
        else:
            file_name = os.listdir(temp_path)[0]
            file_path = os.path.join(temp_path, file_name)
            return send_file(file_path, as_attachment=True)

    except Exception as e:
        print(f"Erro durante o download: {e}") # Log para depuração no servidor
        return jsonify({"error": "Erro ao processar o download"}), 500
    
    finally:
        # Garante que a pasta temporária seja sempre removida, mesmo se ocorrer um erro
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path, ignore_errors=True)
        # Limpa também o arquivo zip, se ele foi criado
        zip_to_clean = os.path.join(BASE_PATH, f"{uid}.zip")
        if os.path.exists(zip_to_clean):
            os.remove(zip_to_clean)


# Este bloco só é executado se você rodar o script diretamente (ex: `python app.py`)
# O Gunicorn não executa este bloco.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
