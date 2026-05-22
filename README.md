# Inference Logging System

A production-oriented lightweight LLM inference logging and ingestion system with a streaming chatbot, reusable Gemini SDK wrapper, MongoDB persistence, and analytics dashboard.

## Stack

- Frontend: Next.js 15 App Router, TypeScript, Tailwind CSS, shadcn-style UI primitives, Zustand, Recharts, streaming readable streams
- Backend: FastAPI, Python 3.12, async APIs, Pydantic v2, Motor, official Google Gemini SDK
- Database: MongoDB Atlas or local MongoDB
- Deployment: Vercel frontend, Render/Railway backend, Docker Compose for local development

## Folder Structure

```text
.
├── backend
│   ├── app
│   │   ├── core
│   │   ├── db
│   │   ├── repositories
│   │   ├── routes
│   │   ├── schemas
│   │   ├── sdk
│   │   └── services
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend
│   ├── app
│   ├── components
│   ├── hooks
│   ├── lib
│   ├── store
│   └── package.json
├── k8s
├── docker-compose.yml
└── .env.example
```

## Setup

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Set `GEMINI_API_KEY`. For Atlas, replace `MONGODB_URI` with your Atlas connection string.

3. Run with Docker:

```bash
docker compose up --build
```

4. Open:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API

- `POST /chat`: stream an assistant reply and persist the conversation
- `GET /conversations`: list conversations
- `GET /conversations/{id}`: fetch a conversation
- `GET /conversations/{id}/messages`: fetch messages
- `DELETE /conversations/{id}`: delete a conversation and its messages/logs
- `POST /ingest`: validate and persist inference metadata
- `GET /metrics/dashboard`: dashboard metrics

## Architecture Notes

The backend follows clean architecture:

- `routes`: HTTP boundaries and dependency injection
- `services`: use cases and orchestration
- `repositories`: MongoDB persistence
- `sdk`: provider abstractions and Gemini implementation
- `schemas`: Pydantic request/response contracts
- `db`: Mongo client lifecycle and indexes

The LLM wrapper records latency, status, token usage, timestamps, previews, provider/model, conversation id, and errors. It sends logs through the ingestion service. If ingestion fails, chat still completes and the failure is logged server-side.

## MongoDB Schema

`conversations`

- `_id`: ObjectId
- `title`: generated short title
- `created_at`, `updated_at`: UTC timestamps
- `message_count`: denormalized count for sidebar performance
- `last_message_preview`: short preview

Indexes: `updated_at desc`, text index on `title`.

`messages`

- `_id`: ObjectId
- `conversation_id`: ObjectId string
- `role`: `user` or `assistant`
- `content`: markdown text
- `created_at`: UTC timestamp

Indexes: `(conversation_id, created_at)`, `created_at desc`.

`inference_logs`

- `_id`: ObjectId
- `conversation_id`
- `provider`, `model`
- `latency_ms`
- `input_tokens`, `output_tokens`, `total_tokens`
- `status`: `success` or `error`
- `error`
- `input_preview`, `output_preview`
- `started_at`, `completed_at`, `created_at`
- `metadata`

Indexes: `created_at desc`, `(provider, model)`, `(conversation_id, created_at)`, `status`.

## Deployment

Frontend on Vercel:

- Root directory: `frontend`
- Build command: `npm run build`
- Environment: `NEXT_PUBLIC_API_BASE_URL=https://your-backend.example.com`

Backend on Render/Railway:

- Root directory: `backend`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment: `MONGODB_URI`, `MONGODB_DB`, `GEMINI_API_KEY`, `API_CORS_ORIGINS`

MongoDB Atlas:

- Create a cluster and database user
- Add your deployment IPs or `0.0.0.0/0` for initial testing
- Use the SRV connection string in `MONGODB_URI`
