const API_URL = "https://SEU-BACKEND.onrender.com";

async function buscar() {
    const url = document.getElementById("url").value;
    document.getElementById("loader").hidden = false;

    const res = await fetch(`${API_URL}/info`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    });

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

    document.getElementById("loader").hidden = true;
    document.getElementById("result").hidden = false;
}

function download(type) {
    const url = document.getElementById("url").value;
    window.location.href =
        `${API_URL}/download?type=${type}&url=${encodeURIComponent(url)}`;
}
