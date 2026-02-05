const API_URL = "https://downyt-f9ul.onrender.com";

const messages = [
    "Baixe vídeos e reels do Instagram",
    "Simples, rápido e gratuito",
    "Funciona com posts e reels públicos",
    "Sem instalar nada"
];

let messageIndex = 0;

async function buscar() {

    const url = document.getElementById("url").value.trim();
    const result = document.getElementById("result");
    const loader = document.getElementById("loader");

    result.style.display = "none";

    if (!url.includes("instagram.com")) {
        alert("Cole um link válido do Instagram.");
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

        if (!res.ok) throw new Error(data.error);

        document.getElementById("thumb").src = data.thumbnail;
        document.getElementById("title").innerText = data.title;

        result.style.display = "flex";

    } catch (err) {
        alert(err.message);
    } finally {
        loader.hidden = true;
    }
}

async function download() {

    const url = document.getElementById("url").value.trim();
    const loader = document.getElementById("loader");
    const progressBar = document.querySelector(".progress");
    const progressText = document.getElementById("progressText");

    loader.hidden = false;
    progressBar.style.width = "0%";
    progressText.innerText = "0%";

    const res = await fetch(`${API_URL}/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
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
            window.location.href = `${API_URL}/file/${pid}`;
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
    