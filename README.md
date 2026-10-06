# Trion Corte — Vercel Edition v3

Reescrita completa do antigo backend FastAPI para uma arquitetura compatível com Vercel.

## O que mudou

- **Vercel:** somente Next.js 16 + Route Handlers leves.
- **Upload:** navegador envia o vídeo **diretamente ao Vercel Blob** em multipart. O arquivo não atravessa uma Function.
- **Banco:** Postgres serverless (Neon recomendado), sem SQLite local.
- **Processamento:** Whisper, FFmpeg e OpenCV ficam em `processor-worker/`, que é excluído do deploy Vercel por `.vercelignore`.
- **Privacidade:** projeto preparado para **Private Vercel Blob** e URLs temporárias assinadas.
- **Autenticação:** cookie HttpOnly assinado e senha com PBKDF2.
- **Créditos:** 1 crédito por minuto ou fração do vídeo.
- **Editor:** título, tempo inicial/final, estilo de legenda e re-renderização via worker.

## Deploy rápido

Leia `VERCEL_SETUP.md`. Não altere Root Directory e não adicione `pyproject.toml`, `requirements.txt`, `Dockerfile` ou `main.py` Python na raiz.

## Verificação estrutural

```bash
npm run check:project
```

Esse teste garante que o repositório não voltou ao padrão que fazia o Vercel detectar FastAPI/Python.
