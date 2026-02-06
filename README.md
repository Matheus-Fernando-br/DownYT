🎧 Conversor de Vídeo para MP3

Aplicação web moderna, rápida e minimalista para converter vídeos em MP3 diretamente pelo navegador, com foco total em praticidade, UX e performance.

🚀 Funcionalidades
🎬 Upload e Seleção

✅ Upload de 1 arquivo por vez
✅ Drag & Drop com efeito glow
✅ Clique para selecionar vídeo
✅ Preview do vídeo carregado
✅ Exibição do nome do arquivo

⚡ Conversão Inteligente

✅ Conversão rápida utilizando FFmpeg
✅ Barra de progresso em tempo real
✅ Spinner visual dentro do botão converter
✅ Mensagens dinâmicas durante processamento

Mensagens alternadas automaticamente:

Processando vídeo...

Extraindo áudio...

Finalizando conversão...

📥 Download e Fluxo Automatizado

✅ Botão download liberado automaticamente
✅ Nome do MP3 mantém nome original do vídeo
✅ Feedback de sucesso após download
✅ Reset automático da interface
✅ Reset com animação suave

🎨 Experiência Visual Avançada

✅ Interface minimalista estilo tech
✅ Hover com scale nos botões
✅ Drag & Drop com glow effect
✅ Micro animações suaves
✅ Smooth page reset animation
✅ Feedback visual progressivo
✅ Preview animado do vídeo
✅ Drop-zone desaparece após seleção

🧰 Tecnologias Utilizadas
Frontend

HTML5

CSS3

JavaScript Vanilla

Deploy: Vercel

Backend

Python

Flask

FFmpeg

Gunicorn

Deploy: Render

📁 Estrutura do Projeto
project-root
│
├── backend
│   ├── app.py
│   ├── requirements.txt
│   └── temp/
│
├── frontend
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── logo.png
│
└── README.md

⚙️ Configuração do Backend
📌 Instalar FFmpeg
Linux (Ubuntu / Render)
apt-get update && apt-get install -y ffmpeg

Windows

Baixe no site oficial:

https://ffmpeg.org/download.html

Depois adicione o FFmpeg ao PATH do sistema.

📌 Instalar dependências Python

Entre na pasta backend:

cd backend


Instale:

pip install -r requirements.txt

📌 Rodar servidor local
python app.py


Servidor local:

http://localhost:5000

🌐 Configuração do Frontend

Abra:

frontend/script.js


Configure a URL da API:

const API = "https://SEU_BACKEND_RENDER.onrender.com";

🚀 Deploy no Render (Backend)
Criar Web Service

Acesse:
https://render.com

Clique em:
New → Web Service

Conecte seu repositório Git

⚙️ Configuração
Root Directory
backend

Environment
Python 3

Build Command
pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg

Start Command
gunicorn app:app

📌 Variáveis de Ambiente

Nenhuma necessária.

🚀 Deploy no Vercel (Frontend)

Acesse:
https://vercel.com

Clique em:
Import Project

Selecione o repositório

⚙️ Configuração
Root Directory
frontend


Clique em Deploy

🔄 Fluxo da Aplicação
1️⃣ Usuário seleciona vídeo

Pode arrastar ou clicar

Preview aparece automaticamente

Nome do vídeo exibido

Drop-zone desaparece suavemente

2️⃣ Usuário clica em Converter

Botão vira spinner

Feedback começa a alternar mensagens

Upload inicia

Conversão é processada no backend

3️⃣ Conversão em Andamento

Barra de progresso atualizada em tempo real

Mensagens dinâmicas simulam pipeline de processamento

4️⃣ Conversão Finalizada

Botão download aparece com animação

Conversão confirmada ao usuário

5️⃣ Download

MP3 mantém nome original do vídeo

Feedback de sucesso exibido

Página reinicia automaticamente com animação suave

🎨 Experiência do Usuário (UX)

O projeto foi desenhado com foco em:

Interação rápida

Feedback constante

Micro animações suaves

Fluxo linear simples

Interface limpa e intuitiva

Sensação de aplicação moderna estilo Apple / Vercel / Linear

⚠️ Observações Técnicas

Apenas 1 arquivo por conversão

Arquivos são armazenados temporariamente

FFmpeg é obrigatório no backend

Conversão depende do tamanho do vídeo

🔐 Segurança

Upload controlado

Arquivos temporários isolados

Conversão executada server-side

📌 Melhorias Futuras Planejadas

Cancelamento real da conversão

Exibição da duração do vídeo

Exibição do tamanho do arquivo

Múltiplos formatos de saída

Limpeza automática de arquivos temporários

Conversão em fila

Dark/Light mode

Suporte mobile avançado

Upload com progresso real

👨‍💻 Autor

Projeto desenvolvido com foco em performance, simplicidade e experiência moderna de conversão de mídia.

⭐ Objetivo do Projeto

Criar um conversor extremamente simples, rápido e visualmente agradável, eliminando complexidade e oferecendo uma experiência direta ao usuário.