# Deploy correto no Vercel

## 1. Repositório

Envie **o conteúdo desta pasta diretamente para a raiz** do repositório GitHub.

A raiz precisa conter:

```text
package.json
next.config.mjs
app/
components/
lib/
```

Não configure uma subpasta como Root Directory.

## 2. Vercel

1. Import Project > selecione o repositório.
2. Framework Preset: **Next.js** (deve ser detectado automaticamente).
3. Root Directory: **vazio / raiz do repositório**.
4. Build Command: deixe o padrão (`next build`).
5. Install Command: deixe o padrão.
6. Não adicione configuração de FastAPI/Python.

## 3. Banco

No projeto Vercel:

**Storage / Marketplace > Neon > Create New**

Conecte o banco ao projeto. O `DATABASE_URL` será criado pela integração.

O Trion Corte cria as tabelas automaticamente na primeira operação de banco usando `CREATE TABLE IF NOT EXISTS`.

## 4. Blob

No projeto Vercel:

**Storage > Blob > Create > Private**

Conecte o store ao projeto. O código usa `@vercel/blob` e upload direto do navegador em multipart.

## 5. Variáveis

Adicione:

- `SESSION_SECRET`: string aleatória longa.
- `APP_URL`: domínio de produção, por exemplo `https://trion-corte.vercel.app`.
- `PROCESSOR_URL`: URL do worker de vídeo.
- `PROCESSOR_SECRET`: segredo compartilhado entre site e worker.
- `MAX_VIDEO_MB`: opcional, padrão 2048.
- `DEFAULT_FREE_CREDITS`: opcional, padrão 60.

## 6. Worker

A pasta `processor-worker/` **não é enviada ao Vercel**. Ela precisa rodar num serviço para jobs pesados (Railway, Render, Fly.io, RunPod etc.).

No worker configure:

- `PROCESSOR_SECRET` igual ao Vercel.
- `WHISPER_MODEL=small` (ou medium/large conforme GPU).
- `WHISPER_DEVICE=cpu` ou `cuda`.
- `WHISPER_COMPUTE_TYPE=int8` para CPU ou `float16` para GPU.

## 7. Teste

Acesse `/configuracao` após o deploy. O painel mostra quais integrações estão disponíveis.

Depois:

1. crie uma conta;
2. envie um vídeo;
3. acompanhe o upload direto ao Blob;
4. o Vercel dispara o worker;
5. o worker devolve os cortes e o painel atualiza automaticamente.
