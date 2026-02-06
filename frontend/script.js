const API = "https://downyt-f9ul.onrender.com";

let fileId = null;

const input = document.getElementById("fileInput");
const convertBtn = document.getElementById("convertBtn");
const progressBar = document.getElementById("progress");
const downloadBtn = document.getElementById("downloadBtn");
const feedback = document.getElementById("feedback");
const fileInfo = document.getElementById("fileInfo");

input.addEventListener("change", () => {

    const file = input.files[0];

    if (!file) return;

    fileInfo.innerHTML = `
        <p><strong>${file.name}</strong></p>
        <p>${(file.size / 1024 / 1024).toFixed(2)} MB</p>
    `;

    convertBtn.disabled = false;
});


convertBtn.onclick = async () => {

    const file = input.files[0];

    const formData = new FormData();
    formData.append("file", file);

    const upload = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData
    });

    const data = await upload.json();
    fileId = data.file_id;

    await fetch(`${API}/convert/${fileId}`, {
        method: "POST"
    });

    checkProgress();
};


async function checkProgress() {

    const interval = setInterval(async () => {

        const res = await fetch(`${API}/progress/${fileId}`);
        const data = await res.json();

        progressBar.style.width = data.progress + "%";

        if (data.done) {
            clearInterval(interval);

            downloadBtn.hidden = false;
        }

    }, 500);
}


downloadBtn.onclick = () => {

    window.open(`${API}/download/${fileId}`);

    feedback.innerText = "Vídeo convertido com sucesso!";

    setTimeout(() => location.reload(), 2000);
};
