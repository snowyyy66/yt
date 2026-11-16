# Vidósfera Visual and Spec Audit Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task. Steps use checkbox syntax.

**Goal:** Bring the parody interface closer to the familiar YouTube information hierarchy, repair the broken watch/comment controls, and verify every assignment requirement against the implementation.

**Architecture:** Keep FastAPI and the existing static HTML/CSS/JavaScript frontend. Add no external frontend dependency. Preserve the parody identity and make the watch dialog responsive and functional; use focused API tests for persisted interactions and a real-browser visual check for rendering.

**Tech Stack:** FastAPI, PostgreSQL/SQLAlchemy, vanilla HTML/CSS/JavaScript, pytest, Playwright CLI.

**Spec:** User-provided YouTube copy assignment in the conversation; product constraints in `AGENTS.md`; art direction in `DESIGN.md`.

## Global Constraints

- Keep the interface in Russian and do not reuse YouTube branding or media.
- Preserve keyboard access and mobile layout.
- Fix actual behavior surfaced by the audit when the backend supports it; document remaining hosting limits clearly.
- Do not claim a requirement is complete when the deployed configuration or implementation does not prove it.

## Tasks

### Task 1: Persistent like state

**Files:** Modify `app/main.py`; modify `tests/test_interactions.py`.

- [x] Add a regression test showing the like endpoint returns the persisted state and active count.
- [x] Run it and verify the response lacks the required state/count.
- [x] Return `liked` and active `count` from the endpoint using a database query.
- [x] Run interaction tests and commit.

### Task 2: Watch and comment interface

**Files:** Modify `app/static/index.html`, `app/static/styles.css`, and `app/static/app.js`; add `DESIGN.md`.

- [x] Capture the current local homepage and watch dialog at desktop and mobile widths.
- [x] Replace the browser-default comment submit control with a semantic composer and designed button; improve the channel/action hierarchy and responsive watch dialog.
- [x] Ensure likes use the server response and comments refresh from the API without losing the current video state.
- [x] Recheck keyboard, focus, and narrow-screen behavior in a browser; commit.

### Task 3: Assignment compliance audit

**Files:** Modify upload API/UI and regression tests to close the Vercel body-size gap; update `README.md`, architecture and Vercel docs; add a compliance checklist to `docs/`.

- [x] Trace each requested screen, role, private-media rule, object-storage path, worker, demo seed, test, Swagger path, and clean-Ubuntu command to code or documentation.
- [x] Replace the Vercel-limited multipart path in the UI with a signed direct-to-object-store upload; verify ownership, object size, and video signature before enabling playback.
- [x] Document R2 endpoint/CORS setup and report the remaining worker, quota, migration, and external-deploy limitations.
- [x] Run the full pytest suite and deployment/configuration checks supported by this repository.
- [x] Record verified coverage and any gaps that cannot be closed without external service credentials or platform support; commit.

## Review Focus

- Comment submission must use the same authenticated API path for mouse and keyboard.
- The interface must not show a successful fake like or comment when persistence fails.
- Private-video grants must still be checked before a signed object URL is issued.
- Vercel's request-body ceiling must not be described as supporting 2 GB uploads end to end.
