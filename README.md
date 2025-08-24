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
- GET /todos — list current user’s todos
- POST /todos — JSON { "title": "Buy milk" }
- GET /todos/{id} — get one
- PATCH /todos/{id}?done=true (or &title=New+title) — update
- DELETE /todos/{id} — delete


30-second curl test
# Register
curl -s -X POST http://127.0.0.1:8000/auth/register -H "Content-Type: application/json" \
 -d '{"username":"ali","password":"pass"}'

# Login (get token)
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=ali&password=pass' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')


# Create + list
curl -s -X POST http://127.0.0.1:8000/todos -H "Authorization: Bearer $TOKEN" \
 -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/todos


Configuration

Environment variables (optional; defaults shown):
SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///./app.db
