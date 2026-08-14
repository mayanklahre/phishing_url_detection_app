"""ASGI entry point: `uvicorn app:app --host 0.0.0.0 --port 8000`."""

from phishing_detector.api import app
