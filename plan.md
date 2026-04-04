# Plan: AI Talking Avatar Generator

## Project Overview
Web application ที่ให้ผู้ใช้อัปโหลดรูปตัวละคร + พิมพ์ข้อความ → ระบบแปลงข้อความเป็นเสียง → ตัวละครขยับปากตามเสียง → ได้วิดีโอ MP4

---

## Architecture

```
┌─────────────────────────────────┐
│  Frontend (Next.js + Tailwind)  │
│  Port: 3000                     │
└──────────┬──────────────────────┘
           │ HTTP / FormData
┌──────────▼──────────────────────┐
│  Backend (Python FastAPI)       │
│  Port: 8000                     │
│                                 │
│  1. Receive image + text        │
│  2. edge-tts → audio.wav        │
│  3. SadTalker CLI → output.mp4  │
│  4. Return video URL            │
└──────────┬──────────────────────┘
           │ subprocess
┌──────────▼──────────────────────┐
│  Local AI Models                │
│  - edge-tts (TTS)               │
│  - SadTalker (Lip-sync)         │
└─────────────────────────────────┘
```

---

## Folder Structure

```
web-character-lipsync/
├── plan.md
├── ideas.md
├── frontend/                    # Next.js App
│   ├── app/
│   │   ├── page.tsx             # Main UI page
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ImageUpload.tsx      # Drag-and-drop upload
│   │   ├── TextInput.tsx        # Dialogue textarea
│   │   ├── VoiceSettings.tsx    # Voice/language selector
│   │   ├── GenerateButton.tsx   # Trigger + loading state
│   │   └── VideoPlayer.tsx      # Result + download
│   ├── lib/
│   │   └── api.ts               # Axios/fetch helpers
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── backend/                     # FastAPI Server
│   ├── main.py                  # FastAPI app + endpoints
│   ├── requirements.txt
│   ├── .env.example
│   ├── uploads/                 # Temp uploaded images
│   ├── outputs/                 # Generated MP4 files
│   └── models/
│       └── SadTalker/           # Clone SadTalker repo here
│
└── SETUP.md                     # Step-by-step setup guide
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | Python 3.10+, FastAPI, Uvicorn |
| TTS | edge-tts (free, high-quality, multi-language) |
| Lip-sync | SadTalker (local model, supports 2D/anime images) |
| File handling | python-multipart, aiofiles |
| CORS | fastapi middleware |

---

## Phase 1 — Backend (FastAPI)

### Tasks
- [x] P1.1 Create `backend/main.py` with FastAPI skeleton + CORS
- [x] P1.2 Create `/generate-video` endpoint (POST)
  - Accept: `image_file` (UploadFile) + `text_prompt` (str) + `voice` (str)
  - Save uploaded image to `uploads/`
  - Call edge-tts subprocess → `audio.wav`
  - Call SadTalker subprocess → `output.mp4`
  - Return static URL to video
- [x] P1.3 Serve `outputs/` as static files
- [x] P1.4 Create `requirements.txt`
- [x] P1.5 Create `SETUP.md` (SadTalker clone + checkpoint download guide)

### Key Endpoint

```
POST /generate-video
Content-Type: multipart/form-data

Body:
  image_file: File
  text_prompt: string
  voice: string (default: "th-TH-PremwadeeNeural")

Response:
  { "video_url": "/outputs/result_uuid.mp4", "status": "success" }
```

---

## Phase 2 — Frontend (Next.js)

### Tasks
- [x] P2.1 Init Next.js project with TypeScript + Tailwind CSS
- [x] P2.2 Create main page layout (`page.tsx`)
- [x] P2.3 Build `ImageUpload` component (drag-and-drop, preview)
- [x] P2.4 Build `TextInput` component (textarea with character count)
- [x] P2.5 Build `VoiceSettings` component (voice dropdown + language)
- [x] P2.6 Build `GenerateButton` component (loading spinner + progress)
- [x] P2.7 Build `VideoPlayer` component (HTML5 video + download button)
- [x] P2.8 Create `lib/api.ts` for backend API calls
- [x] P2.9 Wire all components with React state (`useState`, `useRef`)

### Voice Options (edge-tts Thai + English)
- th-TH-PremwadeeNeural (หญิง ไทย)
- th-TH-NiwatNeural (ชาย ไทย)
- en-US-JennyNeural (Female EN)
- en-US-GuyNeural (Male EN)
- en-GB-SoniaNeural (Female EN-GB)

---

## Phase 3 — Integration & Polish

### Tasks
- [x] P3.1 Test end-to-end flow (upload → TTS → lip-sync → video)
- [x] P3.2 Add error handling (file size limit, unsupported format, timeout)
- [x] P3.3 Add progress indicator (polling or SSE)
- [x] P3.4 Add file cleanup (auto-delete old uploads/outputs)
- [x] P3.5 Responsive design check (mobile + desktop)

---

## SadTalker Setup (Summary)

```bash
# 1. Clone into backend/models/
cd backend/models
git clone https://github.com/OpenTalker/SadTalker.git

# 2. Create conda env
conda create -n sadtalker python=3.10
conda activate sadtalker

# 3. Install dependencies
cd SadTalker
pip install -r requirements.txt

# 4. Download checkpoints (run provided script)
bash scripts/download_models.sh
```

SadTalker CLI command used by FastAPI:
```bash
python SadTalker/inference.py \
  --driven_audio /path/to/audio.wav \
  --source_image /path/to/image.jpg \
  --result_dir /path/to/outputs \
  --still \
  --preprocess full
```

---

## UI Design Reference

```
┌─────────────────────────────────────────────────┐
│  🎭 AI Talking Avatar Generator                  │
├──────────────────────┬──────────────────────────┤
│  [Image Upload Area] │  [Text Input Area]       │
│  Drag & Drop         │  Type your dialogue...   │
│  or Click to Upload  │                          │
│  ┌──────────┐        │  Voice: [dropdown ▼]     │
│  │ preview  │        │  Language: [dropdown ▼]  │
│  └──────────┘        │                          │
├──────────────────────┴──────────────────────────┤
│          [ ▶ Generate Avatar Video ]            │
│          [████████░░░░░░] 60% Processing...     │
├─────────────────────────────────────────────────┤
│  Output:                                        │
│  ┌───────────────────────────────────────────┐  │
│  │           [Video Player]                  │  │
│  └───────────────────────────────────────────┘  │
│  [ ⬇ Download MP4 ]                            │
└─────────────────────────────────────────────────┘
```

---

## Implementation Order

1. **Phase 1** — Backend scaffold + endpoint logic
2. **Phase 2** — Frontend UI components
3. **Phase 3** — Integration, testing, polish
4. **SETUP.md** — Complete setup guide for SadTalker + environment
