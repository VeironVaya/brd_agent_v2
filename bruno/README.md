# BRD-Agent API — Bruno collection

A [Bruno](https://www.usebruno.com/) collection covering every endpoint in
`../brainstorming/api_contract.md`, checked in as plain-text `.bru` files
so it stays diffable and versioned alongside the API itself — this is both
the test suite and the living, runnable documentation for the API surface.

## Using it

**GUI**: open Bruno, "Open Collection", point it at this folder. Select
the **Local** environment (top-right) before running anything — it holds
`baseUrl` and the auth token/ids that get passed between requests.

**CLI**: `npx @usebruno/cli run --env Local -r` from this directory runs
the entire collection top-to-bottom (needs `backend/` running first —
see its README/`implementation_1.md`).

## Structure

Folders run in this order, each depending on state set by the ones
before it (`Auth/Register` sets `token`, `Conversations/Create Conversation`
sets `conversationId`, etc. — see each request's `script:post-response`):

1. **Health** — plain liveness check, no auth
2. **Auth** — register (unique email every run, see its pre-request
   script) → login → session → logout, plus a `ZZ Error Cases` subfolder
   (wrong password, duplicate email) that intentionally runs *after* the
   main flow so it has a real registered user to test against — folder
   names are prefixed `ZZ` because Bruno's CLI runner (`-r`) sorts
   alphabetically, not by the `seq` field, when walking subfolders
2. **Conversations** — CRUD, plus a `ZZ Error Cases` subfolder (404 on a
   nonexistent id, 401 unauthenticated)
3. **Chat** — post a message in a template-leaf room and in General
4. **Custom Sections** — add a leaf, add a group, nest a child under
   that group (proving arbitrary-depth nesting), rename, delete
5. **Review** — recompute flagged items
6. **Documents** — generate markdown and PDF format requests
7. **Cleanup** — deletes the conversation created in step 2, last on
   purpose so everything above still has it to work with

Every request has `tests { ... }` assertions — running the whole
collection is a real (if shallow — status codes and response shapes, not
deep business-logic edge cases; see `backend/tests/` for that level) smoke
test of the live API, currently 24/24 requests, 39/39 assertions green.
