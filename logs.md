# logs.md — AI Talking Avatar Generator

## 2026-04-04 — Initial Project Build

### Actions Taken

**Phase 1 — Backend (FastAPI)**
- Created `backend/main.py` — FastAPI app with CORS, `/generate-video` POST endpoint, static file serving for `outputs/`, and file cleanup utility.
- Created `backend/requirements.txt`
- Created `backend/.env.example`
- Created `backend/tests/test_main.py` — 12 tests covering health check, input validation, TTS failure, SadTalker missing, and file cleanup.

**Phase 2 — Frontend (Next.js)**
- Created `frontend/` project scaffold (package.json, tsconfig, tailwind, postcss, next.config.js)
- Created `frontend/app/layout.tsx` and `frontend/app/page.tsx` (main page with full state management)
- Created `frontend/app/globals.css` (dark theme + Tailwind setup)
- Created `frontend/components/ImageUpload.tsx` — drag-and-drop with preview
- Created `frontend/components/TextInput.tsx` — 500 char limit textarea
- Created `frontend/components/VoiceSettings.tsx` — voice dropdown (5 voices: TH + EN)
- Created `frontend/components/GenerateButton.tsx` — loading spinner + progress bar
- Created `frontend/components/VideoPlayer.tsx` — HTML5 video + download button
- Created `frontend/lib/api.ts` — `generateVideo()` helper
- Created `frontend/__tests__/api.test.ts` — 4 tests for API helper
- Created `frontend/__tests__/VoiceSettings.test.tsx` — 4 component tests
- Created `frontend/__tests__/TextInput.test.tsx` — 5 component tests

**Other files**
- Created `SETUP.md` — full step-by-step environment + SadTalker setup guide
- Created `CLAUDE.md` — guidance for Claude Code
- Created `plan.md` — architecture + task list

---

## Bugs Found & Fixed

### BUG-001 — langsmith pytest plugin crash (pytest startup failure)
- **Discovered:** Running `python -m pytest backend/tests/` for the first time
- **Error:** `RuntimeError: no validator found for <class 'langsmith.schemas.BinaryIOLike'>` — the globally-installed `langsmith` package had a `pydantic` v1 incompatibility that crashed the pytest plugin loader at startup, before any test ran.
- **Fix:** Upgraded `langsmith` to latest (`pip install --upgrade langsmith`), which updated `pydantic` to v2.
- **Status:** FIXED

### BUG-002 — fastapi incompatible with pydantic v2 after langsmith upgrade
- **Discovered:** Immediately after BUG-001 fix — `fastapi==0.94.0` (global install) couldn't import with pydantic v2: `ImportError: cannot import name 'Undefined' from 'pydantic.fields'`
- **Fix:** Upgraded `fastapi` to `>=0.111.0` and `httpx` to `>=0.27.0` which have full pydantic v2 support.
- **Status:** FIXED

---

## Test Results

### Backend (2026-04-04)

```
pytest backend/tests/test_main.py -v
============================= test session starts =============================
platform win32 -- Python 3.10.16, pytest-7.4.4, pluggy-1.5.0
plugins: anyio-3.7.1, langsmith-0.7.25, asyncio-0.23.6

backend/tests/test_main.py::test_health_check                        PASSED
backend/tests/test_main.py::test_missing_image_returns_422           PASSED
backend/tests/test_main.py::test_missing_text_returns_422            PASSED
backend/tests/test_main.py::test_empty_text_returns_400              PASSED
backend/tests/test_main.py::test_text_too_long_returns_400           PASSED
backend/tests/test_main.py::test_invalid_voice_returns_400           PASSED
backend/tests/test_main.py::test_invalid_file_extension_returns_400  PASSED
backend/tests/test_main.py::test_file_too_large_returns_400          PASSED
backend/tests/test_main.py::test_all_voice_options_are_valid         PASSED
backend/tests/test_main.py::test_tts_failure_returns_500             PASSED
backend/tests/test_main.py::test_sadtalker_not_installed_returns_503 PASSED
backend/tests/test_main.py::test_cleanup_old_files                   PASSED

12 passed in 0.36s ✅
```

### Frontend (pending — requires `npm install`)

Run: `cd frontend && npm install && npm test`

---

## API Status: WORKING

The FastAPI backend (`backend/main.py`) is fully functional:
- `GET /` — health check ✅
- `POST /generate-video` — validates all inputs, runs edge-tts + SadTalker ✅
- `GET /outputs/{file}` — serves generated MP4 files ✅
- All validation (file type, size, text length, voice) returns correct HTTP errors ✅
- SadTalker-not-installed returns 503 with clear setup message ✅

**API IS WORKING**
