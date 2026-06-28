import subprocess, tempfile, os

# edge-tts: free Microsoft cloud TTS, sounds very natural
# Voice options: en-IN-NeerjaNeural (female) / en-IN-PrabhatNeural (male)
VOICE = "en-IN-PrabhatNeural"


def speak(text: str):
    print(f"[TTS] Speaking: '{text}'")
    try:
        # Try edge-tts first (needs internet)
        import subprocess, tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp = f.name
        result = subprocess.run(
            ["edge-tts", "--voice", "en-IN-PrabhatNeural",
             "--text", text, "--write-media", tmp],
            capture_output=True, timeout=10
        )
        if result.returncode == 0:
            subprocess.run(["mpv", "--really-quiet", tmp], capture_output=True)
            os.unlink(tmp)
            return
    except Exception:
        pass

    # Fallback: pyttsx3 (fully offline, no internet needed)
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] All TTS failed: {e}")
        print(f"[TTS] Text was: {text}")


def play_beep():
    """Play a short beep to signal Blackberry is listening."""
    try:
        # Generate a simple beep using Python
        import numpy as np
        import sounddevice as sd
        import config

        freq     = 880           # Hz
        duration = 0.2           # seconds
        t        = np.linspace(0, duration, int(config.SAMPLE_RATE * duration))
        beep     = (np.sin(2 * np.pi * freq * t) * 0.3 * 32767).astype(np.int16)
        sd.play(beep, config.SAMPLE_RATE, device=config.OUT_DEVICE)
        sd.wait()
    except Exception:
        pass   # beep failing should never stop Blackberry
