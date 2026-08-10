# BRD-Agent API — Bruno collection

A [Bruno](https://www.usebruno.com/) collection covering every endpoint in
`../brainstorming/api_contract.md`, checked in as plain-text `.bru` files
so it stays diffable and versioned alongside the API itself — this is both
the test suite and the living, runnable documentation for the API surface.

## Using it

**First time**: copy `environments/Local.example.bru` to
`environments/Local.bru` (gitignored — same reasoning as `.env`/
`.env.example` elsewhere in this repo: `Local.bru` accumulates real,
if throwaway/dev-only, JWTs written by test runs as you use the
collection, so it never gets committed).

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
   script) → login → session → **a separate scratch registration just
   for the logout test** → logout → confirm the now-logged-out token is
   actually rejected. That scratch registration exists on purpose:
   `/auth/logout` now does real server-side revocation (see
   `../erd.md`'s `REVOKED_TOKEN`, added after discovering logout used to
   be a no-op), so logging out with the shared `{{token}}` — the one
   every folder after this one keeps authenticating with — would 401 the
   rest of the collection. `Register For Logout Test.bru` sets a
   throwaway `{{logoutToken}}` instead, and only that gets revoked.
   Plus a `ZZ Error Cases` subfolder (wrong password, duplicate email,
   logout without a token) — see the note on subfolder ordering below.
3. **Conversations** — CRUD, plus a `ZZ Error Cases` subfolder (404 on a
   nonexistent id, 401 unauthenticated)
4. **Chat** — post a message in a template-leaf room and in General
5. **Custom Sections** — add a leaf, add a group, nest a child under
   that group (proving arbitrary-depth nesting), rename, delete
6. **Review** — recompute flagged items
7. **Documents** — generate markdown and PDF format requests
8. **Sharing** — registers its own editor/viewer users, creates its own
   conversation (`sharingConversationId`, separate from step 2's
   `conversationId` so it doesn't disturb the rest of the collection),
   shares it as editor and viewer, proves an editor can chat/add custom
   sections while a viewer can't (403) but both can export, updates and
   revokes a role, then the error cases (removed collaborator gets 404,
   non-owner can't manage collaborators, self-share/duplicate-share/
   unknown-email all reject), ending with its own self-contained
   conversation cleanup.
9. **Cleanup** — deletes the conversation created in step 3, last on
   purpose so everything above still has it to work with
10. **Manual** — not part of the tested flow above, see "Manual testing"
    below

**On the `ZZ Error Cases` subfolders (Auth, Conversations)**: named `ZZ`
on the assumption Bruno's CLI runner (`-r`) sorts alphabetically rather
than by `seq` when walking a folder's contents, so `ZZ` would sort last.
While building the Sharing folder we confirmed that's only half true —
subfolders actually run *before* a parent folder's own files, not after,
regardless of name. Auth's and Conversations' error cases only pass
today because they coincidentally reuse leftover state from a *previous*
run (a stale-but-still-valid registered user/token sitting in
`Local.bru`) rather than genuinely depending on this run's own `Register`
step — a fresh clone's very first run would fail them. Not fixed here
(pre-existing, out of scope of whatever change you're reading this
paragraph for) — Sharing's own error cases deliberately avoid this by
staying flat, no subfolder, plain seq-ordered files instead.

Every request has `tests { ... }` assertions — running the whole
collection is a real (if shallow — status codes and response shapes, not
deep business-logic edge cases; see `backend/tests/` for that level) smoke
test of the live API, currently 45/45 requests, 72/72 assertions green.

## Manual testing

To click through requests by hand in the Bruno GUI rather than running
the whole collection — e.g. "register, then poke around a few endpoints
myself" — you don't need a separate variable or setup. `{{token}}` is
already exactly that: open `Auth > Register` (or `Login`) and run it
once — its `script:post-response` writes `{{token}}` into the active
environment — and every other request in the collection already reads
`{{token}}`, so anything else you click next just works. Unlike the
automated `-r` run, clicking requests by hand doesn't care about `seq`
order at all — click whatever you want, whenever.

The one thing that *doesn't* just work this way: `Auth/Logout` (the one
that's part of the tested flow above) deliberately logs out a separate
throwaway `{{logoutToken}}`, not `{{token}}` — see the "On the `ZZ Error
Cases` subfolders" note below for why (short version: revoking the
shared `{{token}}` mid-collection would 401 every request after it in
the same automated run). So clicking it won't kill the session you're
manually testing with. For that, use **`Manual/Logout My Current
Token`** — it's identical except its `auth:bearer` points at `{{token}}`
directly. It's kept in its own folder seq'd to run dead last (after
`Cleanup`) specifically so that even though it *does* still execute
during a full `-r` run (Bruno's `ignore` config, tried and confirmed
during this work, does **not** actually exclude a folder from the `-r`
CLI run — only `node_modules`/`.git`-style tooling dirs behave that
way), nothing later in that same run still needs `{{token}}` by the time
it's this folder's turn, so it's harmless there too.
