"""
Standalone model-serving microservice — deliberately separate from the main app
backend, mirroring how real ML systems decouple model serving from application code.
"""
import joblib
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "category_classifier.joblib"

app = FastAPI(title="Expense Categorization Model Service")

_model = None


@app.on_event("startup")
def load_model():
    global _model
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found at {MODEL_PATH}. Run `python train.py` first.")
    _model = joblib.load(MODEL_PATH)


class PredictRequest(BaseModel):
    description: str


class PredictResponse(BaseModel):
    category: str
    confidence: float


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": _model is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if not req.description.strip():
        raise HTTPException(status_code=400, detail="description cannot be empty")

    probs = _model.predict_proba([req.description])[0]
    classes = _model.classes_
    best_idx = probs.argmax()

    return {"category": classes[best_idx], "confidence": round(float(probs[best_idx]), 4)}