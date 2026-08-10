# BRD-Agent backend — implementation plan v1

## Scope of this doc

A plan for the real backend, before any code gets written. Covers: tech
stack, directory layout, how each layer talks to the next, how every
entity in `../brainstorming/erd.md` maps to a table/model, how every
endpoint in `../brainstorming/api_contract.md` maps to a
route → controller → service → repository chain, migration order, and a
phased build order. Once this is reviewed, implementation starts from
here — this doc is the reference point for what "done" looks like at
each phase.

**Data model and API surface: this project's own**, exactly as designed
in `../brainstorming/erd.md` and `../brainstorming/api_contract.md` this
session (recursive `Section` tree, arbitrary CustomSection nesting,
computed display codes, rename/delete, `last_generated_at`, `purpose`,
`missing_items`, `answered_at`, and now real email+password auth — the
full current version of those two docs). Nothing here is ported from
any other project's schema.

**Directory convention borrowed on purpose:** `controllers → services →
repositories`, plus `dtos` / `models` / `middleware` / `routes` / `utils`
as separate layers — a layout you already use elsewhere, translated to
idiomatic Python/FastAPI rather than copied file-for-file from a Go
project. The mapping below is deliberate, not incidental:

| Layer | Go convention | FastAPI equivalent |
| --- | --- | --- |
| `routes/` | route registration (`gin.Engine`) | `APIRouter` instances, just path → controller wiring |
| `controllers/` | Gin handlers, thin | FastAPI path functions, thin — parse request, call one service method, return |
| `dtos/` | request/response structs | Pydantic models — also what FastAPI uses for OpenAPI schema + validation |
| `models/` | domain structs | SQLAlchemy ORM models — one per `erd.md` entity |
| `repositories/` | DB access, no business logic | same role, SQLAlchemy queries only, no business logic |
| `services/` | business logic | same role — tree building, code computation, flagged detection, merge logic |
| `middleware/` | logging, CORS, error handling | FastAPI middleware + exception handlers |
| `utils/` | id generation, helpers | same |

**Scope of this team's job:** build the app — data model, CRUD, auth,
tree logic, review/flagged detection, document export. **Not** the AI
inferencing itself — that's a separate team's work, integrated later
behind one seam (see "AI integration boundary" below). Nothing in this
plan designs prompts, model calls, or conversational behavior.

## Tech stack

| Piece | Choice | Why |
| --- | --- | --- |
| Framework | FastAPI | per your instruction — full Python, no Go |
| Validation / DTOs | Pydantic v2 | FastAPI's native request/response layer; `snake_case` field names match `api_contract.md`'s wire convention directly, no translation layer needed |
| DB | **PostgreSQL** | confirmed — matches `CLAUDE.md`'s existing "Leaning PostgreSQL" |
| ORM | SQLAlchemy 2.0 (async) | de facto standard, works cleanly with FastAPI's async request handling |
| DB driver | `asyncpg` | the standard async Postgres driver SQLAlchemy 2.0 async expects |
| Migrations | Alembic | standard SQLAlchemy migration tool |
| Server | Uvicorn | ASGI server FastAPI expects |
| Password hashing | `passlib[bcrypt]` (or `pwdlib`) | standard, well-audited — never roll your own hashing |
| Auth tokens | JWT (`python-jose` or `pyjwt`) | see Auth section below |
| AI orchestration | one stub interface, owned by the AI team | see "AI integration boundary" below |

### PostgreSQL setup

- **Local dev**: a `postgres` service in `docker-compose.yml` (data
  volume mounted, standard `POSTGRES_USER`/`POSTGRES_PASSWORD`/
  `POSTGRES_DB` env vars), same pattern as any other containerized dev
  DB — nothing unusual needed here.
- **Connection**: `DATABASE_URL` env var,
  `postgresql+asyncpg://user:pass@host:5432/brdagent`, read once in
  `config.py` via `pydantic-settings` — never hardcoded, matches
  `CLAUDE.md`'s existing "no backend-secret values in `.env`" rule for
  the frontend, same principle applied here.
- **Connection pooling**: SQLAlchemy's `create_async_engine` default
  pool is fine to start (`pool_size`/`max_overflow` defaults) — no need
  to hand-tune this before there's real load to measure.
- **Migrations**: Alembic's `env.py` reads the same `DATABASE_URL`, so
  `alembic upgrade head` is the one command that brings a fresh
  Postgres instance to the current schema — no manual SQL ever run by
  hand outside of migration files.
- **Array column**: `ANSWER.missing_items` (`erd.md`) uses Postgres's
  native `ARRAY(String)` type via SQLAlchemy — no separate join table
  needed for a handful of short strings, and this specific column type
  is one of the reasons Postgres was already the right call over
  something like SQLite for this project.

## Directory structure

```
backend/
  app/
    main.py                      # FastAPI() instance, mounts routers, middleware, startup/shutdown
    config.py                    # pydantic-settings: DATABASE_URL, JWT_SECRET, CORS origins — env-driven, no hardcoded values

    routes/
      __init__.py                # aggregates all routers into one APIRouter
      auth.py                    # /auth/register, /auth/login, /auth/session, /auth/logout
      conversations.py           # /api/conversations, /api/conversations/{id}
      chat.py                    # /api/conversations/{id}/rooms/{room_id}/messages
      custom_sections.py         # /api/conversations/{id}/custom-sections...
      review.py                  # /api/conversations/{id}/review/recompute
      documents.py                # /api/conversations/{id}/generate

    controllers/
      __init__.py
      auth_controller.py
      conversation_controller.py
      chat_controller.py
      custom_section_controller.py
      review_controller.py
      document_controller.py

    dtos/
      __init__.py
      auth_dtos.py                # RegisterRequest, LoginRequest, AuthResponse (user + token)
      conversation_dtos.py        # ConversationListItem, ConversationDetail, CreateConversationRequest, ...
      section_dtos.py             # AnswerDto, CustomSectionNodeDto (recursive), FlaggedItemDto
      chat_dtos.py                 # MessageDto, PostMessageRequest
      custom_section_dtos.py      # AddCustomSectionRequest (target/title/has_children/purpose), RenameRequest
      review_dtos.py
      document_dtos.py

    models/
      __init__.py
      user.py                     # User — erd.md USER, incl. password_hash
      conversation.py             # Conversation — erd.md CONVERSATION
      section.py                  # Section — erd.md SECTION (self-referential parent_id)
      answer.py                   # Answer — erd.md ANSWER
      bubble.py                   # Bubble — erd.md BUBBLE
      section_dependency.py       # SectionDependency — erd.md SECTION_DEPENDENCY

    repositories/
      __init__.py
      user_repository.py
      conversation_repository.py
      section_repository.py
      answer_repository.py
      bubble_repository.py
      section_dependency_repository.py

    services/
      __init__.py
      auth_service.py             # register/login: hash/verify password, issue JWT
      conversation_service.py     # create/rename/delete, answered_count query, updated_at bumping
      section_tree_service.py     # builds the recursive custom_sections tree + computes display codes
                                   # (the Python port of customSectionTree.js's logic)
      template_service.py         # static app config: the 26-leaf template graph, dependsOn,
                                   # template_key lookups — the Python port of draftFields.js's SECTIONS
      chat_service.py             # postMessage: inserts Bubble rows, bumps ANSWER.answered_at
      custom_section_service.py   # add/rename/remove CustomSection nodes, cascading delete
      review_service.py           # flagged detection (SECTION_DEPENDENCY + answered_at join),
                                   # regenerates `reason` text on demand — never stored
      document_service.py         # builds the markdown doc (Python port of documentMarkdown.js),
                                   # bumps last_generated_at/last_generated_version
      ai_integration.py           # ONE stub function/interface — see AI integration boundary below.
                                   # This team owns the seam, not what's behind it.

    middleware/
      __init__.py
      auth.py                     # get_current_user FastAPI dependency — verifies JWT, loads User, 401s otherwise
      error_handler.py            # maps domain exceptions -> {error, message} + status code, matching api_contract.md's error shapes
      cors.py
      logging.py

    utils/
      __init__.py
      ids.py                      # UUID/ULID generation — never slugified from title, per api_contract.md §0
      time.py                     # server-side timestamp helpers

  migrations/                     # Alembic
    env.py
    versions/

  tests/
    conftest.py                   # test DB fixture (separate test database or transactional rollback per test)
    test_auth_service.py
    test_conversation_service.py
    test_section_tree_service.py
    test_review_service.py
    test_document_service.py
    test_custom_section_service.py
    # one test module per service — services hold the actual logic worth testing;
    # controllers/repositories get thinner integration-style coverage, not unit tests per function

  alembic.ini
  pyproject.toml                  # dependencies + tool config (ruff/pytest), replaces requirements.txt
  .env.example
  docker-compose.yml              # app + postgres, local dev
  Dockerfile
  implementation_1.md             # this file
```

## Layer responsibilities (the actual rule, not just the folder names)

- **`routes/`** — one `APIRouter` per resource group, mirroring
  `api_contract.md`'s numbered sections. Only path + HTTP verb + which
  controller function handles it. No logic.
- **`controllers/`** — parse the validated Pydantic request (FastAPI
  already did the parsing/validation before the function body runs),
  call exactly one service method, wrap the result in the response DTO.
  If a controller function has an `if` statement that isn't
  error-shape-related, that logic belongs in a service instead.
- **`dtos/`** — the wire contract. Every shape in `api_contract.md`
  becomes a Pydantic model here, field names `snake_case` to match
  directly (Pydantic's `alias_generator` isn't even needed — the models
  can just declare `snake_case` fields natively, since FastAPI is the
  only consumer of these and the frontend already does its own
  `camelCase` translation in `services/api.js` per `CLAUDE.md`).
- **`models/`** — SQLAlchemy ORM classes, one per `erd.md` entity,
  columns exactly matching that doc's attribute tables (see mapping
  below). No request/response shaping here — that's what `dtos/` is for.
- **`repositories/`** — SQLAlchemy queries only: fetch, insert, update,
  delete. A repository method returns models or primitives, never a DTO.
  No business rules (e.g. "is this leaf blocked" does not belong here).
- **`services/`** — everything `erd.md`'s Decisions log actually
  decided how to compute: display codes, `answered_count`, flagged
  detection, cascading delete, `reason` regeneration, markdown building,
  password verification. A service calls one or more repositories and
  returns domain data — controllers turn that into DTOs, not services.
- **`middleware/`** — cross-cutting only: CORS, request logging, JWT
  verification (`get_current_user`, used as a FastAPI `Depends` on every
  protected route), and one central exception handler that turns raised
  domain exceptions (e.g. `TitleRequiredError`, `InvalidCredentialsError`)
  into the `{error, message}` JSON shape `api_contract.md` already
  documents per endpoint, so individual controllers don't each
  hand-write error responses.

## Entity → model mapping

Directly from `erd.md`'s Entity attribute reference — every column
listed there becomes a SQLAlchemy column here, same name, same
nullability. Nothing added, nothing skipped:

| `erd.md` entity | `models/` file | Notes |
| --- | --- | --- |
| `USER` | `user.py` | `password_hash` (bcrypt/argon2, never returned in any response), `email` unique-constrained, `created_at` |
| `CONVERSATION` | `conversation.py` | Includes `last_generated_at`/`last_generated_version` (nullable); `user_id` FK now enforced on every query — see Auth below |
| `SECTION` | `section.py` | Self-referential `parent_id` FK; `purpose` nullable, only meaningful when `is_custom=True` |
| `ANSWER` | `answer.py` | `missing_items` as a Postgres `ARRAY(String)` column; `answered_at` nullable |
| `BUBBLE` | `bubble.py` | Immutable once created — no update path needed |
| `SECTION_DEPENDENCY` | `section_dependency.py` | Composite key (`section_id`, `depends_on_section_id`), no surrogate PK needed |

`answered_count` and CustomSection display codes are **not columns
anywhere** — per `erd.md`'s explicit decision, both stay computed. That
logic lives in `conversation_service.py` (a query, see below) and
`section_tree_service.py` (Python recursion over an already-fetched flat
list — no recursive SQL needed at this data size; fetch every `Section`
row for the conversation once, ordered by `parent_id, sort_order`, and
build the tree + codes in memory, the same way `customSectionTree.js`
does it client-side today).

## Auth: real email+password (not SSO, not yet)

Per your call: build actual registration/login now so the app has a
real, working auth boundary from day one, instead of leaving `/auth` as
a placeholder until SSO specifics are known. SSO stays a later addition
on top of this, not something blocking it (`erd.md`'s Auth decision).

- **`POST /auth/register`** (`AuthService.register`) — validates email
  isn't already taken (`UserRepository.find_by_email`), hashes the
  password (`passlib`'s `bcrypt` scheme), inserts the `User` row,
  issues a JWT the same way login does, returns `{user, token}`.
- **`POST /auth/login`** (`AuthService.login`) — looks up by email,
  verifies the password hash, issues a JWT (`sub` claim = `user_id`,
  reasonable expiry, e.g. 7 days — revisit once there's a real security
  review). Same generic `invalid_credentials` error whether the email
  doesn't exist or the password is wrong (`api_contract.md` §1 — avoids
  leaking which emails are registered).
- **`GET /auth/session`** — the `get_current_user` dependency already
  had to verify the token to reach the handler at all, so this endpoint
  is just "return that user."
- **`POST /auth/logout`** — `204`, no server-side state to clear yet
  (stateless JWT) — see `api_contract.md` §1 for why this is still a
  real endpoint anyway.
- **`middleware/auth.py`'s `get_current_user`** is a FastAPI
  dependency (`Depends(get_current_user)`) added to every controller
  under `/api/...` — decodes the `Authorization: Bearer <token>` header,
  loads the `User`, or raises `401`. This is also what makes
  `Conversation.user_id` real: `ConversationService.create`/`list_for_user`
  etc. take the authenticated user from this dependency, not from
  anything the client passes in the request body.
- **Not building in this pass**: password reset/forgot-password flow,
  email verification, rate limiting on login attempts. Minimal viable
  auth first — these are natural, contained follow-ups once the rest of
  the app is working, not blockers for it.

## AI integration boundary

This team's job stops at exposing one clean seam — not designing what's
behind it. `services/ai_integration.py` holds a single function/interface
(shape TBD by the AI team, e.g. `async def get_reply(room_context) -> AgentReply`)
that `chat_service.py`/`document_service.py` call through. Until the AI
team implements it, it returns a fixed placeholder reply — enough for
`ChatService`/`DocumentService` to be fully built, tested, and demoed
end-to-end (real `Bubble` rows, real `answered_at` bumps, real markdown
generation from whatever's in the DB) without waiting on any model
integration. When the AI team is ready, they implement the other side of
that one function — nothing in `controllers/`, `dtos/`, `models/`, or any
other service needs to change.

## Endpoint → layer mapping

One row per `api_contract.md` endpoint. `Service method` is the one
place the actual logic lives; controller/repository are mechanical.

### Auth (§1)

| Endpoint | Controller | Service method | Repository calls |
| --- | --- | --- | --- |
| `POST /auth/register` | `register` | `AuthService.register` | `UserRepository.find_by_email`, `UserRepository.insert` |
| `POST /auth/login` | `login` | `AuthService.login` | `UserRepository.find_by_email` |
| `GET /auth/session` | `get_session` | — (just returns the `get_current_user` result) | `UserRepository.find_by_id` (via the auth dependency) |
| `POST /auth/logout` | `logout` | — (no-op, `204`) | none |

### Conversations (§2)

| Endpoint | Controller | Service method | Repository calls |
| --- | --- | --- | --- |
| `GET /api/conversations` | `list_conversations` | `ConversationService.list_for_user` | `ConversationRepository.list_by_user` + per-row `answered_count` query |
| `POST /api/conversations` | `create_conversation` | `ConversationService.create` | `ConversationRepository.insert` + `SectionRepository.seed_template_tree` (see Seeding below) |
| `PATCH /api/conversations/{id}` | `rename_conversation` | `ConversationService.rename` | `ConversationRepository.update_title` |
| `DELETE /api/conversations/{id}` | `delete_conversation` | `ConversationService.delete` | `ConversationRepository.delete` (cascades via FK `ON DELETE CASCADE`) |
| `GET /api/conversations/{id}` | `get_conversation_detail` | `ConversationService.get_detail` | fans out to `SectionRepository`, `AnswerRepository`, `BubbleRepository`, then `SectionTreeService.build_custom_tree` |

Every row above also checks the conversation's `user_id` matches
`get_current_user`'s result — a `404` (not `403`, to avoid confirming a
conversation id exists at all to someone who doesn't own it) if not.

### Chat / Rooms (§3)

| Endpoint | Controller | Service method | Repository calls |
| --- | --- | --- | --- |
| `POST /api/conversations/{id}/rooms/{room_id}/messages` | `post_message` | `ChatService.post_message` | `BubbleRepository.insert` (user + agent turn) → `AnswerRepository.touch_answered_at` if the turn changed that leaf's answer → `ai_integration.get_reply` (stubbed, see above) |

### Custom Sections (§4)

| Endpoint | Controller | Service method | Repository calls |
| --- | --- | --- | --- |
| `POST /api/conversations/{id}/custom-sections` | `add_custom_section` | `CustomSectionService.add_node` | `SectionRepository.insert` (sets `parent_id` per `target.kind`) |
| `PATCH /api/conversations/{id}/custom-sections/{section_id}` | `rename_custom_section` | `CustomSectionService.rename_node` | `SectionRepository.update_title` |
| `DELETE /api/conversations/{id}/custom-sections/{section_id}` | `remove_custom_section` | `CustomSectionService.remove_node` | `SectionRepository.delete_cascading` (descendants via `ON DELETE CASCADE` on `parent_id`) |

### Review (§5)

| Endpoint | Controller | Service method | Repository calls |
| --- | --- | --- | --- |
| `POST /api/conversations/{id}/review/recompute` | `recompute_review` | `ReviewService.recompute` | `SectionDependencyRepository.find_flagged` (the join query from `erd.md`) — `reason` text built in-service from template copy, never stored |

### Document Generation (§6)

| Endpoint | Controller | Service method | Repository calls |
| --- | --- | --- | --- |
| `POST /api/conversations/{id}/generate` | `generate_document` | `DocumentService.generate` | reads full tree + answers (same fan-out as `GET .../{id}`), builds markdown, then `ConversationRepository.update_generation_metadata` (sets `last_generated_at`/`last_generated_version`) |

## Seeding: how a new Conversation gets its 26 template `Section` rows

Per `erd.md`'s decision (application code, not a DB trigger):
`ConversationService.create` calls `template_service.get_template_tree()`
(the Python port of `draftFields.js`'s static `SECTIONS` — same 26
leaves, same `dependsOn`, same `template_key` values) and
`SectionRepository.seed_template_tree` bulk-inserts one `Section` row per
template node (`is_custom=False`, `template_key` set, `parent_id` mirrors
the template's own nesting) plus one `SECTION_DEPENDENCY` row per
`dependsOn` edge, plus the one synthetic `is_general=True` row for
General chat. This runs once, inside the same transaction as the
`Conversation` insert.

## Flagged detection & `reason` text (Review service)

Directly implements `erd.md`'s worked query:
```sql
SELECT dependent.section_id
FROM section_dependencies sd
JOIN answers dependent ON dependent.section_id = sd.section_id
JOIN answers prereq ON prereq.section_id = sd.depends_on_section_id
WHERE dependent.status IN ('done', 'review')
  AND prereq.answered_at > dependent.answered_at;
```
`ReviewService.recompute` runs this via SQLAlchemy, then for each row
builds `reason` from `template_service`'s static copy (never stored, per
`erd.md`'s decision) plus the two sections' titles/codes.

## Migrations (Alembic)

One migration per entity, in dependency order:
1. `users` (incl. `password_hash`, `created_at`)
2. `conversations` (FK → `users`)
3. `sections` (FK → `conversations`, self-referential FK → `sections`)
4. `answers` (FK → `sections`, 1:1)
5. `bubbles` (FK → `sections`)
6. `section_dependencies` (composite FK → `sections` ×2)

All FKs from a conversation's children back up to `conversations` use
`ON DELETE CASCADE` — matches the existing `DELETE /api/conversations/{id}`
behavior (deleting a Conversation removes its Sections, Answers, Bubbles,
dependencies) without needing application-level cascade logic. Same for
`sections.parent_id` self-reference, so deleting a CustomSection group
cascades to its descendants at the DB level, not just in
`CustomSectionService`.

## Testing approach

- **Services get real unit tests** — this is where the actual logic
  lives (auth hashing/verification, tree building, code computation,
  flagged detection, seeding). Repositories mocked or hit against a
  real test-transaction DB, whichever proves less brittle once written.
- **Repositories get integration tests** against a real (test) Postgres
  instance — SQLAlchemy query correctness, cascade behavior.
- **Controllers get thin request/response contract tests** — status
  codes and DTO shapes matching `api_contract.md`, not business-logic
  re-verification (that's the service tests' job). Auth-protected routes
  get one test each confirming a missing/invalid token 401s.

## Frontend integration point

No frontend changes needed beyond `frontend/src/services/api.js`'s
internals (per `CLAUDE.md`'s "Mocking strategy" — this is the one file
that's allowed to change). Concretely: swap each function's body from
"read/write the in-memory `store`" to `fetch(`${VITE_API_BASE_URL}/...`)`
calls matching this backend's routes, storing the JWT from
login/register and attaching it as `Authorization: Bearer <token>` on
every subsequent call — keep the same function signatures so no
component needs to change. `.env`'s `VITE_API_BASE_URL` points at this
backend once it's running instead of nothing.

## Phased build order

1. **Auth** — register/login/session/logout, `get_current_user`
   dependency. Everything after this point is built as authenticated
   from the start, not bolted on later.
2. **Conversations CRUD + template seeding** — `GET/POST/PATCH/DELETE /api/conversations`,
   `GET /api/conversations/{id}` returning the 26 seeded template leaves
   with empty answers, scoped to the logged-in user. Proves the
   directory layout, DB connection, migrations, and seeding all work
   end to end.
3. **Chat / Rooms**, AI integration stubbed — `POST .../messages`
   inserting real `Bubble` rows and bumping `answered_at`, reply from
   the stub in `ai_integration.py`.
4. **CustomSections** — add/rename/remove, arbitrary nesting, computed
   display codes. The most logic-dense phase (`SectionTreeService`).
5. **Review** — flagged detection query + `reason` generation.
6. **Document generation** — markdown building (Python port of
   `documentMarkdown.js`), `last_generated_at`/`last_generated_version`.
7. **Handoff to the AI team** — `ai_integration.py`'s interface is the
   deliverable; whatever they build behind it doesn't require changes
   to phases 1–6.

Each phase should be independently demoable against the real frontend
(`VITE_API_BASE_URL` pointed at this backend) before moving to the next
— not built end-to-end blind.

## Open questions this plan doesn't resolve

- Exact JWT expiry/refresh strategy — a reasonable default (e.g. 7-day
  expiry, no refresh token yet) is enough to unblock building; revisit
  before any real deployment.
- Password reset, email verification, login rate-limiting — deliberately
  out of scope for this pass, see Auth section above.
- The shape of `ai_integration.py`'s interface is a placeholder guess —
  the AI team should have real input on it once they're engaged, this
  isn't meant to lock them into a specific function signature.
- Whether `answered_count`'s per-row query (§ "Entity → model mapping")
  needs to become a single batched query across the whole list instead
  of N+1 per conversation, once real data volume exists — flagged, not
  solved, since it's a performance question with no signal yet either way.
