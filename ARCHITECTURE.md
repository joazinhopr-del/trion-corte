# Arquitetura

```text
Browser
  │
  ├── Next.js pages/API ───────────────► Neon Postgres
  │        (Vercel)
  │
  ├── multipart direto ────────────────► Vercel Private Blob
  │
  └── acompanha status ◄─────────────── Next.js API

Vercel API
  │
  └── POST job ────────────────────────► Processor Worker
                                             │
                                             ├── Whisper
                                             ├── scoring
                                             ├── OpenCV
                                             ├── FFmpeg
                                             │
                                             ├── GET assinado ◄── Blob
                                             ├── PUT assinado ───► Blob
                                             └── callback ───────► Vercel API ─► Neon
```

## Por que não há FFmpeg/Whisper dentro do Vercel

O frontend e as APIs de coordenação são serverless e curtos. Processamento de vídeo consome CPU por muitos minutos, baixa arquivos grandes e precisa de binários/modelos. Mantê-lo fora do bundle web reduz cold start, tamanho de função, custo e risco de timeout.

## Segurança

- uploads em Blob privado;
- URLs temporárias assinadas para o worker e para o navegador;
- `PROCESSOR_SECRET` autentica callbacks do worker;
- cookie HttpOnly/SameSite=Lax;
- senha PBKDF2 com salt;
- consultas sempre filtradas pelo `user_id`.
