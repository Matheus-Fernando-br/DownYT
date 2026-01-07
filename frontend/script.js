const API_URL = "https://downyt-f9ul.onrender.com";

async function buscar() {
    const url = document.getElementById("url").value.trim();
    const result = document.getElementById("result");
    const loader = document.getElementById("loader");

    // Esconde a section toda vez que clicar em pesquisar
    result.style.display = "none";

    if (!url) {
        alert("Cole um link do YouTube");
        return;
    }

    loader.hidden = false;

    try {
        const res = await fetch(`${API_URL}/info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!res.ok) throw new Error("Erro ao buscar vídeo");

        const data = await res.json();

        document.getElementById("thumb").src = data.thumbnail;
        document.getElementById("title").innerText = data.title;
        document.getElementById("duration").innerText = data.duration;

        if (data.playlist) {
            document.getElementById("playlistInfo").innerText =
                `Playlist com ${data.count} vídeos`;
        } else {
            document.getElementById("playlistInfo").innerText = "";
        }

        // MOSTRA a section SOMENTE agora
        result.style.display = "flex";

    } catch (err) {
        alert("Erro ao buscar informações do vídeo");
    } finally {
        loader.hidden = true;
    }
}

function download(type) {
    const url = document.getElementById("url").value;
    window.location.href =
        `${API_URL}/download?type=${type}&url=${encodeURIComponent(url)}`;
}
