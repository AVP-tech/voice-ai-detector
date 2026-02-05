import joblib
from pathlib import Path

MODEL_PATH = Path("spam_intent/artifacts/spam_model.pkl")

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
vectorizer = bundle["vectorizer"]

def predict_spam(text: str):
    text = text.lower()
    X = vectorizer.transform([text])
    prob = model.predict_proba(X)[0]

    spam_score = float(prob[1])
    label = "SPAM" if spam_score >= 0.6 else "NORMAL"

    return {
        "label": label,
        "spam_score": round(spam_score * 100, 2)
    }


if __name__ == "__main__":
    sample = input("Enter transcript: ")
    result = predict_spam(sample)
    print("\nResult:", result)
