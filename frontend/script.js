const API_URL = "https://downyt-f9ul.onrender.com";

const messages = [
    "Baixe vídeos e músicas do YouTube com máxima qualidade",
    "DownYT é rápido, simples e sem complicações",
    "Suporte a vídeos individuais e playlists completas",
    "Escolha entre áudio MP3 ou vídeo MP4",
    "Tudo online, sem instalar nada no seu computador",
    "Sem anuncios, sem taxas, 100% gratuito",
    "DownYT — seu downloader inteligente"
];

let messageIndex = 0;


async function buscar() {
    const url = document.getElementById("url").value.trim();
    const result = document.getElementById("result");
    const loader = document.getElementById("loader");

    result.style.display = "none";

    if (!url) {
        alert("Erro: cole um link válido do YouTube.");
        return;
    }

    loader.hidden = false;

    try {
        const res = await fetch(`${API_URL}/info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(`Erro: ${data.error}`);
            return;
        }

        document.getElementById("thumb").src = data.thumbnail;
        document.getElementById("title").innerText = data.title;
        document.getElementById("duration").innerText = "";

        result.style.display = "flex";

    } catch {
        alert("Erro de conexão com o servidor.");
    } finally {
        loader.hidden = true;
    }
}

async function download(type) {

    const url = document.getElementById("url").value;
    const loader = document.getElementById("loader");
    const progressBar = document.querySelector(".progress");
    const progressText = document.getElementById("progressText");

    loader.hidden = false;
    progressBar.style.width = "0%";
    progressText.innerText = "0%";

    const res = await fetch(`${API_URL}/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, type })
    });

    const data = await res.json();
    const pid = data.progress_id;

    const source = new EventSource(`${API_URL}/progress/${pid}`);

    source.onmessage = (event) => {

        const { progress } = JSON.parse(event.data);

        progressBar.style.width = progress + "%";
        progressText.innerText = progress + "%";

        if (progress >= 100) {
            source.close();
            loader.hidden = true;
            alert("Download finalizado!");
        }
    };
}

function startMessages() {
    const section = document.getElementById("messages");
    const text = document.getElementById("messageText");

    text.innerText = messages[0];
    section.classList.add("show");

    setInterval(() => {
        section.classList.remove("show");
        section.classList.add("hide");

        setTimeout(() => {
            messageIndex = (messageIndex + 1) % messages.length;
            text.innerText = messages[messageIndex];

            section.classList.remove("hide");
            section.classList.add("show");
        }, 1000);

    }, 5000);
}

document.addEventListener("DOMContentLoaded", startMessages);