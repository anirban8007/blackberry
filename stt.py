import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile, os
import config

_whisper_model = None

def _get_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        print("[STT] Loading Whisper model (first run takes ~30s)...")
        _whisper_model = WhisperModel(config.WHISPER_MODEL, device="cpu",
                                      compute_type="int8")
        print("[STT] Whisper ready.")
    return _whisper_model


def record_command() -> np.ndarray:
    """Record audio until silence is detected. Returns numpy array."""
    print("[MIC] Recording... (speak now)")
    frames  = []
    silent  = 0.0
    rate    = config.SAMPLE_RATE
    chunk   = 1024

    def callback(indata, frame_count, time_info, status):
        nonlocal silent
        frames.append(indata.copy())
        level = np.abs(indata).mean()
        if level < config.SILENCE_THRESHOLD:
            silent += frame_count / rate
        else:
            silent = 0.0

    with sd.InputStream(samplerate=rate,
                        channels=1,
                        dtype='int16',
                        device=config.MIC_DEVICE,
                        blocksize=chunk,
                        callback=callback):
        while silent < config.SILENCE_SECONDS:
            sd.sleep(100)

    print("[MIC] Done recording.")
    return np.concatenate(frames, axis=0)


def transcribe(audio: np.ndarray) -> str:
    """Convert recorded numpy audio to text using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, 16000, audio)
        tmp_path = f.name

    model    = _get_model()
    segments, _ = model.transcribe(tmp_path, language="en")
    text     = " ".join([s.text for s in segments]).strip()
    os.unlink(tmp_path)

    print(f"[STT] You said: '{text}'")
    return text
