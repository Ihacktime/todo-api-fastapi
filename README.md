# Todo API (FastAPI + JWT + SQLite)

Minimal, production-style API: **register/login**, **JWT auth**, and **user-scoped Todo CRUD**.

## Quick start
~~~bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
uvicorn main:app --reload
~~~
Open **http://127.0.0.1:8000/docs** for Swagger.

## Auth
- `POST /auth/register` — JSON `{ "username": "ali", "password": "pass" }`
- `POST /auth/login` — **form** (`application/x-www-form-urlencoded`)
  - Response: `{ "access_token": "...", "token_type": "bearer" }`
  - Use header: `Authorization: Bearer <token>`
- `GET /me` — current user info

## Todos (require Bearer token)
- `GET /todos` — list your todos
- `POST /todos` — JSON `{ "title": "Buy milk" }`
- `GET /todos/{id}` — get one
- `PATCH /todos/{id}?done=true` (or `&title=New+title`) — update
- `DELETE /todos/{id}` — delete

## 30-second curl test
~~~bash
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
~~~

## Configuration
Optional env vars (defaults shown):
~~~text
SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///./app.db
~~~
You can copy `example.env` to `.env` in production.

## Stack
FastAPI · Uvicorn · SQLAlchemy 2.x · Passlib (bcrypt) · python-jose

## License
MIT
