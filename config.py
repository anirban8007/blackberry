import os
from typing import Optional

def _env_int(name: str, default: Optional[int] = None) -> Optional[int]:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default

# ── Device ────────────────────────────────────────────────
DEVICE       = "laptop"
BASE         = os.path.expanduser("~/.blackberry")

# ── Gemini ────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")   # set in .env
GEMINI_MODEL   = "gemini-1.5-flash"

# ── Audio ─────────────────────────────────────────────────
MIC_DEVICE        = _env_int("BLACKBERRY_MIC_DEVICE", None)
OUT_DEVICE        = _env_int("BLACKBERRY_OUT_DEVICE", None)
SAMPLE_RATE = _env_int("BLACKBERRY_SAMPLE_RATE", 16000)
SILENCE_THRESHOLD = _env_int("BLACKBERRY_SILENCE_THRESHOLD", 1200)
SILENCE_SECONDS   = 1.8        # seconds of silence = end of command
WAKE_MIN_VOLUME   = _env_int("BLACKBERRY_WAKE_MIN_VOLUME", 800)

# ── Whisper ───────────────────────────────────────────────
WHISPER_MODEL = "base"         # tiny/base/small — base is best for your RAM

# ── Memory ────────────────────────────────────────────────
MEMORY_TOP_K = 5
