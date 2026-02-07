# Voice AI Detector

Detect whether a voice is AI-generated or human, and classify calls as normal, suspicious, or spam by combining:
1. Acoustic AI vs human classification.
2. Speech-to-text + multilingual spam intent scoring.
3. A decision engine that merges both signals into a final verdict.

This project ships a CLI pipeline and a Flask API + UI for interactive usage.

**Quick links**
1. **Run the UI/API**: `python ui/app.py`
2. **Run the pipeline (CLI)**: `python run_pipeline.py path\to\audio.wav`

---

**What It Does**

- **AI vs Human voice detection** using a calibrated ML model (`artifacts/model.pkl`).
- **Multilingual spam intent detection** over transcripts (English, Hindi, Tamil, Telugu, Malayalam).
- **End-to-end decisioning** to output a final label and a detailed analysis payload.
- **Flask API + UI** with API key protection for production use.

---

**Architecture Overview**

1. **Audio input** (`.wav` or `.mp3`)
2. **Speech-to-text** using `faster-whisper`
3. **Spam intent scoring** from transcript
4. **AI vs Human model inference**
5. **Decision engine** combines signals to produce the final verdict

---

**Project Structure**

- `ui/app.py`: Flask app with API + UI.
- `ui/templates/index.html`: Frontend UI.
- `run_pipeline.py`: End-to-end CLI pipeline.
- `stt/transcribe.py`: Speech-to-text and language detection.
- `features/extract.py`: Audio feature extraction for AI detection.
- `inference/predict.py`: Model inference wrapper.
- `decision_engine/final_decision.py`: Final verdict rules.
- `spam_intent/`: Multilingual spam intent engine and data.
- `training/train.py`: Model training script.
- `artifacts/model.pkl`: Trained model used for inference.

---

**Requirements**

- Python 3.10+
- FFmpeg available on PATH (required by `faster-whisper` for decoding audio)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

**Configuration**

Environment variables:

- `API_KEY`: Required for `/api/voice-detection` and `/ui/voice-detection`
- `WHISPER_MODEL`: Whisper model name (default: `small`)

Windows example:

```bat
set API_KEY=your_key_here
set WHISPER_MODEL=small
```

---

**Run The UI / API**

```bash
python ui/app.py
```

Or on Windows:

```bat
run_app.bat
```

Endpoints:

1. `GET /`
   - UI page

2. `POST /api/voice-detection`
   - Requires `x-api-key` header
   - JSON body:
     - `language`: `tamil | english | hindi | malayalam | telugu`
     - `audioFormat`: must be `mp3`
     - `audioBase64`: base64-encoded audio bytes (data-URI prefix allowed)
   - Response:
     - `status`, `language`, `classification`, `confidenceScore`, `explanation`

3. `POST /ui/voice-detection`
   - Requires `x-api-key` header
   - JSON body:
     - `audioFormat`: must be `mp3`
     - `audioBase64`: base64-encoded audio bytes
   - Response is the same as `/api/voice-detection`, but language is auto-detected.

---

**Run With Docker**

```bash
docker build -t voice-ai-detector .
docker run -e API_KEY=your_key_here -p 8080:8080 voice-ai-detector
```

The container runs Gunicorn with `main:app` and exposes port `8080`.

---

**Run The CLI Pipeline**

```bash
python run_pipeline.py audio\ENGLISH.wav
```

Output includes:

- Transcript (STT)
- Voice type and confidence
- Spam score and matched intents
- Final verdict label

The pipeline returns a structured dictionary with all fields and the transcript.

---

**Model Training (Optional)**

Train or retrain the AI detection model:

```bash
python training/train.py
```

This expects processed WAV data under:

- `data/ai_processed_v2`
- `data/human_processed_v2`

The trained model is saved to `artifacts/model.pkl`.

---

**Notes and Limitations**

- The end-to-end pipeline expects audio that can be decoded by FFmpeg. For best results, use 16 kHz WAV.
- API endpoints require `API_KEY` to be set in the environment.
- Some legacy test scripts reference an old `SpamIntentEngine.score(..., lang=...)` signature and may need updates.

---
