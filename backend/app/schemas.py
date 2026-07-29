from datetime import datetime, date
from pydantic import BaseModel, EmailStr


# ---- Auth ----

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Category (used by later phases too) ----

class CategoryOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


# ---- Transaction (scaffolded now, wired up in Phase 2) ----

class TransactionOut(BaseModel):
    id: str
    description: str
    amount: float
    date: date
    category: CategoryOut | None = None
    category_source: str

    class Config:
        from_attributes = True
