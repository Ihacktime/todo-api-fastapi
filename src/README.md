# Todo API (FastAPI + JWT + SQLite)

Minimal, production-style API: register/login, JWT auth, user-scoped todos (CRUD).

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
