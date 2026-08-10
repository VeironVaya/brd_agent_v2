# BRD-Agent

A conversational tool that walks a user through an org's 26-question
Business Requirement Document template via chat. A structured draft
builds up live next to the conversation as the user answers — tracking
completion and confidence per question, supporting user-added custom
sections (nested to any depth), flagging answers for re-review when a
question they depended on changes, and generating a final PDF/Markdown
document at the end.

AI responses are currently a fixed placeholder (see [AI integration](#ai-integration)
below) — everything else (auth, the 26-question tree, custom sections,
review/flagging, document export) is real, running against a real
PostgreSQL database.

## Project structure

```
brd_agent_v2/
├── docker-compose.yml       # postgres + app services for local dev
│
├── backend/                 # FastAPI — controllers → services → repositories
│   ├── app/
│   │   ├── main.py          # app entrypoint, mounts routers + middleware
│   │   ├── config.py        # env-driven settings (DATABASE_URL, JWT_SECRET, ...)
│   │   ├── db.py            # SQLAlchemy async engine/session
│   │   ├── exceptions.py    # domain exceptions -> {error, message} JSON shape
│   │   ├── routes/          # APIRouters — path + verb -> controller, no logic
│   │   ├── controllers/     # thin: parse request, call one service, return
│   │   ├── dtos/             # Pydantic request/response shapes (the wire contract)
│   │   ├── models/           # SQLAlchemy ORM — one per brainstorming/erd.md entity
│   │   ├── repositories/     # DB queries only, no business rules
│   │   ├── services/         # the actual logic:
│   │   │   ├── conversation_service.py    # CRUD + template seeding
│   │   │   ├── section_tree_service.py    # recursive CustomSection tree + codes
│   │   │   ├── template_service.py        # static 26-leaf template config
│   │   │   ├── chat_service.py            # message posting, focus tracking
│   │   │   ├── custom_section_service.py  # add/rename/remove, arbitrary nesting
│   │   │   ├── review_service.py          # flagged-item detection
│   │   │   ├── document_service.py        # Markdown/PDF export
│   │   │   └── ai_integration.py          # <- DUMMY AI, see below
│   │   ├── middleware/       # auth (JWT), CORS, logging, error handling
│   │   └── utils/            # id generation, etc.
│   ├── migrations/          # Alembic schema history
│   ├── tests/                # pytest — real Postgres, real HTTP requests
│   └── implementation_1.md  # the original build plan (historical record)
│
├── frontend/                 # React + Vite
│   ├── Dockerfile            # dev-mode container (runs `npm run dev`), bind-mounted
│   │                         # for hot reload — see docker-compose.yml's frontend service
│   └── src/
│       ├── pages/            # LoginPage, ConversationsPage, DraftSessionPage, ExportPage
│       ├── components/
│       │   ├── Chat/         # message thread, room tabs
│       │   ├── DraftPanel/   # section tree, progress, custom-section modals
│       │   ├── Sidebar/      # conversation list pieces
│       │   └── common/       # buttons, modals, form fields
│       ├── services/api.js   # the ONLY file that talks to the backend
│       └── utils/            # draftFields.js (template config, mirrors
│                              # template_service.py), customSectionTree.js
│                              # (mirrors section_tree_service.py), documentPdf.js
│
├── bruno/                    # API collection — testing + runnable docs, see its README
│
└── brainstorming/            # gitignored — erd.md, api_contract.md (the contract,
                               # kept current), integration_1.md (how the backend
                               # build actually went, bugs found, decisions made)
```

## AI integration

Every chat reply right now is a fixed placeholder string, deliberately
centralized in `backend/app/services/ai_integration.py` (search the
codebase for `DUMMY_AI`). Nothing else in the backend contains
model/prompt logic — that file is the one seam a real AI integration
plugs into later without anything else needing to change.

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
cd backend && pytest                                    # 33 tests, real DB
cd bruno && npx @usebruno/cli run --env Local -r         # 24 requests, 39 assertions
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
