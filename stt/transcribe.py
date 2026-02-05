"""
Speech-to-Text transcription module
High-accuracy multilingual transcription via faster-whisper
Supports: English, Hindi, Tamil, Telugu, Malayalam (and more)
"""

from pathlib import Path
from typing import List, Optional

import os


def _select_best_text(texts: List[str]) -> str:
    # Pick the longest non-empty transcript as a simple quality heuristic
    texts = [t.strip() for t in texts if t and t.strip()]
    if not texts:
        return ""
    return max(texts, key=len)


def transcribe_audio(wav_path: str, chunk_sec: int = 30) -> str:
    """
    Transcribes a WAV file to text using faster-whisper.

    Args:
        wav_path (str): Path to WAV file
        chunk_sec (int): Length of each audio chunk in seconds

    Returns:
        str: Full lowercase transcript
    """

    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_path}")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError(
            "faster-whisper not installed. Install via: pip install faster-whisper"
        )

    # Small model is faster; medium/large is more accurate (choose based on hardware)
    model_name = os.environ.get("WHISPER_MODEL", "medium")
    model = WhisperModel(model_name, compute_type="int8")

    segments, _info = model.transcribe(
        str(wav_path),
        language=None,  # auto-detect
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        initial_prompt=None,
        condition_on_previous_text=True,
        word_timestamps=False,
        beam_size=5,
        temperature=0.0,
        prompt_reset_on_temperature=True,
        no_speech_threshold=0.6,
        log_prob_threshold=-1.0,
        compression_ratio_threshold=2.4,
        chunk_length=chunk_sec,
    )

    texts = [seg.text for seg in segments]
    return " ".join(texts).lower().strip()


def detect_language(audio_path: str) -> str:
    """
    Detect language from audio using faster-whisper.
    Returns one of: Tamil, English, Hindi, Malayalam, Telugu (or "English" as fallback).
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError(
            "faster-whisper not installed. Install via: pip install faster-whisper"
        )

    model_name = os.environ.get("WHISPER_MODEL", "medium")
    model = WhisperModel(model_name, compute_type="int8")

    _segments, info = model.transcribe(
        str(audio_path),
        language=None,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        initial_prompt=None,
        condition_on_previous_text=False,
        word_timestamps=False,
        beam_size=1,
        temperature=0.0,
        prompt_reset_on_temperature=True,
        no_speech_threshold=0.6,
        log_prob_threshold=-1.0,
        compression_ratio_threshold=2.4,
        chunk_length=30,
    )

    code = (info.language or "").lower()
    mapping = {
        "ta": "Tamil",
        "en": "English",
        "hi": "Hindi",
        "ml": "Malayalam",
        "te": "Telugu",
    }
    return mapping.get(code, "English")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m stt.transcribe <wav_file>")
        sys.exit(1)

    wav_file = sys.argv[1]

    try:
        print("Transcript:")
        print(transcribe_audio(wav_file))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
