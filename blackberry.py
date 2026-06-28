"""
BLACKBERRY — Personal AI Assistant
Phase 1: Voice Loop (Wake Word → STT → Gemini → TTS)

Run: python3 blackberry.py
"""

import os, sys, time
from dotenv import load_dotenv

# Load .env from ~/.blackberry/.env
load_dotenv(os.path.expanduser("~/.blackberry/.env"))

import config
import stt
import llm
import tts
import memory
import actions

# Cache Whisper model — load once, reuse forever
_wake_whisper = None
def _get_wake_model():
    global _wake_whisper
    if _wake_whisper is None:
        from faster_whisper import WhisperModel
        print("[WAKE] Loading Whisper... (one-time, ~30s)")
        _wake_whisper = WhisperModel(config.WHISPER_MODEL,
                                     device="cpu", compute_type="int8")
        print("[WAKE] Whisper ready.")
    return _wake_whisper

# ── Wake word detection ────────────────────────────────────────────────────

def setup_wake_word():
    """
    Phase 1 uses a simple keyword spotter on Whisper output
    (openwakeword custom model training is Phase 2).
    We record 3s chunks and check if 'blackberry' was said.
    This is reliable and needs zero extra setup.
    """
    pass   # handled in main loop below


# ── Main loop ─────────────────────────────────────────────────────────────

def simple_wake_listen() -> bool:
    """
    Listen for 3 seconds. Return True if 'blackberry' was said.
    This is the Phase 1 wake word approach — robust, zero config.
    """
    import sounddevice as sd
    import numpy as np

    print("[WAKE] Listening for 'Blackberry'...")
    rate    = config.SAMPLE_RATE
    seconds = 3
    audio   = sd.rec(int(rate * seconds),
                     samplerate=rate,
                     channels=1,
                     dtype='int16',
                     device=config.MIC_DEVICE)
    sd.wait()
    audio = audio.flatten()

    # Only transcribe if audio has actual content (not silence)
    vol = int(np.abs(audio.astype(np.float32)).mean())
    print(f"[WAKE] Volume: {vol}")
    if vol < 8000:
        return False

    import scipy.io.wavfile as wav
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, 16000, audio)
        tmp = f.name

    try:
        model    = _get_wake_model()
        segments, _ = model.transcribe(tmp, language="en")
        text     = " ".join([s.text for s in segments]).lower()
        os.unlink(tmp)
        print(f"[WAKE] Heard: '{text}'")
        return "blackberry" in text
    except Exception as e:
        print(f"[WAKE] Error: {e}")
        os.unlink(tmp)
        return False


def handle_command():
    """Full pipeline: record command → Gemini → action → speak."""
    tts.play_beep()
    print("[BB] Activated! Listening for command...")

    # Record command
    audio = stt.record_command()
    text  = stt.transcribe(audio)

    if not text.strip():
        tts.speak("I didn't catch that. Try again.")
        return

    # Get memory context
    context = memory.get_context(text)

    # Ask Gemini
    result = llm.ask(text, context)

    # Save to memory
    memory.save("user", text)
    memory.save("blackberry", result.get("speech", ""))

    # Execute action if any
    actions.execute(
        result.get("action"),
        result.get("target"),
        result.get("payload")
    )

    # Speak the response
    tts.speak(result.get("speech", "Done."))


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    print("""
╔══════════════════════════════════════╗
║   🫐  BLACKBERRY is starting...      ║
║   Say 'Blackberry' to activate       ║
║   Press Ctrl+C to stop               ║
╚══════════════════════════════════════╝
    """)

    # Sanity checks
    if not config.GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set.")
        print(f"   Create file: ~/.blackberry/.env")
        print(f"   Add line:    GEMINI_API_KEY=your_key_here")
        sys.exit(1)

    os.makedirs(config.BASE, exist_ok=True)
    print(f"[BB] Memory folder: {config.BASE}")
    print(f"[BB] LLM: Gemini {config.GEMINI_MODEL}")
    print(f"[BB] Mic: device {config.MIC_DEVICE}")
    print()

    tts.speak("Blackberry is ready. Say Blackberry to activate me.")
    time.sleep(2)   # wait for speaker to finish before mic starts

    while True:
        try:
            if simple_wake_listen():
                handle_command()
            else:
                time.sleep(0.1)   # tiny pause between wake checks

        except KeyboardInterrupt:
            print("\n[BB] Shutting down. Goodbye.")
            tts.speak("Shutting down. Goodbye.")
            break
        except Exception as e:
            print(f"[BB] Error in main loop: {e}")
            time.sleep(1)
            continue


if __name__ == "__main__":
    main()
