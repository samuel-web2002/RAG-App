# RAG Chatbot

> A production-grade Retrieval-Augmented Generation (RAG) chatbot — chat with your documents powered by GPT-4o and ChromaDB.

[![CI](https://github.com/YOUR_USERNAME/RAG-App/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/RAG-App/actions/workflows/ci.yml)

---

## Architecture

```
RAG-App/
├── backend/            # FastAPI Python API
│   ├── app/
│   │   ├── api/        # Route handlers (chat, ingest, documents)
│   │   ├── rag/        # Pipeline + session memory
│   │   ├── middleware/  # API key auth
│   │   ├── models/     # Pydantic schemas
│   │   ├── config.py   # pydantic-settings
│   │   └── main.py     # FastAPI app factory
│   └── tests/          # pytest test suite
├── frontend/           # React + Vite + TypeScript UI
│   └── src/
│       ├── api/        # Typed API client
│       ├── components/ # Chat, Documents, Settings
│       └── types/      # TypeScript interfaces
├── .github/workflows/  # CI (lint/test) + CD (Docker → GHCR)
└── docker-compose.yml  # Full-stack orchestration
```

## Quickstart

### 1. Prerequisites

- Python 3.12+, Node 20+, Docker (optional)
- [Ollama](https://ollama.com/) installed and running
- Download models:
  ```bash
  ollama pull llama3
  ollama pull nomic-embed-text
  ```

### 2. Backend

```bash
cd backend

# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env — set OLLAMA_BASE_URL (defaults to http://localhost:11434)

# Run
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# UI: http://localhost:5173
```

### 4. Docker Compose (full stack)

```bash
# Ensure backend/.env exists with OPENAI_API_KEY set
docker compose up --build
# UI: http://localhost:3000
# API: http://localhost:8000/docs
```

---

## API Reference

All endpoints (except `/health`) require `X-API-Key` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/chat` | Chat with the RAG pipeline |
| `POST` | `/api/ingest` | Upload a document |
| `GET` | `/api/documents` | List indexed documents |
| `DELETE` | `/api/documents/{id}` | Delete a document |

### Chat example

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize the document", "session_id": "session-1"}'
```

### Ingest example

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "X-API-Key: your-api-key" \
  -F "file=@report.pdf"
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

---

## CI/CD

- **CI** (`.github/workflows/ci.yml`) — runs on every push/PR: ruff lint, ruff format, mypy, pytest, TSC, Vite build
- **CD** (`.github/workflows/cd.yml`) — runs on push to `main`: builds and pushes Docker images to GitHub Container Registry

To enable CD, push to GitHub — `GITHUB_TOKEN` is automatically available. No secrets needed for GHCR push.

---

## Configuration

All backend settings are driven by environment variables (see `backend/.env.example`):

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `API_KEY` | `dev-secret-change-me` | Your API key for auth |
| `MODEL_NAME` | `llama3` | Ollama LLM model |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Ollama embedding model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `CHUNK_SIZE` | `1000` | Text chunk size (tokens) |
| `RETRIEVER_K` | `6` | Number of chunks to retrieve |

## Pushing to GitHub

```bash
cd "/Users/sambacha/Desktop/Redemption Arc/RAG-App"
git init
git add .
git commit -m "feat: initial production RAG chatbot"
git remote add origin https://github.com/YOUR_USERNAME/RAG-App.git
git push -u origin main
```

## License

MIT
