const API = "https://downyt-f9ul.onrender.com";

let fileId = null;
let fileName = "";

const dropZone = document.getElementById("dropZone");
const input = document.getElementById("fileInput");
const convertBtn = document.getElementById("convertBtn");
const downloadBtn = document.getElementById("downloadBtn");
const cancelBtn = document.getElementById("cancelBtn");
const progressBar = document.getElementById("progress");
const feedback = document.getElementById("feedback");
const preview = document.getElementById("preview");
const fileInfo = document.getElementById("fileInfo");

const mensagens = [
    "Processando vídeo...",
    "Extraindo áudio...",
    "Finalizando conversão..."
];

let msgInterval;

/* ================= DRAG & DROP ================= */

dropZone.onclick = () => input.click();

dropZone.addEventListener("dragover", e => {
    e.preventDefault();
    dropZone.classList.add("glow");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("glow");
});

dropZone.addEventListener("drop", e => {
    e.preventDefault();
    dropZone.classList.remove("glow");

    const file = e.dataTransfer.files[0];

    if (!file) return;

    // colocar arquivo dentro do input (SOLUÇÃO)
    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;

    handleFile(file);
});

input.addEventListener("change", () => {
    handleFile(input.files[0]);
});

dropZone.addEventListener("mousedown", () => {
    dropZone.style.transform = "scale(0.85)";
});

dropZone.addEventListener("mouseup", () => {
    dropZone.style.transform = "scale(1)";
});

dropZone.addEventListener("mouseleave", () => {
    dropZone.style.transform = "scale(1)";
});


/* ================= HANDLE FILE ================= */

function handleFile(file) {

    if (!file) return;

    fileName = file.name.replace(/\.[^/.]+$/, "");

    /* MOSTRAR NOME DO VIDEO */
    fileInfo.innerText = file.name;
    fileInfo.classList.add("fade-in");

    preview.src = URL.createObjectURL(file);
    preview.hidden = false;
    preview.classList.add("fade-in");

    convertBtn.disabled = false;
    cancelBtn.hidden = false;

    dropZone.classList.add("hidden-smooth");
}

/* ================= CANCEL ================= */

cancelBtn.onclick = smoothReload;

/* ================= CONVERT ================= */

convertBtn.onclick = async () => {

    const file = input.files[0];

    convertBtn.innerHTML = `<div class="spinner-btn"></div>`;
    convertBtn.disabled = true;

    alternarMensagens();

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

function alternarMensagens() {
    let index = 0;
    feedback.innerText = mensagens[index];

    msgInterval = setInterval(() => {
        index = (index + 1) % mensagens.length;
        feedback.innerText = mensagens[index];
    }, 2000);
}

/* ================= PROGRESS ================= */

async function checkProgress() {

    const interval = setInterval(async () => {

        const res = await fetch(`${API}/progress/${fileId}`);
        const data = await res.json();

        progressBar.style.width = data.progress + "%";

        if (data.done) {

            clearInterval(interval);
            clearInterval(msgInterval);

            convertBtn.innerHTML = "Converter";
            convertBtn.disabled = true;

            downloadBtn.hidden = false;
            downloadBtn.classList.add("fade-in");

            feedback.innerText = "Conversão concluída!";
        }

    }, 500);
}

/* ================= DOWNLOAD ================= */

downloadBtn.onclick = () => {

    convertBtn.disabled = true;
    downloadBtn.disabled = true;
    cancelBtn.disabled = true;

    const link = document.createElement("a");
    link.href = `${API}/download/${fileId}`;
    link.download = `${fileName}.mp3`;
    link.click();

    feedback.innerText = "Download realizado com sucesso!";

    setTimeout(smoothReload, 2000);
};

/* ================= SMOOTH RELOAD ================= */

function smoothReload() {
    document.body.classList.add("fade-out");
    setTimeout(() => location.reload(), 400);
}
