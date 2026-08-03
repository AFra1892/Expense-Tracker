import os
import httpx

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
CONFIDENCE_THRESHOLD = 0.5


def predict_category(description: str) -> tuple[str | None, float | None]:
    try:
        response = httpx.post(
            f"{ML_SERVICE_URL}/predict",
            json={"description": description},
            timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["category"], data["confidence"]
    except (httpx.HTTPError, KeyError, ValueError):
        return None, None