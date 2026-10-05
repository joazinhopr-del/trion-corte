"""Vercel/FastAPI compatibility entrypoint.

The application itself lives in app.main. Keeping this root module makes the
project discoverable by hosts that look for a conventional `main.py`.
"""

from app.main import app

__all__ = ["app"]
