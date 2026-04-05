import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

load_dotenv()

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
    allow_origin_regex=r"http://localhost:\d+",
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

# Emotion → (rate, pitch) prosody modifiers for edge-tts
EMOTION_PROSODY: dict[str, tuple[str, str]] = {
    "happy":    ("+15%", "+3Hz"),
    "cheerful": ("+15%", "+3Hz"),
    "sad":      ("-15%", "-3Hz"),
    "angry":    ("+10%", "+6Hz"),
    "excited":  ("+25%", "+8Hz"),
    "calm":     ("-10%", "-2Hz"),
    "gentle":   ("-8%",  "-2Hz"),
    "fearful":  ("+8%",  "+5Hz"),
    "serious":  ("-5%",  "+0Hz"),
    "whisper":  ("-20%", "-5Hz"),
    "shouting": ("+20%", "+10Hz"),
    "normal":   ("+0%",  "+0Hz"),
}


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


async def analyze_text_emotions(text: str) -> list[dict] | None:
    """
    Call local Ollama to split text into sentences and assign an emotion to each.

    Uses OLLAMA_URL (default: http://localhost:11434) and
    OLLAMA_MODEL (default: glm-4.7-flash:latest).

    glm-4.7-flash is a thinking model — it streams reasoning into the
    `reasoning` field and the final answer into `content`. We check
    `content` first, then fall back to extracting JSON from `reasoning`.

    Returns list of {"text": str, "emotion": str} or None on failure
    (caller falls back to plain TTS).
    """
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "glm-4.7-flash:latest")

    prompt = (
        "Analyze the following text for text-to-speech emotion tagging.\n"
        "Split it into natural sentences or phrases. For each part, assign the most fitting emotion.\n\n"
        "Return ONLY a valid JSON array — no markdown, no code fences, no explanation.\n"
        "Each element must have exactly two keys:\n"
        '  "text": the original sentence/phrase\n'
        '  "emotion": one of: happy, sad, angry, excited, calm, gentle, fearful, serious, whisper, normal\n\n'
        f"Text:\n{text}"
    )

    try:
        # glm-4.7-flash is a thinking model — it runs a reasoning chain before
        # producing output. Thai/non-Latin text increases reasoning time.
        # 300 s is conservative but safe for ≤500-char inputs.
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{ollama_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a concise TTS emotion tagger. "
                                "Always respond with ONLY a valid JSON array. "
                                "No explanation, no markdown fences."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000,
                    "stream": False,
                },
            )

        if resp.status_code != 200:
            logger.warning("Ollama returned %s: %s", resp.status_code, resp.text[:300])
            return None

        msg = resp.json()["choices"][0]["message"]
        # thinking model: final answer in `content`, chain-of-thought in `reasoning`
        content = msg.get("content", "").strip()
        reasoning = msg.get("reasoning", "").strip()
        logger.info("Ollama emotion analysis content=%r reasoning_len=%d", content[:200], len(reasoning))

        # Search content first, then reasoning as fallback.
        # Use greedy .*  (not .*?) so the full array is captured, not just up to
        # the first closing bracket inside a nested object.
        json_match = re.search(r"\[.*\]", content, re.DOTALL)
        if not json_match:
            json_match = re.search(r"\[.*\]", reasoning, re.DOTALL)
        if not json_match:
            logger.warning("Could not find JSON array in Ollama response")
            return None

        segments = json.loads(json_match.group())

        result = []
        for seg in segments:
            text_part = seg.get("text", "").strip()
            emotion = seg.get("emotion", "normal").lower().strip()
            if text_part:
                result.append({"text": text_part, "emotion": emotion})

        return result if result else None

    except Exception as exc:
        logger.warning("Emotion analysis failed (%s): %s", type(exc).__name__, exc)
        return None


async def generate_tts_audio(
    text: str,
    voice: str,
    audio_path: Path,
    rate: str = "+0%",
    pitch: str = "+0Hz",
) -> None:
    """Generate TTS audio using the edge_tts Python API (avoids subprocess arg issues)."""
    import edge_tts
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(str(audio_path))


async def generate_emotional_audio(
    segments: list[dict],
    voice: str,
    output_path: Path,
    job_id: str,
) -> None:
    """
    Generate per-segment audio with emotion prosody, then concatenate into output_path.
    Segment format: {"text": str, "emotion": str}
    """
    import imageio_ffmpeg as _iio_ffmpeg
    ffmpeg_exe = _iio_ffmpeg.get_ffmpeg_exe()

    segment_paths: list[Path] = []
    try:
        for i, seg in enumerate(segments):
            emotion = seg.get("emotion", "normal")
            rate, pitch = EMOTION_PROSODY.get(emotion, ("+0%", "+0Hz"))
            seg_path = UPLOADS_DIR / f"{job_id}_seg{i}.wav"
            logger.info(
                "TTS segment %d/%d emotion=%s rate=%s pitch=%s text=%r",
                i + 1, len(segments), emotion, rate, pitch, seg["text"][:60],
            )
            await generate_tts_audio(seg["text"], voice, seg_path, rate=rate, pitch=pitch)
            segment_paths.append(seg_path)

        if len(segment_paths) == 1:
            # No concat needed — just rename
            segment_paths[0].rename(output_path)
            segment_paths.clear()
            return

        # Write ffmpeg concat list
        concat_list_path = UPLOADS_DIR / f"{job_id}_concat.txt"
        concat_list_path.write_text(
            "\n".join(f"file '{p}'" for p in segment_paths),
            encoding="utf-8",
        )

        concat_cmd = [
            ffmpeg_exe,
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_path),
            "-c", "copy",
            str(output_path),
            "-y",
        ]
        retcode, _, stderr = await run_subprocess(concat_cmd)
        concat_list_path.unlink(missing_ok=True)
        if retcode != 0:
            raise RuntimeError(f"ffmpeg concat failed: {stderr.strip()}")

    finally:
        for p in segment_paths:
            p.unlink(missing_ok=True)


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
        # --- Step 1: Emotion analysis via MiniMax ---
        logger.info("Analyzing text emotions for job %s", job_id)
        segments = await analyze_text_emotions(text_prompt)

        # --- Step 2: TTS (emotion-aware or plain fallback) ---
        if segments:
            logger.info("Using emotion-aware TTS (%d segments)", len(segments))
            await generate_emotional_audio(segments, voice, audio_path, job_id)
        else:
            logger.info("Emotion analysis unavailable — using plain TTS for job %s", job_id)
            import edge_tts
            communicate = edge_tts.Communicate(text=text_prompt, voice=voice)
            await communicate.save(str(audio_path))

        # --- Step 3: Lip-sync with SadTalker ---
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
            "--preprocess", "full",
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

        # Re-encode to h264 for browser compatibility
        output_mp4 = OUTPUTS_DIR / f"{job_id}.mp4"
        import imageio_ffmpeg as _iio_ffmpeg
        ffmpeg_exe = _iio_ffmpeg.get_ffmpeg_exe()
        reenc_cmd = [
            ffmpeg_exe,
            "-i", str(sadtalker_output),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(output_mp4),
            "-y",
        ]
        retcode_enc, _, stderr_enc = await run_subprocess(reenc_cmd)
        sadtalker_output.unlink(missing_ok=True)
        if retcode_enc != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Video re-encoding failed: {stderr_enc.strip()}",
            )

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
