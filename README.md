# 🎧 Conversor de Vídeo para MP3

Projeto simples, rápido e minimalista para converter vídeos em MP3 diretamente pelo navegador.

---

## 🚀 Funcionalidades

✅ Upload de 1 arquivo por vez  
✅ Exibição do nome e tamanho do arquivo  
✅ Conversão para MP3  
✅ Barra de progresso  
✅ Botão de download após conversão  
✅ Feedback de sucesso  
✅ Reset automático da página  

---

## 🧰 Tecnologias Utilizadas

### Frontend
- HTML
- CSS
- JavaScript
- Deploy: Vercel

### Backend
- Python
- Flask
- FFmpeg
- Deploy: Render

---

## 📁 Estrutura do Projeto

project-root
│
├── backend
│ ├── app.py
│ ├── requirements.txt
│ └── temp/
│
├── frontend
│ ├── index.html
│ ├── style.css
│ ├── script.js
│ └── logo.png
│
└── README.md

yaml
Copiar código

---

## ⚙️ Configuração do Backend

### 📌 Instalar FFmpeg

#### Linux (Ubuntu / Render)

apt-get update && apt-get install -y ffmpeg

yaml
Copiar código

---

#### Windows

Baixe no site oficial:

https://ffmpeg.org/download.html

Depois adicione o FFmpeg ao PATH do Windows.

---

### 📌 Instalar dependências Python

Entre na pasta backend:

cd backend

makefile
Copiar código

Instale:

pip install -r requirements.txt

yaml
Copiar código

---

### 📌 Rodar servidor local

python app.py

css
Copiar código

Servidor irá rodar em:

http://localhost:5000

yaml
Copiar código

---

## 🌐 Configuração do Frontend

No arquivo:

frontend/script.js

css
Copiar código

Troque a URL da API:

const API = "https://SEU_BACKEND_RENDER.onrender.com";

yaml
Copiar código

---

## 🚀 Deploy no Render (Backend)

### Criar Web Service

1. Acesse:
https://render.com

2. Clique em:
New → Web Service

3. Conecte seu repositório Git

4. Configure:

#### Root Directory
backend

shell
Copiar código

#### Environment
Python 3

shell
Copiar código

#### Build Command
pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg

shell
Copiar código

#### Start Command
gunicorn app:app

yaml
Copiar código

---

### 📌 Variáveis Importantes

Não precisa adicionar nenhuma variável de ambiente.

---

## 🚀 Deploy no Vercel (Frontend)

1. Acesse:
https://vercel.com

2. Import Project

3. Selecione o repositório

4. Root Directory:

frontend

yaml
Copiar código

5. Deploy

---

## 🔄 Como Funciona o Fluxo

1. Usuário seleciona vídeo
2. Arquivo é enviado ao backend
3. FFmpeg converte para MP3
4. Progresso é exibido
5. Download é liberado
6. Página reinicia automaticamente

---

## ⚠️ Observações

- Apenas 1 arquivo por vez
- Arquivos são armazenados temporariamente no servidor
- FFmpeg é obrigatório

---

## 📌 Melhorias Futuras

- Drag and Drop
- Múltiplos formatos de áudio
- Limpeza automática de arquivos
- Conversão em fila
- Interface mais avançada

---

## 👨‍💻 Autor

Projeto desenvolvido para conversão rápida e prática de vídeo para MP3.