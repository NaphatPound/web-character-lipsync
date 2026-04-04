"""
Backend API Tests — AI Talking Avatar Generator
Run: pytest backend/tests/ -v
"""
import io
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, VOICE_OPTIONS

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "AI Talking Avatar" in data["message"]


# ---------------------------------------------------------------------------
# Input validation tests (no AI calls)
# ---------------------------------------------------------------------------

def _make_image_bytes(color: bytes = b"\xff\xff\xff") -> bytes:
    """Return a minimal valid JPEG header for testing."""
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + color * 100
        + b"\xff\xd9"
    )


def test_missing_image_returns_422():
    response = client.post(
        "/generate-video",
        data={"text_prompt": "Hello", "voice": "th-TH-PremwadeeNeural"},
    )
    assert response.status_code == 422


def test_missing_text_returns_422():
    img = io.BytesIO(_make_image_bytes())
    response = client.post(
        "/generate-video",
        files={"image_file": ("test.jpg", img, "image/jpeg")},
        data={"voice": "th-TH-PremwadeeNeural"},
    )
    assert response.status_code == 422


def test_empty_text_returns_400():
    img = io.BytesIO(_make_image_bytes())
    response = client.post(
        "/generate-video",
        files={"image_file": ("test.jpg", img, "image/jpeg")},
        data={"text_prompt": "   ", "voice": "th-TH-PremwadeeNeural"},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_text_too_long_returns_400():
    img = io.BytesIO(_make_image_bytes())
    long_text = "a" * 501
    response = client.post(
        "/generate-video",
        files={"image_file": ("test.jpg", img, "image/jpeg")},
        data={"text_prompt": long_text, "voice": "th-TH-PremwadeeNeural"},
    )
    assert response.status_code == 400
    assert "500" in response.json()["detail"]


def test_invalid_voice_returns_400():
    img = io.BytesIO(_make_image_bytes())
    response = client.post(
        "/generate-video",
        files={"image_file": ("test.jpg", img, "image/jpeg")},
        data={"text_prompt": "Hello", "voice": "xx-INVALID-Voice"},
    )
    assert response.status_code == 400
    assert "Invalid voice" in response.json()["detail"]


def test_invalid_file_extension_returns_400():
    gif_bytes = io.BytesIO(b"GIF89a" + b"\x00" * 100)
    response = client.post(
        "/generate-video",
        files={"image_file": ("test.gif", gif_bytes, "image/gif")},
        data={"text_prompt": "Hello", "voice": "th-TH-PremwadeeNeural"},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_file_too_large_returns_400():
    big_image = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * (11 * 1024 * 1024))
    response = client.post(
        "/generate-video",
        files={"image_file": ("big.jpg", big_image, "image/jpeg")},
        data={"text_prompt": "Hello", "voice": "th-TH-PremwadeeNeural"},
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_all_voice_options_are_valid():
    """Ensure every listed voice passes the voice validation gate."""
    expected = [
        "th-TH-PremwadeeNeural",
        "th-TH-NiwatNeural",
        "en-US-JennyNeural",
        "en-US-GuyNeural",
        "en-GB-SoniaNeural",
    ]
    assert set(expected).issubset(set(VOICE_OPTIONS))


# ---------------------------------------------------------------------------
# TTS subprocess mock tests
# ---------------------------------------------------------------------------

@patch("main.SADTALKER_DIR", Path("/nonexistent/SadTalker"))
@patch("main.run_subprocess", new_callable=AsyncMock)
def test_tts_failure_returns_500(mock_subprocess):
    """If edge-tts exits non-zero, endpoint should return 500."""
    mock_subprocess.return_value = (1, "", "edge-tts: command not found")
    img = io.BytesIO(_make_image_bytes())
    response = client.post(
        "/generate-video",
        files={"image_file": ("char.jpg", img, "image/jpeg")},
        data={"text_prompt": "สวัสดี", "voice": "th-TH-PremwadeeNeural"},
    )
    assert response.status_code == 500
    assert "TTS generation failed" in response.json()["detail"]


@patch("main.run_subprocess", new_callable=AsyncMock)
def test_sadtalker_not_installed_returns_503(mock_subprocess):
    """If SadTalker directory is missing, endpoint should return 503."""
    # TTS succeeds, but SadTalker dir doesn't exist
    mock_subprocess.return_value = (0, "", "")
    img = io.BytesIO(_make_image_bytes())
    with patch("main.SADTALKER_DIR", Path("/does/not/exist")):
        response = client.post(
            "/generate-video",
            files={"image_file": ("char.jpg", img, "image/jpeg")},
            data={"text_prompt": "Hello", "voice": "en-US-JennyNeural"},
        )
    assert response.status_code == 503
    assert "SadTalker" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Cleanup utility test
# ---------------------------------------------------------------------------

def test_cleanup_old_files(tmp_path):
    from main import cleanup_old_files
    import time

    old_file = tmp_path / "old.mp4"
    old_file.write_bytes(b"data")
    # Set mtime to 2 hours ago
    old_mtime = time.time() - 7200
    import os
    os.utime(old_file, (old_mtime, old_mtime))

    new_file = tmp_path / "new.mp4"
    new_file.write_bytes(b"data")

    with (
        patch("main.UPLOADS_DIR", tmp_path),
        patch("main.OUTPUTS_DIR", tmp_path),
    ):
        cleanup_old_files(max_age_seconds=3600)

    assert not old_file.exists(), "Old file should have been deleted"
    assert new_file.exists(), "New file should be kept"
