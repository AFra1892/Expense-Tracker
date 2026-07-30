import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import Base, engine, SessionLocal
from .routers import auth, categories, transactions, reports
from .seed import seed_categories

load_dotenv()

# Creates tables if they don't exist yet. Fine for this project's scale;
# a bigger project would use Alembic migrations for every schema change.
Base.metadata.create_all(bind=engine)

# Seed preset categories once at startup (idempotent - safe to run every time).
with SessionLocal() as db:
    seed_categories(db)

app = FastAPI(title="Expense Tracker API")

origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(reports.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
