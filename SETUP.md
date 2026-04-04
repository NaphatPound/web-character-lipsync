# Setup Guide — AI Talking Avatar Generator

## Prerequisites

- Python 3.10+ with conda or venv
- Node.js 18+
- GPU with CUDA support recommended (NVIDIA, ≥4 GB VRAM)
- Git

---

## 1. Clone This Repository

```bash
git clone <your-repo-url> web-character-lipsync
cd web-character-lipsync
```

---

## 2. Backend Setup

### 2a. Create Python environment

```bash
conda create -n avatar python=3.10 -y
conda activate avatar
```

### 2b. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2c. Install edge-tts

```bash
pip install edge-tts
# Verify it works:
edge-tts --text "Hello" --voice en-US-JennyNeural --write-media test.wav
```

---

## 3. SadTalker Setup

### 3a. Clone SadTalker into the models folder

```bash
cd backend/models
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
```

### 3b. Install SadTalker dependencies

```bash
# Inside backend/models/SadTalker/
pip install -r requirements.txt

# Install face alignment (required)
pip install "git+https://github.com/deepinsight/insightface.git@mp-feat#egg=insightface"
```

### 3c. Download model checkpoints

```bash
# Option A — automatic script (Linux/Mac/WSL)
bash scripts/download_models.sh

# Option B — manual download (Windows)
# Download from: https://github.com/OpenTalker/SadTalker#download-models
# Place files in: backend/models/SadTalker/checkpoints/
```

Required checkpoint files:
```
backend/models/SadTalker/checkpoints/
├── SadTalker_V0.0.2_256.safetensors
├── SadTalker_V0.0.2_512.safetensors
└── mapping_00109-model.pth.tar
```

### 3d. Verify SadTalker works (optional)

```bash
cd backend/models/SadTalker
python inference.py \
  --driven_audio examples/driven_audio/bus_chinese.wav \
  --source_image examples/source_image/full_body_2.png \
  --result_dir ./results \
  --still \
  --preprocess full
```

---

## 4. Frontend Setup

```bash
cd frontend
npm install
```

---

## 5. Running the Project

### Terminal 1 — Backend

```bash
conda activate avatar
cd backend
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API docs: http://localhost:8000/docs

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:3000

---

## 6. Running Tests

### Backend tests

```bash
conda activate avatar
cd backend
pytest tests/ -v
```

### Frontend tests

```bash
cd frontend
npm test
```

---

## 7. Troubleshooting

| Problem | Fix |
|---------|-----|
| `edge-tts: command not found` | Run `pip install edge-tts` in the avatar conda env |
| SadTalker inference fails | Ensure checkpoints are in `backend/models/SadTalker/checkpoints/` |
| CORS error in browser | Make sure FastAPI is running on port 8000 |
| Video not found after generation | Check `backend/outputs/` directory exists and has write permission |
| `module 'cv2' not found` | Run `pip install opencv-python-headless` in the avatar env |
| Out of VRAM | Add `--cpu` flag to the SadTalker command in `main.py` (slower) |

---

## Project Structure

```
web-character-lipsync/
├── CLAUDE.md            # Guidance for Claude Code
├── SETUP.md             # This file
├── plan.md              # Architecture & task plan
├── backend/
│   ├── main.py          # FastAPI application
│   ├── requirements.txt
│   ├── uploads/         # Temp uploaded images
│   ├── outputs/         # Generated MP4 videos
│   └── models/
│       └── SadTalker/   # Clone here
└── frontend/
    ├── app/             # Next.js App Router pages
    ├── components/      # React UI components
    └── lib/api.ts       # Backend API helper
```
