# Architecture
<img width="2816" height="1536" alt="Architecture_Image" src="https://github.com/user-attachments/assets/c1328933-7062-409f-b03d-5529fcc0c69a" />

## Request Flow

1. The Next.js chat input sends `POST /chat` with a message and optional `conversation_id`.
2. FastAPI creates or loads the conversation, persists the user message, builds history, and calls the configured LLM provider.
3. The Gemini provider streams chunks back through `StreamingResponse` using server-sent event frames.
4. The frontend reads the response body with `ReadableStream`, appends token chunks to the active assistant message, and can cancel via `AbortController`.
5. When the stream completes or fails, the backend persists the assistant message if one exists and writes an inference log through the ingestion service.

## Clean Architecture

- Routes know HTTP and dependency injection only.
- Services orchestrate application use cases.
- Repositories encapsulate MongoDB queries and indexes.
- SDK providers encapsulate LLM-specific APIs.
- Schemas define public request/response contracts and persistence validation.

## Ingestion Pipeline

`POST /ingest` accepts `InferenceLogCreate`, validates it with Pydantic, flattens token usage into query-friendly fields, adds a server-side `created_at`, and persists it to `inference_logs`.

The chat service uses the same ingestion service in best-effort mode. Ingestion failures are retried and logged, but they do not break the user-facing chat stream.

## Provider Abstraction

`LLMProvider` defines a small streaming interface. `GeminiProvider` is production-ready with the official `google-genai` SDK. `OpenAICompatibleProvider` is included as an extension point so another provider can be wired without changing chat routes or repositories.

## MongoDB Indexes

Conversations:

- `updated_at desc`: fast sidebar listing
- `title text`: future search

Messages:

- `(conversation_id, created_at)`: ordered conversation history
- `created_at desc`: operational inspection

Inference logs:

- `created_at desc`: recent metrics
- `(provider, model)`: usage breakdown
- `(conversation_id, created_at)`: trace logs by conversation
- `status`: error-rate filtering

## Deployment

The frontend is a standalone Next.js build suitable for Vercel or containerized hosting. The backend is a single ASGI service `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
