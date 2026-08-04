# Expense Tracker — with AI-Powered Categorization

A full-stack expense tracker built to demonstrate taking machine learning from a
notebook to a deployed, production-shaped system: a FastAPI + React application, with
a **separately deployable ML microservice** that automatically categorizes expenses
from transaction descriptions.

> **Live demo:** _coming soon_
> **Video walkthrough:** _coming soon_

## Why this project

Most portfolio "expense tracker" projects are CRUD apps with a coat of paint. This one
exists to answer a different question: *can this model actually be trained,
evaluated, served, and improved over time* — not just called as a black-box API.
That's the part of the project that's actually about ML engineering.

## Features

- 🔐 **Authentication** — JWT-based register/login
- 💸 **Transactions** — full CRUD, scoped per user
- 🏷️ **Categories** — 9 preset categories (kept fixed to give the classifier a small,
  consistent label space)
- 📊 **Charts** — spending by category (pie), spending by month (bar)
- 📥 **CSV import** — bulk-load transactions from a bank export, with row-level error
  reporting for malformed rows
- 🤖 **AI categorization** — a real trained text classifier predicts a category from
  the transaction description, with a confidence threshold deciding whether to
  auto-apply the prediction or leave it for the user
- 🔁 **Correction tracking** — every time a user overrides a model-assigned category,
  it's flagged (`was_corrected`) — this is the raw material for retraining a v2 model

**Not yet built:** CSV export, budget alerts, dark mode, live deployment. See
[Roadmap](#roadmap).

## Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌────────────────────┐
│   React     │─────▶│  FastAPI backend │─────▶│  Postgres / SQLite  │
│  (frontend) │      │   (app logic)    │      └────────────────────┘
└─────────────┘      └────────┬─────────┘
                               │  HTTP (description text only)
                               ▼
                      ┌──────────────────┐      ┌────────────────────┐
                      │  FastAPI ML       │─────▶│  TF-IDF + LogReg   │
                      │  service          │      │  classifier (.joblib) │
                      └──────────────────┘      └────────────────────┘
```

The ML service is a **separate deployable unit** from the app backend on purpose —
this mirrors how real ML systems are usually architected, so the model can be
retrained and redeployed independently of the application code that calls it. The app
backend talks to it over HTTP and never touches the model directly.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React (Vite), react-router, recharts, axios |
| Backend | FastAPI, SQLAlchemy, JWT auth (python-jose + passlib) |
| Database | SQLite (dev) / Postgres (production) |
| ML service | FastAPI, scikit-learn, pandas |
| ML approach | TF-IDF (word n-grams) → Logistic Regression |

## The ML model

**Task:** given a transaction description (e.g. `"POS DEBIT STARBUCKS #4521"`),
predict which of the 9 preset categories it belongs to.

**Why TF-IDF + Logistic Regression:** short, noisy, template-like text (bank
statement descriptions) is exactly the regime where a simple bag-of-n-grams model is
a strong, fast, interpretable baseline — a sensible v1 before reaching for anything
heavier.

**Training data:** 405 synthetic but realistic examples (merchant names ×
bank-statement formatting patterns — see `ml-service/generate_training_data.py`), since
no real user transaction history exists yet.

### Evaluation (held-out test set, 81 examples, stratified split)

| Metric | Score |
|---|---|
| **Accuracy** | **92.6%** |

| Category | Precision | Recall | F1 |
|---|---|---|---|
| Entertainment | 1.00 | 1.00 | 1.00 |
| Food & Dining | 0.78 | 0.78 | 0.78 |
| Health | 1.00 | 1.00 | 1.00 |
| Housing & Rent | 0.89 | 0.89 | 0.89 |
| Income | 0.90 | 1.00 | 0.95 |
| Other | 1.00 | 1.00 | 1.00 |
| Shopping | 0.89 | 0.89 | 0.89 |
| Transport | 1.00 | 0.89 | 0.94 |
| Utilities | 0.89 | 0.89 | 0.89 |

Full report including the confusion matrix: `ml-service/models/eval_metrics.json`.

### A real limitation, and the design decision it drove

The model generalizes well to phrasing *patterns* it has seen in training, but can
misfire on unseen phrasing. For example, `"UBER TRIP"` gets classified as
Food & Dining at only **27% confidence** (should be Transport) — the training set had
`"Uber"`-style descriptions but not that exact suffix.

Rather than silently accepting low-confidence predictions, **the app only
auto-applies a category when the model's confidence is ≥ 0.5**. Below that, the
transaction is left uncategorized for the user to set manually. This is a real,
observed tradeoff between coverage and precision — the kind of decision that comes up
constantly in production ML — not a hypothetical.

### The feedback loop (v1 → v2)

`Transaction.category_source` and `Transaction.was_corrected` track every case where
the model predicted a category and the user changed it. That's real labeled data.
The plan (not yet executed): periodically export those corrections, add them to the
training set, retrain, and compare v1 vs. v2 metrics here. That comparison — a
before/after retraining story backed by real numbers — is the strongest interview
talking point in this whole project.

## Running locally

Three services, three terminals.

**1. ML service** (port 8001)
```bash
cd ml-service
python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
mkdir -p data models
python generate_training_data.py
python train.py
uvicorn app.main:app --reload --port 8001
```

**2. Backend** (port 8000)
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit JWT_SECRET_KEY to something random
uvicorn app.main:app --reload
```

**3. Frontend** (port 5173)
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Then open `http://localhost:5173`, register an account, and:
- Import transactions via CSV (or add them manually)
- Click **Auto-categorize with AI** to see the model in action
- Check **Charts** for the spending breakdown

## Roadmap

- [ ] Deploy: backend + ML service to Render, frontend to Vercel
- [ ] CSV export
- [ ] Budget alerts
- [ ] Dark mode
- [ ] Automated tests (pytest for backend + ML service)
- [ ] Retrain on real correction data, publish v1 vs. v2 comparison
- [ ] Dockerize all three services

## Project structure

```
expense-tracker/
├── backend/          # FastAPI app: auth, transactions, categories, reports
├── frontend/         # React (Vite) app
└── ml-service/        # Standalone model training + serving microservice
    ├── generate_training_data.py
    ├── train.py
    ├── app/main.py    # /predict endpoint
    ├── data/          # generated training data (gitignored)
    └── models/        # trained model + eval metrics (gitignored)
```
