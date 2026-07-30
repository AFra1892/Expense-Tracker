# Expense Tracker (with AI-powered categorization)

A full-stack expense tracker built to demonstrate taking ML from notebook to production:
FastAPI + React app, with a separate model-serving microservice for AI expense categorization
(coming in Phase 3).

## Status: Phase 1 — Foundation ✅

- [x] FastAPI backend: JWT auth (register/login/me), User/Category/Transaction models
- [x] React (Vite) frontend: login, register, protected dashboard route
- [ ] Phase 2: Categories CRUD, transactions, charts, CSV import, budget alerts, dark mode
- [ ] Phase 3: AI categorization model + serving microservice + feedback loop
- [ ] Phase 4: tests, Docker, deployment, README writeup with model eval results

## Running locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then edit JWT_SECRET_KEY to something random
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

### Frontend
 
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Try it

1. Start both servers above.
2. Go to `http://localhost:5173/register`, create an account.
3. You'll be redirected to `/dashboard` — confirms the full auth flow (register → login → JWT
   → protected route → `/auth/me`) works end to end.

## Architecture notes

- Auth uses JWT bearer tokens (1hr expiry), passwords hashed with bcrypt.
- DB layer uses SQLAlchemy with SQLite for local dev; swap `DATABASE_URL` in `.env` to a
  Postgres URL for deployment (e.g. Render's managed Postgres) — no code changes needed.
- `Transaction.category_source` and `Transaction.was_corrected` are scaffolded now
  even though categorization isn't built yet — these fields are what will power the
  Phase 3 feedback loop (model prediction vs. user correction → retraining data).
