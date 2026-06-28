import os

# ── Device ────────────────────────────────────────────────
DEVICE       = "laptop"
BASE         = os.path.expanduser("~/.blackberry")

# ── Gemini ────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")   # set in .env
GEMINI_MODEL   = "gemini-1.5-flash"

# ── Audio ─────────────────────────────────────────────────
MIC_DEVICE        = 14      # pulse — handles sample rate conversion automatically
OUT_DEVICE        = 19         # default ALSA output (speakers)
SAMPLE_RATE = 16000   # back to 16000 — pulse supports this
SILENCE_THRESHOLD = 8000        # lower = more sensitive
SILENCE_SECONDS   = 1.8        # seconds of silence = end of command

# ── Whisper ───────────────────────────────────────────────
WHISPER_MODEL = "base"         # tiny/base/small — base is best for your RAM

# ── Memory ────────────────────────────────────────────────
MEMORY_TOP_K = 5
