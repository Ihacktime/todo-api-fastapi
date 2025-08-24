# Todo API (FastAPI + JWT + SQLite)

Minimal API: **register/login**, **JWT auth**, user-scoped **todo CRUD**.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
uvicorn main:app --reload
