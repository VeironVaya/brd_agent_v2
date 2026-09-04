# BRD-Agent

A conversational tool that walks a user through an organisation's 26-question
Business Requirement Document template via chat. A structured draft builds up
live next to the conversation as the user answers — tracking completeness and
confidence per section, enforcing a `dependsOn` graph between sections,
supporting user-added custom sections (nested to any depth), flagging answers
for re-review when a dependency changes, letting the owner share a BRD with
other users as an editor or viewer, organising BRDs into shareable groups, and
generating a final PDF/Markdown/DOCX document at the end.

AI responses are powered by **LiteLLM** routing to **Groq** (`llama-3.3-70b-versatile`,
primary) with **Gemini** as fallback. If no API key is configured, a deterministic
placeholder keeps the rest of the pipeline exercisable. Everything else — auth
with real server-side logout revocation, the 26-question tree with a full
dependency rules engine, choice-based sections, custom sections, review/flagging,
sharing, BRD groups, and document export — is real, running against a real
PostgreSQL database.

---

## Tech stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI + Python 3.11+, layered `controllers ? services ? repositories` |
| **Database** | PostgreSQL 16, SQLAlchemy 2.0 async ORM, Alembic migrations |
| **Auth** | bcrypt password hashing + JWT bearer tokens, real server-side logout via `REVOKED_TOKEN` denylist |
| **AI** | LiteLLM — primary: `groq/llama-3.3-70b-versatile`, fallbacks: Gemini models |
| **Frontend** | React 18 + Vite 5, React Router v6, TailwindCSS v4 |
| **Export** | Server-side Markdown, client-side PDF via jsPDF, client-side DOCX via docx |
| **Testing** | pytest (black-box HTTP), Bruno API collection |
| **Container** | Docker Compose — postgres + app + frontend services |

---

## Project structure

```
brd_agent_v2/
+-- docker-compose.yml       # postgres + app + frontend for local dev
-
+-- backend/
-   +-- app/
-   -   +-- main.py          # FastAPI entrypoint - routers + middleware + lifespan
-   -   +-- config.py        # env-driven settings (DATABASE_URL, JWT_SECRET,
-   -   -                    #   GROQ_API_KEY, GEMINI_API_KEY, ...)
-   -   +-- db.py            # SQLAlchemy async engine/session
-   -   +-- exceptions.py    # domain exceptions ? {error, message} JSON shape
-   -   +-- routes/          # APIRouters - path + verb ? controller, no logic
-   -   -   +-- auth.py
-   -   -   +-- conversations.py
-   -   -   +-- chat.py
-   -   -   +-- choices.py       # choice-based section answers (1.3, 1.4, ...)
-   -   -   +-- custom_sections.py
-   -   -   +-- review.py
-   -   -   +-- documents.py
-   -   -   +-- shares.py
-   -   -   +-- brd_groups.py    # group CRUD + group sharing
-   -   +-- controllers/     # thin: parse request ? call service ? return DTO
-   -   +-- dtos/            # Pydantic request/response shapes (wire contract)
-   -   +-- models/          # SQLAlchemy ORM - one per ERD entity
-   -   -   +-- user.py
-   -   -   +-- conversation.py
-   -   -   +-- section.py
-   -   -   +-- section_dependency.py
-   -   -   +-- answer.py
-   -   -   +-- bubble.py        # chat messages
-   -   -   +-- collaborator.py  # per-BRD sharing
-   -   -   +-- brd_group.py     # folder-like BRD groups
-   -   -   +-- group_collaborator.py
-   -   -   +-- revoked_token.py
-   -   +-- repositories/    # DB queries only, no business rules
-   -   +-- services/        # all business logic lives here
-   -   -   +-- ai_integration.py      # LiteLLM router ? AgentReply
-   -   -   +-- brd_rules.py           # 26-section dependency rules engine
-   -   -   +-- auth_service.py        # register, login, logout, session
-   -   -   +-- conversation_service.py# CRUD + template seeding
-   -   -   +-- template_service.py    # static 26-leaf tree + dependsOn graph
-   -   -   +-- section_tree_service.py# recursive CustomSection tree + codes
-   -   -   +-- chat_service.py        # message posting, focus tracking
-   -   -   +-- choice_section_service.py # enum-answer sections (1.3, 1.4, ...)
-   -   -   +-- custom_section_service.py # add/rename/remove, arbitrary nesting
-   -   -   +-- review_service.py      # flagged-item detection
-   -   -   +-- document_service.py    # Markdown/PDF/DOCX export
-   -   -   +-- share_service.py       # per-BRD collaborator management
-   -   -   +-- brd_group_service.py   # group CRUD + group sharing
-   -   +-- middleware/      # CORS, auth (JWT), logging, error handling
-   -   +-- utils/           # id generation, etc.
-   +-- migrations/          # Alembic schema history
-   +-- tests/               # pytest — real Postgres, real HTTP requests
-   -   +-- conftest.py
-   -   +-- test_auth.py
-   -   +-- test_chat.py
-   -   +-- test_choices.py
-   -   +-- test_conversations.py
-   -   +-- test_custom_sections.py
-   -   +-- test_review_and_documents.py
-   -   +-- test_sharing.py
-   +-- pyproject.toml
-   +-- implementation_1.md  # original build plan (historical record)
-
+-- frontend/
-   +-- src/
-       +-- App.jsx          # routes + RequireAuth / RequireGuest guards
-       +-- pages/
-       -   +-- LoginPage.jsx          # register / login (email + password)
-       -   +-- ConversationsPage.jsx  # BRD list — My BRDs / Shared with me tabs,
-       -   -                          #   group cards, assign-to-group
-       -   +-- DraftSessionPage.jsx   # workspace: Chat + DraftPanel side-by-side
-       -   +-- ExportPage.jsx         # document preview + generate (PDF/DOCX)
-       +-- components/
-       -   +-- Chat/
-       -   -   +-- ChatHeader.jsx     # breadcrumb, Share button, room tabs
-       -   -   +-- FocusBar.jsx       # "Currently discussing: X" badge
-       -   -   +-- Message.jsx        # renders user / assistant / assumption pills
-       -   -   +-- MessageInput.jsx
-       -   -   +-- MessageThread.jsx
-       -   -   +-- ThinkingIndicator.jsx
-       -   +-- DraftPanel/
-       -   -   +-- SectionTree.jsx    # standard 26-leaf outline
-       -   -   +-- SectionRow.jsx     # status badge, completeness donut, focus
-       -   -   +-- CustomSectionRow.jsx / CustomSectionsList.jsx
-       -   -   +-- ProgressHeader.jsx # overall % complete + counts
-       -   -   +-- DonutBadge.jsx
-       -   -   +-- ConfidenceBreakdown.jsx # 5-dimension confidence panel
-       -   -   +-- AnswerDetailModal.jsx
-       -   -   +-- ReviewFlaggedModal.jsx
-       -   -   +-- SectionCompleteModal.jsx
-       -   -   +-- AddCustomSectionModal.jsx
-       -   -   +-- BoilerplateSection.jsx
-       -   +-- ChoiceSections/
-       -   -   +-- ChoiceSectionModal.jsx # multi-select picker for enum sections
-       -   +-- Sidebar/               # used on ConversationsPage
-       -   -   +-- ConversationRow.jsx    # owner kebab: Share/Rename/Delete/Assign
-       -   -   +-- GroupCard.jsx          # group folder card
-       -   -   +-- GroupModal.jsx         # create / rename group
-       -   -   +-- GroupShareModal.jsx    # share a group with collaborators
-       -   -   +-- AssignGroupModal.jsx   # assign a BRD to a group
-       -   -   +-- NewConversationModal.jsx
-       -   -   +-- EmptyState.jsx
-       -   +-- common/
-       -       +-- ShareModal.jsx     # per-BRD collaborator management
-       -       +-- UserMenu.jsx, Button.jsx, Modal.jsx, etc.
-       +-- contexts/
-       -   +-- AuthContext.jsx        # session state, login/logout
-       +-- services/
-       -   +-- api.js                 # ONLY file that talks to the backend
-       +-- utils/
-           +-- draftFields.js         # mirrors template_service.py — keep in sync
-           +-- customSectionTree.js   # mirrors section_tree_service.py
-           +-- choiceSections.js      # mirrors choice_section_service.py
-           +-- documentPdf.js         # client-side Markdown ? PDF (jsPDF)
-           +-- documentDocx.js        # client-side DOCX (docx library)
-           +-- documentMarkdown.js    # legacy dead code (server now owns Markdown)
-           +-- confidenceColors.js
-
+-- bruno/                   # Bruno API collection — every endpoint, checked in
-                            #   as .bru files; also a runnable test suite
+-- brainstorming/           # gitignored - erd.md, api_contract.md, guide.md, etc.
```

---

## BRD template

The template has **26 answerable leaf sections** across 5 top-level chapters,
plus a static "Document Signoff" boilerplate appended at export time.

| Chapter | Sections |
|---|---|
| **1 - Introduction** | 1.1.1 Background — 1.1.2 Business and Market Analysis — 1.1.3 Relevant Historical Data — 1.2 Business Objective — 1.3 Purpose *(choice)* — 1.4 Program Type *(choice)* — 1.5 Business Risk |
| **2 - Benefit Analysis** | 2.1 Summary — 2.2 Assumption and Calculation |
| **3 - Service Description** | 3.1 General Requirement — 3.2 Product/Service Specification — 3.3.1 Business Process Impact — 3.3.2 Description — 3.3.3 Security — 3.3.4 Organisation and Policy — 3.3.5 Service Delivery Plan — 3.4 Complaint Handling — 3.5 Reporting — 3.6 Monitoring — 3.7 Settlement Plan — 3.8 Assumptions and Dependencies |
| **4 - Release Plan** | 4.1 Target Ready for Service — 4.2 Commercial Launch — 4.3 Internal Socialisation Plan — 4.4 Rollout Scenario |
| **5 - Retirement Plan** | 5.1 Retirement Plan |

Sections are **gated by a `dependsOn` graph** - a section stays `locked` until
all its prerequisites reach `answered`. The graph is derived from the full BRD
dependency matrix (`brd_rules.py` + `template_service.py`).

**Choice sections** (1.3 *Purpose of this Business Requirement* and 1.4
*Program Type*) are answered via a structured multi-select modal instead of
chat, and their answers are written directly to the `Answer` row without going
through the LLM.

---

## AI integration

Every chat reply goes through `backend/app/services/ai_integration.py`, which
uses **LiteLLM** to route to:

- **Primary**: `groq/llama-3.3-70b-versatile`
- **Fallbacks**: `gemini/gemini-3.1-flash-lite`, `gemini/gemini-flash-latest`

The AI acts as a strict senior Business Analyst. It:

- Enforces a quality bar (no vague/unmeasurable language)
- Stays scoped to the currently focused section
- Injects context from prerequisite sections (via `brd_rules.py`) into its system prompt
- Returns structured JSON conforming to `LLMReplySchema`:
  `reply_text`, `answer_text`, `completeness` (0-100), `confidence` (0-100),
  `missing_items`, `is_assumption`, and an optional 5-dimension
  `confidence_breakdown` (`grounding`, `reference_context`, `section_compliance`,
  `testability`, `consistency`)
- Generates a contextual greeting when a user first opens a section

If neither `GROQ_API_KEY` nor `GEMINI_API_KEY` is set, a deterministic fallback
reply is returned so the rest of the app remains testable without model access.

---

## Running locally

**Everything, one command** (repo root):

```bash
docker compose up -d --build
```

Brings up Postgres, the backend (runs `alembic upgrade head` on boot, then
`uvicorn` with `--reload`), and the frontend dev server (source bind-mounted -
hot reload works inside the container). Open **http://127.0.0.1:5173**.

> **Use `127.0.0.1:5173`, not `localhost:5173`.**
> On Docker Desktop + WSL2 (Windows), `localhost` can resolve to `::1` first,
> which WSL2's own `wslrelay.exe` separately binds - causing
> `ERR_CONNECTION_RESET` even though Docker's proxy is listening on `0.0.0.0`.
> `127.0.0.1` sidesteps it entirely, and is what `docker-compose.yml`'s own
> `VITE_API_BASE_URL` uses internally.

**Rebuilding after a dependency change:** `docker compose up -d --build` again -
only rebuilds images that actually changed.

### Running services individually (faster backend iteration)

```bash
docker compose up -d postgres                        # just the DB

# backend
cd backend
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload                        # :8000

# frontend
cd frontend
npm install
npm run dev                                          # :5173
```

### Environment variables

`backend/.env` (gitignored - copy from `.env.example`):

| Variable | Required | Notes |
|---|---|---|
| `DATABASE_URL` | ? | e.g. `postgresql+asyncpg://brdagent:brdagent@localhost:5432/brdagent` |
| `JWT_SECRET` | ? | any long random string |
| `JWT_EXPIRY_HOURS` | optional | default `168` (7 days) |
| `CORS_ORIGINS` | optional | default `http://localhost:5173` |
| `GROQ_API_KEY` | optional* | primary LLM provider |
| `GEMINI_API_KEY` | optional* | fallback LLM provider |

*At least one API key is needed for real AI replies. Without either, a
deterministic placeholder is used.

`frontend/.env` only ever holds `VITE_API_BASE_URL` (e.g.
`http://127.0.0.1:8000`). No AI secrets belong on the frontend.

---

## Testing

```bash
# Backend integration tests - real Postgres, real HTTP (no mocks)
cd backend && pytest

# Bruno API collection — every endpoint, 72 assertions
cd bruno && npx @usebruno/cli run --env Local -r
```

Test coverage includes: auth (register, login, server-side logout revocation),
ownership/404 enforcement, template seeding, arbitrary-depth custom section
nesting, choice section answers, flagged/review detection, document generation
(Markdown), sharing (editor/viewer permission enforcement, role changes,
revocation, owner-only management), and the AI stub updating `Answer` rows
through real chat messages.

---

## Key concepts / naming glossary

| Term | Meaning |
|---|---|
| **Conversation** | One BRD in progress |
| **Owner** | The user who created a Conversation. Only the owner can rename/delete it or manage collaborators |
| **Collaborator** | A user a Conversation has been shared with by email, in one of two Roles |
| **Role** | `Editor` (chat + edit custom sections + export) or `Viewer` (view + export only) |
| **BRD Group** | A folder-like container that groups related Conversations. Shareable independently of the BRDs inside it |
| **Section** | A standard template outline node — header or leaf |
| **CustomSection** | A user-added outline node — either a single item (leaf, gets its own chat Room) or a group header with arbitrarily nested children |
| **Room** | The persistent chat thread for one leaf Section/CustomSection, or the general chat |
| **Answer** | The current recorded content + quality state for one leaf |
| **Completeness** | 0-100% — whether the answer meets the quality bar for this section (requires 100% completeness, >= 70% confidence, and 0 identified issues to mark as done) |
| **Confidence** | 0-100%, with 5-dimension breakdown: grounding, reference_context, section_compliance, testability, consistency |
| **Status** | `locked` / `ready` / `answered` / `needs_review` |
| **Flagged** | A completed answer that needs re-verification because a section it `dependsOn` changed after it was answered |
| **Focused** | The single section currently being discussed in chat |
| **Choice section** | A section answered via a structured multi-select picker rather than free-form chat (e.g. 1.3, 1.4) |
| **Boilerplate section** | A section (e.g. "Document Signoff") auto-filled from placeholders at export time; excluded from the 26-question completion count |

---

## Feature status

| Feature | Status |
|---|---|
| Conversations CRUD + 26-leaf template seeding | ? Real |
| `dependsOn` dependency graph + section locking | ? Real |
| Section rules engine (26-section quality prompts) | ? Real (`brd_rules.py`) |
| Chat (Rooms, Bubbles, focus tracking) | ? Real |
| Choice-based sections (1.3, 1.4 - multi-select) | ? Real |
| Custom sections (arbitrary depth) | ? Real |
| Flagged/review detection | ? Real |
| Document export (Markdown server-side, PDF + DOCX client-side) | ? Real |
| Sharing (per-BRD editor/viewer collaborators) | ? Real |
| BRD Groups (folder-like, shareable) | ? Real |
| AI via LiteLLM (Groq primary, Gemini fallback) | ? Real (requires API key) |
| 5-dimension confidence breakdown | ? Returned by AI; dummy fallback when unavailable |
| Auth (email+password, bcrypt, JWT, server-side logout) | ? Real |
| SSO | ? Out of scope - additive change once company specifics are known |
| Deployment/infra beyond local docker-compose | ? Out of scope |
| Full document-generation history (only latest export tracked) | ? Out of scope |

---

## More context

- `CLAUDE.md` - the fuller project brief (naming glossary, tech decisions, status)
- `brainstorming/erd.md` / `api_contract.md` - schema and wire-shape source of
  truth, kept current throughout the build
- `brainstorming/guide.md` - day-to-day operator reference: config knobs, auth
  mechanism, migration workflow, dependency-graph rules, symptom?cause?fix table
- `brainstorming/integration_1.md` - narrative of how the backend build actually
  went (bugs found, decisions made mid-build)
- `bruno/README.md` - what the API collection covers
