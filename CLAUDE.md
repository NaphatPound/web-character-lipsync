# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Talking Avatar Generator — users upload a character image + type text → backend converts text to speech (edge-tts) → SadTalker lip-syncs the image to the audio → returns an MP4 video. See `plan.md` for full architecture and task list.

---

## Project Structure

```
web-character-lipsync/
├── frontend/        # Next.js 14 App Router (TypeScript + Tailwind)
└── backend/         # Python FastAPI server
    └── models/
        └── SadTalker/   # Cloned separately — NOT in this repo
```

---

## Development Commands

### Frontend (Next.js)

```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Dev server on http://localhost:3000
npm run build        # Production build
npm run lint         # ESLint check
```

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt       # Install Python deps
uvicorn main:app --reload --port 8000 # Dev server on http://localhost:8000
```

### Backend environment requires SadTalker to be set up first:
```bash
cd backend/models
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker && pip install -r requirements.txt
bash scripts/download_models.sh
```

See `SETUP.md` for the complete step-by-step environment setup guide.

---

## Architecture

### Request Flow

1. Frontend sends `multipart/form-data` (image + text + voice) to `POST /generate-video` on FastAPI (port 8000).
2. FastAPI saves the image to `backend/uploads/`, runs `edge-tts` via `subprocess` to produce `audio.wav`.
3. FastAPI runs `python SadTalker/inference.py` via `subprocess`, passing the image and audio.
4. The resulting `output.mp4` is saved to `backend/outputs/` and served as a static file.
5. FastAPI returns `{ "video_url": "/outputs/<filename>.mp4" }`.
6. Frontend plays the video and offers a download button.

### Backend (`backend/main.py`)

- Single FastAPI app with CORS enabled for `http://localhost:3000`.
- `POST /generate-video` — main endpoint; runs TTS and lip-sync subprocesses sequentially.
- `GET /outputs/{filename}` — static file mount for generated videos.
- Background cleanup task removes files from `uploads/` and `outputs/` older than 1 hour.

### Frontend (`frontend/`)

- `app/page.tsx` — root page; holds all state (`imageFile`, `textPrompt`, `voice`, `isLoading`, `videoUrl`).
- `components/ImageUpload.tsx` — drag-and-drop with image preview.
- `components/TextInput.tsx` — textarea with 500-char limit.
- `components/VoiceSettings.tsx` — dropdown for edge-tts voice selection.
- `components/GenerateButton.tsx` — triggers API call, shows loading/progress state.
- `components/VideoPlayer.tsx` — HTML5 video player + download button.
- `lib/api.ts` — `generateVideo(image, text, voice)` sends FormData to backend, returns video URL.

---

## Key Constraints

- **SadTalker is not bundled** — it must be cloned and set up manually per `SETUP.md`. The FastAPI subprocess path assumes `backend/models/SadTalker/inference.py`.
- **TTS engine:** `edge-tts` CLI tool. Voice names follow the pattern `th-TH-PremwadeeNeural`. Thai and English voices are supported.
- **Subprocess calls are synchronous** — SadTalker inference can take 30–120 seconds. The frontend must keep the loading state active during this time.
- **No ComfyUI** — all AI processing runs directly via Python subprocess, not through any workflow UI.
- **File handling:** uploaded images use `uuid`-based filenames to avoid collisions.
