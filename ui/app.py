import sys
import os
import base64
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# -----------------------------
# Fix imports (project root)
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline import run_pipeline
from inference.predict import predict_audio
from stt.transcribe import detect_language

app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
SUPPORTED_LANGUAGES = {"tamil", "english", "hindi", "malayalam", "telugu"}



# -----------------------------
# Home page (GET)
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# -----------------------------
# Detect button (POST)
# -----------------------------
@app.route("/detect", methods=["POST"])
def detect():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save temp file
    temp_dir = PROJECT_ROOT / "temp_audio"
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / audio_file.filename
    audio_file.save(temp_path)

    # Run pipeline
    try:
        result = run_pipeline(str(temp_path), verbose=False)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _require_api_key(req):
    key = req.headers.get("x-api-key") or req.headers.get("X-API-KEY")
    return key == API_KEY


def _safe_ext_from_format(audio_format: str) -> str:
    if not audio_format:
        return ".wav"
    audio_format = audio_format.strip().lower()
    if not audio_format.startswith("."):
        audio_format = f".{audio_format}"
    return audio_format


def _normalize_language(lang_value):
    if not lang_value:
        return None
    return str(lang_value).strip().lower()


@app.route("/api/voice-detection", methods=["POST"])
def api_voice_detection():
    # API key check (required by guidelines)
    if not _require_api_key(request):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    language = data.get("language")
    audio_format = data.get("audioFormat")
    audio_base64 = data.get("audioBase64")

    language_norm = _normalize_language(language)
    if language_norm not in SUPPORTED_LANGUAGES:
        return jsonify({"status": "error", "message": "Unsupported language"}), 400

    if not audio_format or str(audio_format).strip().lower() != "mp3":
        return jsonify({"status": "error", "message": "audioFormat must be mp3"}), 400

    if not audio_base64:
        return jsonify({"status": "error", "message": "audioBase64 is required"}), 400

    temp_dir = PROJECT_ROOT / "temp_audio"
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / f"api_{uuid.uuid4().hex}.mp3"

    try:
        # Support data URI prefix if provided
        if isinstance(audio_base64, str) and "base64," in audio_base64:
            audio_base64 = audio_base64.split("base64,", 1)[1]
        audio_bytes = base64.b64decode(audio_base64)
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Invalid base64 audio: {e}"}), 400

    try:
        voice_result = predict_audio(str(temp_path))
        voice_type = voice_result["result"]
        if voice_type == "INVALID_AUDIO":
            return jsonify({"status": "error", "message": "Invalid audio"}), 400
        confidence = float(voice_result["confidence"])

        classification = "AI_GENERATED" if voice_type in {"AI", "AI_LIKELY"} else "HUMAN"
        confidence = max(0.0, min(1.0, confidence))

        if classification == "AI_GENERATED":
            explanation = "Unnatural pitch consistency and synthetic speech patterns detected"
        else:
            explanation = "Natural pitch variation and human speech patterns detected"

        return jsonify(
            {
                "status": "success",
                "language": language,
                "classification": classification,
                "confidenceScore": round(confidence, 2),
                "explanation": explanation,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/ui/voice-detection", methods=["POST"])
def ui_voice_detection():
    if not _require_api_key(request):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    audio_format = data.get("audioFormat")
    audio_base64 = data.get("audioBase64")

    if not audio_format or str(audio_format).strip().lower() != "mp3":
        return jsonify({"status": "error", "message": "audioFormat must be mp3"}), 400

    if not audio_base64:
        return jsonify({"status": "error", "message": "audioBase64 is required"}), 400

    temp_dir = PROJECT_ROOT / "temp_audio"
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / f"ui_{uuid.uuid4().hex}.mp3"

    try:
        if isinstance(audio_base64, str) and "base64," in audio_base64:
            audio_base64 = audio_base64.split("base64,", 1)[1]
        audio_bytes = base64.b64decode(audio_base64)
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Invalid base64 audio: {e}"}), 400

    try:
        detected_language = detect_language(str(temp_path))
        voice_result = predict_audio(str(temp_path))
        voice_type = voice_result["result"]
        if voice_type == "INVALID_AUDIO":
            return jsonify({"status": "error", "message": "Invalid audio"}), 400
        confidence = float(voice_result["confidence"])

        classification = "AI_GENERATED" if voice_type in {"AI", "AI_LIKELY"} else "HUMAN"
        confidence = max(0.0, min(1.0, confidence))

        if classification == "AI_GENERATED":
            explanation = "Unnatural pitch consistency and synthetic speech patterns detected"
        else:
            explanation = "Natural pitch variation and human speech patterns detected"

        return jsonify(
            {
                "status": "success",
                "language": detected_language,
                "classification": classification,
                "confidenceScore": round(confidence, 2),
                "explanation": explanation,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
