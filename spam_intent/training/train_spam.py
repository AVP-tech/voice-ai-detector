import json
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Paths
DATA_PATH = Path("spam_intent/data/spam_dataset.json")
MODEL_PATH = Path("spam_intent/artifacts/spam_model.pkl")

# Load dataset
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [d["text"].lower() for d in data]
labels = [1 if d["label"] == "spam" else 0 for d in data]

# TF-IDF (language independent)
vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    min_df=1,
    max_features=8000
)

X = vectorizer.fit_transform(texts)
y = labels

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print("\nSpam Intent Classification Report:\n")
print(classification_report(y_test, y_pred))

# Save model
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(
    {
        "model": model,
        "vectorizer": vectorizer
    },
    MODEL_PATH
)

print(f"\n✅ Spam model saved at: {MODEL_PATH}")
