# Todo API (FastAPI + JWT + SQLite)

Minimal API: **register/login**, **JWT auth**, user-scoped **todo CRUD**.

## Run locally

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
uvicorn main:app --reload

Open http://127.0.0.1:8000/docs

Auth:
- POST /auth/register — { "username": "...", "password": "..." }
- POST /auth/login (form) → { "access_token": "...", "token_type": "bearer" }
Header: Authorization: Bearer <token>

Todos:
- GET /todos · POST /todos · GET /todos/{id} · PATCH /todos/{id} · DELETE /todos/{id}

  Env (see example.env):
  SECRET_KEY (change in prod) · DATABASE_URL (default sqlite:///./app.db)

  Stack

FastAPI · Uvicorn · SQLAlchemy 2.x · Passlib (bcrypt) · python-jose
MD

example.env

cat > example.env <<'ENV'

copy to .env in production

SECRET_KEY=change-this
DATABASE_URL=sqlite:///./app.db
ENV

Minimal CI

mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'YAML'
name: ci
on: [push, pull_request]
jobs:
build:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
with:
python-version: "3.11"
- run: python -m pip install -U pip
- run: pip install -r requirements.txt
- run: python -m py_compile main.py
YAML
