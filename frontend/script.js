const API_URL = "https://downyt-f9ul.onrender.com";

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

    const confirmar = confirm(
        `Confirmar download em formato ${type === "audio" ? "ÁUDIO (MP3)" : "VÍDEO (MP4)"}?`
    );

    if (!confirmar) return;

    try {
        const res = await fetch(`${API_URL}/download`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, type })
        });

        if (!res.ok) {
            const data = await res.json();
            alert(`Erro: ${data.error}`);
            return;
        }

        // 🔥 força download
        const blob = await res.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "DownYT";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        alert("Download concluído com sucesso!");
        location.reload();

    } catch {
        alert("Erro ao realizar o download.");
    }
}
