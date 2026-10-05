# ClipForge AI — Fase 2

Base funcional de SaaS para transformar vídeos longos em cortes verticais para Shorts, Reels e TikTok.

## O que existe nesta versão

### Produto / SaaS
- cadastro e login com sessão em cookie HttpOnly;
- senha armazenada com PBKDF2-HMAC-SHA256 + salt;
- banco SQLite persistente;
- dashboard por usuário;
- histórico de projetos;
- proteção de arquivos: um usuário não acessa os vídeos de outro;
- sistema de créditos: **1 crédito = 1 minuto (ou fração) de vídeo analisado**;
- 60 créditos iniciais em novas contas;
- estorno automático dos créditos se o processamento falhar;
- página de planos pronta para futura integração de pagamento;
- exclusão de projetos e arquivos;
- limite de upload configurável.

### Pipeline de vídeo
- upload de MP4, MOV, MKV, WEBM e M4V;
- inspeção via FFprobe;
- transcrição com Faster-Whisper;
- seleção automática de candidatos de corte;
- score heurístico de potencial (gancho, ritmo, perguntas, números, emoção e contexto);
- deduplicação de trechos muito parecidos;
- detecção do rosto principal;
- crop e renderização 9:16 em 1080×1920;
- legendas queimadas no vídeo;
- 3 presets de legenda: Padrão, Clean e Impacto;
- transcrição persistida por projeto para novas renderizações.

### Editor
- preview do corte;
- troca entre todos os cortes gerados;
- edição do título;
- ajuste manual de início e fim;
- ativação/desativação de legendas;
- escolha do estilo da legenda;
- rerender do MP4 sem reenviar o vídeo original;
- download do corte final.

## Estrutura

```text
clipforge-ai-v2/
├─ app/
│  ├─ main.py          API, páginas, jobs e editor
│  ├─ db.py            persistência SQLite
│  ├─ auth.py          senha, sessão e autenticação
│  ├─ pipeline.py      transcrição + seleção de cortes
│  ├─ scoring.py       Potential Score
│  ├─ video.py         FFprobe/OpenCV/FFmpeg/legendas
│  ├─ templates/
│  └─ static/
├─ data/
│  ├─ db/
│  ├─ uploads/
│  └─ outputs/
├─ requirements.txt
├─ Dockerfile
└─ .env.example
```

## Rodar localmente

Pré-requisitos:
- Python 3.11+
- FFmpeg/FFprobe

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abra `http://localhost:8000`.

Na primeira transcrição, o Faster-Whisper precisa obter o modelo `small`. Em produção, mantenha o modelo já instalado no worker e use GPU.

## Docker

```bash
docker build -t clipforge-ai .
docker run --rm -p 8000:8000 -v $(pwd)/data:/app/data clipforge-ai
```

No Windows, adapte o volume conforme Docker Desktop/PowerShell.

## Variáveis de ambiente

Veja `.env.example`.

- `COOKIE_SECURE=1`: obrigatório na implantação HTTPS de produção.
- `MAX_UPLOAD_MB=2048`: limite máximo do arquivo enviado.

## Limitações conscientes desta Fase 2

O processamento ainda roda em uma thread do mesmo servidor. Isso é adequado para desenvolvimento e testes, não para muitos usuários simultâneos. A nova renderização feita pelo editor também é síncrona nesta fase.

SQLite é adequado para MVP/local. Para lançamento comercial, migrar para PostgreSQL.

O Potential Score atual é heurístico. A próxima fase deve adicionar análise semântica com LLM, score por objetivo e prompts como “encontre a parte onde eu explico X”.

## Fase 3 recomendada

1. Redis + fila (Celery/RQ/Arq) e workers GPU separados.
2. PostgreSQL + migrations.
3. Object Storage (Cloudflare R2/S3) com URLs assinadas.
4. Word-level timestamps para legenda estilo karaoke.
5. Speaker diarization + speaker tracking.
6. Reframe temporal quadro a quadro.
7. Análise semântica com LLM:
   - viral;
   - educativo;
   - vendas;
   - engraçado;
   - surpreendente;
   - frases de impacto.
8. Geração automática de título, hook e descrição.
9. Busca por prompt dentro do vídeo.
10. Mercado Pago/Stripe + webhooks + renovação de créditos.
11. Brand kit.
12. Publicação autorizada para YouTube/TikTok/Instagram.

## Segurança para produção

Antes de disponibilizar publicamente:
- HTTPS obrigatório;
- `COOKIE_SECURE=1`;
- proteção CSRF em operações mutáveis;
- rate limit;
- validação antivírus/malware em uploads;
- storage privado;
- URLs assinadas;
- política de retenção/exclusão dos vídeos;
- termos de uso e política de privacidade;
- backup do banco;
- observabilidade, retries e logs estruturados.

## Arquitetura de produção sugerida

```text
Browser
  ↓
CDN / Next.js
  ↓
FastAPI
  ├── PostgreSQL
  ├── Redis / Queue
  └── Object Storage
         ↑
     Worker GPU
  Whisper / Vision / LLM / FFmpeg
```

## Conteúdo do YouTube

Para um produto comercial, use upload direto ou integração autorizada com a conta/canal do próprio usuário. Evite basear o serviço em download irrestrito de vídeos de terceiros.

## Deploy no Vercel — correção de entrypoint

Esta versão inclui duas formas explícitas para o Vercel localizar o FastAPI:

- `pyproject.toml` → `[tool.vercel] entrypoint = "app.main:app"`;
- `main.py` na raiz → reexporta `app` de `app.main` como fallback de descoberta.

Depois de enviar estes arquivos ao repositório, faça um novo deploy. O endpoint
`/health` deve responder com `{"ok": true, ...}` quando a aplicação estiver no ar.

### Atenção: Vercel não deve receber os vídeos diretamente em produção

Corrigir o entrypoint resolve o **build**, mas o endpoint atual `/api/jobs` ainda
recebe o arquivo de vídeo através da própria Function. Em Vercel Functions há
limite de payload HTTP, portanto a arquitetura de produção deve usar upload
**direto do navegador para object storage** (Vercel Blob, Cloudflare R2, S3 ou
compatível) e enviar para o FastAPI apenas a chave/URL privada do arquivo.

Também não use SQLite/local disk como persistência definitiva no Vercel. Para a
versão comercial, use PostgreSQL + object storage + worker/queue para o pipeline
de Whisper/FFmpeg. O Vercel pode continuar hospedando a aplicação web/API leve.


## Vercel entrypoint (v0.2.2)

This package uses the root-level `main.py` as the explicit FastAPI entrypoint:

```toml
[tool.vercel]
entrypoint = "main:app"
```

`main.py` imports `app` from `app.main`. Keep `main.py`, `pyproject.toml`, `requirements.txt`, and the `app/` directory at the repository root. In Vercel, Project Settings > Build and Deployment > Root Directory should be empty (repository root), unless these files are intentionally inside a subdirectory.

## Vercel: bundle maior que 500 MB

Esta versão inclui `vercel.json` com **Fluid Compute** habilitado. O pipeline de IA usa dependências nativas pesadas (`faster-whisper`, `ctranslate2`, `opencv` e `numpy`), por isso o bundle Python pode ultrapassar 500 MB.

Para projetos Vercel que ainda não estão inscritos em **Large Functions**, adicione no painel do projeto:

- **Settings → Environment Variables**
- Nome: `VERCEL_SUPPORT_LARGE_FUNCTIONS`
- Valor: `1`
- Ambientes: Production, Preview e Development (ou pelo menos o ambiente que você está implantando)

Depois salve e faça um **Redeploy**. O `vercel.json` já ativa `fluid: true`.

Opcionalmente, para diagnosticar o tamanho do bundle, adicione também `VERCEL_ANALYZE_BUILD_OUTPUT=1` e faça um deploy de teste.

### Importante sobre vídeos grandes

Resolver o bundle permite publicar a aplicação, mas uploads de vídeo grandes não devem atravessar a função HTTP do Vercel. O limite de payload de Functions é muito menor que um vídeo típico. Para a versão de produção, o upload será feito diretamente para armazenamento de objetos (R2/S3/Blob) e o processamento será movido para um worker dedicado.
