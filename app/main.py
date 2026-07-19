import os
import time

import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from google.api_core import exceptions as google_exceptions
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel

app = FastAPI(title="ai-api")

REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["endpoint", "status"])
LATENCY = Histogram("request_latency_seconds", "Request latency in seconds", ["endpoint"])


class Question(BaseModel):
    question: str


def get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"))


@app.post("/ask")
def ask(body: Question):
    start = time.time()
    status = "200"
    try:
        model = get_model()
        result = model.generate_content(body.question)
        return {"answer": result.text}
    except HTTPException:
        status = "500"
        raise
    except google_exceptions.ResourceExhausted:
        status = "429"
        raise HTTPException(status_code=429, detail="Gemini rate limit reached, retry later")
    except Exception:
        status = "502"
        raise HTTPException(status_code=502, detail="Upstream Gemini error")
    finally:
        REQUESTS.labels(endpoint="/ask", status=status).inc()
        LATENCY.labels(endpoint="/ask").observe(time.time() - start)


@app.get("/health")
def health():
    REQUESTS.labels(endpoint="/health", status="200").inc()
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
