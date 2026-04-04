import asyncio
import logging
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

logger = logging.getLogger("uvicorn.error")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
SADTALKER_DIR = BASE_DIR / "models" / "SadTalker"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Talking Avatar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    tb = traceback.format_exc()
    logger.error("GLOBAL EXCEPTION HANDLER: %s\n%s", exc, tb)
    return JSONResponse(status_code=500, content={"detail": tb or str(exc)})

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

VOICE_OPTIONS = [
    "th-TH-PremwadeeNeural",
    "th-TH-NiwatNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-GB-SoniaNeural",
]


def cleanup_old_files(max_age_seconds: int = 3600) -> None:
    """Delete files older than max_age_seconds from uploads/ and outputs/."""
    now = time.time()
    for directory in (UPLOADS_DIR, OUTPUTS_DIR):
        for filepath in directory.iterdir():
            if filepath.is_file():
                age = now - filepath.stat().st_mtime
                if age > max_age_seconds:
                    filepath.unlink(missing_ok=True)


def _get_env_with_ffmpeg() -> dict:
    """Return environment with imageio-ffmpeg binary directory on PATH."""
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = str(Path(ffmpeg_exe).parent)
    env = os.environ.copy()
    env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")
    env["FFMPEG_BINARY"] = ffmpeg_exe
    return env


async def run_subprocess(cmd: list[str], cwd: str | None = None, extra_env: dict | None = None) -> tuple[int, str, str]:
    """Run a subprocess asynchronously and return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    def _run():
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
        return result.returncode, result.stdout.decode(), result.stderr.decode()

    return await asyncio.to_thread(_run)


@app.get("/")
async def health_check():
    return {"status": "ok", "message": "AI Talking Avatar API is running"}


@app.post("/generate-video")
async def generate_video(
    image_file: UploadFile = File(...),
    text_prompt: str = Form(...),
    voice: str = Form("th-TH-PremwadeeNeural"),
):
    # Cleanup old files on each request
    cleanup_old_files()

    # --- Validate voice ---
    if voice not in VOICE_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid voice. Choose from: {VOICE_OPTIONS}")

    # --- Validate file type ---
    ext = Path(image_file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}",
        )

    # --- Validate text ---
    text_prompt = text_prompt.strip()
    if not text_prompt:
        raise HTTPException(status_code=400, detail="text_prompt cannot be empty")
    if len(text_prompt) > 500:
        raise HTTPException(status_code=400, detail="text_prompt must be 500 characters or less")

    # --- Read & validate file size ---
    content = await image_file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10 MB.")

    job_id = str(uuid.uuid4())

    # Save uploaded image
    image_path = UPLOADS_DIR / f"{job_id}{ext}"
    image_path.write_bytes(content)

    # Paths for intermediate and output files
    audio_path = UPLOADS_DIR / f"{job_id}.wav"
    output_mp4 = OUTPUTS_DIR / f"{job_id}.mp4"

    try:
        logger.info("Starting TTS step for job %s", job_id)
        # --- Step 1: TTS with edge-tts ---
        tts_cmd = [
            "edge-tts",
            "--voice", voice,
            "--text", text_prompt,
            "--write-media", str(audio_path),
        ]
        retcode, stdout, stderr = await run_subprocess(tts_cmd)
        logger.info("TTS retcode=%s stdout=%r stderr=%r", retcode, stdout[:200], stderr[:200])
        if retcode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"TTS generation failed: {stderr.strip() or stdout.strip()}",
            )

        # --- Step 2: Lip-sync with SadTalker ---
        if not SADTALKER_DIR.exists():
            raise HTTPException(
                status_code=503,
                detail=(
                    "SadTalker model is not installed. "
                    "Please follow SETUP.md to clone and set up SadTalker."
                ),
            )

        # SadTalker outputs to result_dir/<timestamp>.mp4 — record files before
        existing_mp4s = set(OUTPUTS_DIR.glob("*.mp4"))

        sadtalker_cmd = [
            "python",
            str(SADTALKER_DIR / "inference.py"),
            "--driven_audio", str(audio_path),
            "--source_image", str(image_path),
            "--result_dir", str(OUTPUTS_DIR),
            "--still",
            "--preprocess", "crop",
            "--batch_size", "1",
        ]
        logger.error("DEBUG sadtalker_cmd: %s", sadtalker_cmd)
        retcode, stdout, stderr = await run_subprocess(
            sadtalker_cmd, cwd=str(SADTALKER_DIR), extra_env=_get_env_with_ffmpeg()
        )
        if retcode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Lip-sync generation failed: {stderr.strip() or stdout.strip()}",
            )

        # Find the newly created mp4 (SadTalker names it by timestamp)
        new_mp4s = [f for f in OUTPUTS_DIR.glob("*.mp4") if f not in existing_mp4s]
        if not new_mp4s:
            raise HTTPException(
                status_code=500,
                detail="Lip-sync succeeded but output MP4 was not found.",
            )
        sadtalker_output = max(new_mp4s, key=lambda f: f.stat().st_mtime)
        # Rename to job_id for consistent URL
        output_mp4 = OUTPUTS_DIR / f"{job_id}.mp4"
        sadtalker_output.rename(output_mp4)

        return JSONResponse(
            content={
                "status": "success",
                "video_url": f"/outputs/{output_mp4.name}",
                "job_id": job_id,
            }
        )

    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        logger.error("Unhandled exception in generate_video: %s", tb)
        raise HTTPException(status_code=500, detail=tb) from exc

    finally:
        # Clean up intermediate audio file (keep image until cleanup_old_files)
        audio_path.unlink(missing_ok=True)
