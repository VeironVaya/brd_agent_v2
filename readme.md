# BRD-Agent

A conversational tool that walks a user through an org's 26-question
Business Requirement Document template via chat. A structured draft
builds up live next to the conversation as the user answers — tracking
completion and confidence per question, supporting user-added custom
sections (nested to any depth), flagging answers for re-review when a
question they depended on changes, letting the owner share a BRD with
other users as an editor or viewer, and generating a final PDF/Markdown
document at the end.

### Project structure

```
brd-app/
├── docker-compose.yml       # postgres + app + frontend services for local dev
│
├── backend/                 # FastAPI — controllers → services → repositories
│   ├── app/
│   │   ├── main.py          # app entrypoint, mounts routers + middleware
│   │   │
│   │   ├── core/            # core infrastructure
│   │   │   ├── config.py    # env-driven settings (DATABASE_URL, JWT_SECRET, ...)
│   │   │   ├── db.py        # SQLAlchemy async engine/session
│   │   │   └── exceptions.py# domain exceptions -> {error, message} JSON shape
│   │   │
│   │   ├── routes/          # APIRouters — path + verb -> controller, no logic
│   │   ├── controllers/     # thin: parse request, call one service, commit & return
│   │   ├── dtos/            # Pydantic request/response shapes (the wire contract)
│   │   ├── models/          # SQLAlchemy ORM entities (User, Conversation, Answer, ...)
│   │   ├── repositories/    # DB queries only, no business rules
│   │   │
│   │   ├── services/        # normal backend business logic & orchestration:
│   │   │   ├── chat_service.py / chat.py               # message posting, focus tracking
│   │   │   ├── conversation_service.py / conversation.py # CRUD + template seeding
│   │   │   ├── document_service.py / document.py       # Markdown/PDF export
│   │   │   ├── template_service.py / template.py       # static 26-leaf template config
│   │   │   ├── section_tree_service.py / section_tree.py # recursive CustomSection tree
│   │   │   ├── brd_rules.py                            # BRD dependency matrix
│   │   │   ├── brd_group_service.py
│   │   │   ├── choice_section_service.py
│   │   │   ├── custom_section_service.py
│   │   │   ├── review_service.py
│   │   │   └── share_service.py
│   │   │
│   │   ├── ai/              # AI subsystem (modular separation of responsibilities)
│   │   │   ├── drafter/     # AGENT 1: Conversational BRD Drafter
│   │   │   │   ├── service.py   # generation & revision logic (get_reply)
│   │   │   │   ├── prompt.py    # official SYSTEM_PROMPT
│   │   │   │   └── schema.py    # AgentReply, LLMReplySchema
│   │   │   │
│   │   │   ├── judge/       # AGENT 2: Senior BA Reviewer / Judge
│   │   │   │   ├── service.py   # 2-stage evaluation orchestration (evaluate_section)
│   │   │   │   ├── scoring.py   # deterministic confidence scoring & rubric mapping
│   │   │   │   ├── prompt.py    # Stage A (Verifier/Grader) & Stage B (Critic) prompts
│   │   │   │   ├── rubrics.py   # 4 global rubrics + 26 field-specific rubrics
│   │   │   │   └── schema.py    # structured Judge I/O schemas
│   │   │   │
│   │   │   ├── validator.py # HARD VALIDATOR: anti-hallucination fact checking
│   │   │   │
│   │   │   └── rag/         # RAG & Knowledge Base Subsystem
│   │   │       ├── embeddings.py       # vector embeddings generator
│   │   │       ├── retrieval.py        # pgvector semantic reference search
│   │   │       ├── models.py           # RAG data models (SearchResult, etc.)
│   │   │       ├── legacy_confidence.py# legacy 50/30/20 confidence utilities
│   │   │       ├── config/             # canonical fields & reference corpus JSON
│   │   │       └── ingest/             # reference document ingestion pipeline
│   │   │
│   │   ├── middleware/      # auth (JWT), CORS, logging, error handling
│   │   └── utils/           # id generation, etc.
│   │
│   ├── migrations/          # Alembic schema history
│   ├── tests/               # pytest — real Postgres, real HTTP requests
│   └── implementation_1.md  # the original build plan (historical record)
│
├── frontend/                # React + Vite
│   ├── Dockerfile           # dev-mode container (runs `npm run dev`), bind-mounted
│   └── src/
│       ├── pages/           # LoginPage, ConversationsPage, DraftSessionPage, ExportPage
│       ├── components/
│       │   ├── Chat/        # message thread, room tabs
│       │   ├── DraftPanel/  # section tree, progress, custom-section modals
│       │   ├── Sidebar/     # conversation list pieces
│       │   └── common/      # buttons, modals, form fields
│       ├── services/api.js  # the ONLY file that talks to the backend
│       └── utils/           # draftFields.js, customSectionTree.js, documentPdf.js
│
├── bruno/                   # API collection — testing + runnable docs
└── brainstorming/           # erd.md, api_contract.md, integration_1.md
```

## Runtime Flow

```text
User
  │ (Chat input)
  ▼
API Layer (routes → controllers)
  │
  ▼
Chat Service (app/services/chat_service.py)
  │
  ▼
Agent 1 Drafter (app/ai/drafter/service.py)
  │ [Generates/revises section draft, answer_text, completeness]
  ▼
Hard Validator (app/ai/validator.py)
  │ [Checks unconfirmed numbers, metrics, SLAs against confirmed user evidence]
  ▼
RAG References (app/ai/rag/retrieval.py)
  │ [Retrieves top reference BRD chunks as benchmark context]
  ▼
Agent 2 Stage A: Verifier & Grader (app/ai/judge/service.py)
  │ [Labels rubric criteria: MET, MOSTLY_MET, PARTIALLY_MET, NOT_MET, N_A]
  ▼
Deterministic Judge Scoring (app/ai/judge/scoring.py)
  │ [Averages components, renormalizes N_A weights, computes final confidence 0-100]
  ▼
Agent 2 Stage B: Critic (app/ai/judge/service.py)
  │ [Generates qualitative critique, strengths, issues, suggestions]
  ▼
Repositories (app/repositories/)
  │ [Persists answer, bubbles, confidence breakdown]
  ▼
Database (PostgreSQL)
  │
  ▼
Frontend (React Live Draft Panel & Chat UI)
```

## Running it locally

**Everything, one command** (repo root):
```
docker compose up -d --build
```
Brings up Postgres, the backend (runs its own migrations on boot), and
the frontend dev server (hot-reload still works — the container bind-mounts
your local `frontend/` source). Open **http://127.0.0.1:5173** — register
an account, no seed data, first run starts empty.

> **Use `127.0.0.1:5173`, not `localhost:5173`.** On Docker Desktop +
> WSL2 (Windows), `localhost` can resolve to `::1` first, which WSL2's
> own `wslrelay.exe` process separately binds — causing
> `ERR_CONNECTION_RESET` even though Docker's own proxy is listening
> correctly on `0.0.0.0`. `127.0.0.1` sidesteps it entirely. If you're
> not on that combination this may not affect you, but `127.0.0.1` is
> the safe default either way — it's what `docker-compose.yml`'s own
> `VITE_API_BASE_URL` uses internally.

**Rebuilding after a dependency change:** `docker compose up -d --build`
again — only rebuilds the images that actually changed.

**Running services individually** (e.g. for faster backend iteration
without a Docker image rebuild per change):
```
docker compose up -d postgres                             # just the DB
cd backend && .venv\Scripts\activate && alembic upgrade head
cd backend && uvicorn app.main:app --reload                # :8000
cd frontend && npm run dev                                 # :5173
```
First-time backend setup: `python -m venv .venv` then
`.venv\Scripts\pip install -e ".[dev]"` inside `backend/`.

## Testing

```
cd backend && pytest                                    # 45 tests, real DB
cd bruno && npx @usebruno/cli run --env Local -r         # 45 requests, 72 assertions
```

Both are black-box — real HTTP requests against the real API, not
mocked. See `bruno/README.md` for what the collection covers.

## More context

- `CLAUDE.md` — the fuller project brief (naming glossary, what's
  decided vs. still open, where the API contract lives)
- `brainstorming/erd.md` / `api_contract.md` — schema and wire-shape
  source of truth, kept current
- `brainstorming/integration_1.md` — narrative of how the backend build
  actually went
