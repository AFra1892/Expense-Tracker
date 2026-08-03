"""
Trains a transaction-description -> category classifier.
TF-IDF (word n-grams) + Logistic Regression — a strong, fast, interpretable
baseline for short, noisy text classification.
"""
import json
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

DATA_PATH = "data/training_data.csv"
MODEL_PATH = "models/category_classifier.joblib"
METRICS_PATH = "models/eval_metrics.json"


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} labeled examples across {df['category'].nunique()} categories")

    X_train, X_test, y_train, y_test = train_test_split(
        df["description"], df["category"],
        test_size=0.2, random_state=42, stratify=df["category"],
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1, analyzer="word")),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    labels = sorted(df["category"].unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    print(f"\nTest accuracy: {accuracy:.3f}")
    print("\nPer-class report:")
    print(classification_report(y_test, y_pred))

    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nSaved model to {MODEL_PATH}")

    metrics = {
        "accuracy": accuracy, "classification_report": report,
        "confusion_matrix": cm.tolist(), "labels": labels,
        "n_train": len(X_train), "n_test": len(X_test),
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved eval metrics to {METRICS_PATH}")


if __name__ == "__main__":
    main()