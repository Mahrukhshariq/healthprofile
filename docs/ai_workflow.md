# AI Workflow

How AI was used to build HealthProfile (Week 1), how the prompts were refined, how
changes were kept small, and how the output was verified.

Items marked **[FILL IN]** need your own detail before you commit. Delete this line when done.

## Tools used
- **Claude (claude.ai, inside a Project)**: planning, code generation, debugging. The Project held the
  assignment PDFs, the orientation deck, the Vibe Coding deck and the mentor's clarifications, so the
  requirements were always in context.
- **VS Code**: editing, integrated terminal, SQLite Viewer for checking stored data.
- **PowerShell + pytest**: verification of everything the AI produced.
- **[FILL IN]**: any other AI tool you used (Copilot, Cursor, etc.), or delete this line.

Not used: MCP servers, multiple agents, a separate prompt-refiner tool. A single assistant was used,
one step at a time, and every file was reviewed before it was kept.

---

## Iteration 1: broad prompt

**Prompt (real, first message):**
> read all context and we need to start working on week 1 assignment. we joined late but we need to do
> it as soon as possible. Tell me exactly what to do and how to do it

**Output:** a complete 11-step plan for the whole assignment: architecture, models, both auth flows,
tests, EXPLAIN evidence, docs, frontend and a time split.

**What was good:** it picked the right architecture early (JWT in HttpOnly cookies for users, Django
sessions + CSRF for admins) and mapped every requirement in the PDF to a step.

**Problems:**
- Far too wide to execute as one unit. A mistake in step 2 would silently break steps 3 to 8.
- No file-level boundaries, so there was no way to say "this prompt may only touch these files".
- Nothing said what "done" looks like for each step, so failures were found late.

## Iteration 2: scoped prompts with acceptance criteria

After iteration 1, work was driven one step at a time with a fixed structure (the session template):

```
ROLE:         Senior Django engineer in this repository
GOAL:         Step 4 only: user signup + JWT login using HttpOnly cookies
CONTEXT:      Django 6 + DRF + SimpleJWT, custom email User model already migrated
IN SCOPE:     backend/accounts/{serializers,authentication,views,urls}.py, one line in config/urls.py
OUT OF SCOPE: profiles app, admin session flow, models, migrations
ACCEPTANCE:   - staff users cannot log in via the user endpoint
              - JWT claims contain no secrets or password
              - wrong password and unknown email return the same 401 message
              - cookies are HttpOnly, SameSite=Lax
PROCESS:      inspect -> plan -> implement -> verify with status codes
OUTPUT:       full file contents, exact test commands, expected result per command
```

**Differences observed vs iteration 1:**

| | Iteration 1 (broad) | Iteration 2 (scoped) |
|---|---|---|
| Size of change | whole project | 4 to 5 named files |
| Failure isolation | unclear which step broke | immediate: one step, one commit |
| Security rules | mentioned in prose | turned into checks (staff rejected twice, same error for all login failures) |
| Verification | "test it" | a table of command -> expected status code |

**[FILL IN]** Optional but strong for the Loom: run the truly vague prompt `build login for my health app`
in your tool, paste the output summary here, and note what it got wrong (typically one auth method for
everyone, tokens in localStorage, no role separation).

---

## Manual security review (done on AI output before keeping it)
- Staff accounts are rejected in **two** places: the user login view and `CookieJWTAuthentication`.
- Same error message for every login failure, so emails cannot be enumerated.
- Passwords are hashed (`create_user`), never returned in responses; a test checks the stored value differs.
- `status` is read-only for users, so they cannot reactivate a profile an admin deactivated.
- No profile id in user routes, so cross-user access is impossible by design (and tested).
- DRF defaults are deny-by-default: no default authenticators, default permission `IsAuthenticated`.
  Each view declares its own auth explicitly.
- Cookie flags: HttpOnly, SameSite=Lax, `Secure` when `DEBUG=False`. Refresh cookie is limited to `/api/auth/`.
- Secrets live in `.env` (git-ignored); `.env.example` has placeholders only. `git status` was checked
  before every commit.

## Context management
- The Project kept the assignment documents available, so they were never re-pasted.
- One step per message; each step ended with a short state summary (done, files changed, next).
- When something failed, only the relevant lines were shared (the last lines of a traceback, the one
  failing test), not whole files or logs.
- Long sessions were handed off with a compact summary instead of replaying the conversation.
- Test results were requested as a table of expected vs actual status codes, so output stayed small.

## Blast radius control
- Every prompt named the files it could touch and the files it must not.
- One commit per feature. When commits were delayed, changes were split by path
  (`git add backend/accounts/...` for auth, `backend/profiles/...` for profile) so history still reads cleanly.
- `git status` and `git diff` were read before each commit, mainly to confirm that `.env` and
  `db.sqlite3` were not staged.
- Higher-risk areas (authentication, migrations) were treated as high blast radius: custom user model was
  created and migrated before anything depended on it, and each auth change was followed by tests.

---

## Bugs and unexpected AI output

### 1. Settings edits not applied, migrations ran against the wrong user model
- **Symptom:** `No installed app with label 'accounts'`, then `migrate` ran with only the default Django apps.
- **Isolation:** `python manage.py check` passed, but `INSTALLED_APPS` and `AUTH_USER_MODEL` were not in the
  saved `settings.py`. The generated instructions had several scattered edits to one file, and some were missed.
- **Fix:** applied the missing settings, deleted the throwaway `db.sqlite3`, re-ran `makemigrations accounts`
  and `migrate`.
- **Regression check:** `get_user_model()` printed `accounts.models.User`; `check` clean; later tests rely on it.
- **Lesson:** a custom user model must exist before the first `migrate`. For multi-edit instructions,
  confirm each edit landed before running commands.

### 2. Missing file caused a startup crash
- **Symptom:** `ModuleNotFoundError: No module named 'profiles.urls'` from `config/urls.py`.
- **Isolation:** the traceback named the exact import; `backend/profiles/urls.py` had not been created.
- **Fix:** created the file. `check` passed and `/api/profiles/me` returned 200.

### 3. AI-generated test was wrong, application was right
- **Symptom:** `test_admin_list_and_search` failed with `assert 2 == 1`.
- **Isolation:** DRF `SearchFilter` splits `User A` into two terms and requires each to match some field;
  `A` matched `b@example.com`. The endpoint behaved correctly, so the test's expectation was the bug.
  The test was corrected, not the code and not the assertion's intent.
- **Fix:** quoted phrase search (`{"search": '"User A"'}`).
- **Regression:** the corrected test itself.
- **Lesson:** a failing AI-written test is not automatically an app bug; check the library's behavior first.

### 4. Index without a use case
- **Finding (manual review of generated models):** `idx_profile_full_name` could not serve the admin search,
  which uses `icontains` (`LIKE '%text%'`). The assignment says no index without a use case.
- **Fix:** removed the index in a new migration. Documented that a `pg_trgm` index would be the PostgreSQL answer.
- **Evidence kept:** the composite `(status, -created_at)` index is confirmed in `docs/explain.md`
  (`SEARCH ... USING INDEX idx_profile_status_created`).

### 5. Environment slips (not AI errors, but worth recording)
- New terminals did not have the virtual environment active (`No module named 'django'`) and `manage.py`
  was run from the wrong folder. Both were fixed by activating `.venv` and running from `backend/`.

---

## Verification
| Check | Result |
|---|---|
| Manual PowerShell script (user, admin, isolation, CSRF, logout) | 18 of 18 PASS |
| `python -m pytest -v` | 26 of 27 on first run; 27 of 27 after fixing bug 3 **[confirm after re-running]** |
| `python manage.py check` | no issues |
| EXPLAIN on the admin list query | composite index used, no temporary sort |
| Cookie flags (`Set-Cookie` header) | HttpOnly, SameSite=Lax, Max-Age 900 / 604800 |
| Frontend walkthrough (register, login, edit profile, admin search/deactivate, `/admin` as normal user) | **[FILL IN after you run it]** |

## What I would do differently
- Start with the custom user model and a settings checklist before any other generated code.
- Ask for tests alongside each endpoint instead of after all endpoints.
- Run the vague-prompt comparison earlier, while the first outputs are still fresh.