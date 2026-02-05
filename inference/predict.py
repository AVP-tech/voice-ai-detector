import joblib
import numpy as np
from features.extract import extract_features_from_wav

MODEL_PATH = "artifacts/model.pkl"
_MODEL_CACHE = None

# 🔒 CONFIDENCE THRESHOLDS
AI_THRESHOLD = 0.80
AI_LIKELY_THRESHOLD = 0.60




def _get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = joblib.load(MODEL_PATH)
    return _MODEL_CACHE

def predict_audio(filepath):
    model = _get_model()

    features = extract_features_from_wav(filepath)
    if features is None:
        return {"result": "INVALID_AUDIO", "confidence": 0.0}

    features = features.reshape(1, -1)

    proba = model.predict_proba(features)[0]

    ai_proba = float(proba[1])
    human_proba = float(proba[0])

    # ✅ CORRECT DECISION LOGIC
    if ai_proba >= AI_THRESHOLD:
        label = "AI"
        confidence = ai_proba

    elif ai_proba >= AI_LIKELY_THRESHOLD:
        label = "AI_LIKELY"
        confidence = ai_proba

    else:
        label = "HUMAN"
        confidence = human_proba

    return {
        "result": label,
        "confidence": round(confidence, 3)
    }


if __name__ == "__main__":
    audio_path = "audio/test.wav"
    output = predict_audio(audio_path)
    print(output)
