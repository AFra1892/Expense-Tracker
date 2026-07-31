from datetime import datetime, date as date_type
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

class TransactionCreate(BaseModel):
    description: str
    amount: float
    date: date_type
    category_id: str | None = None


class TransactionUpdate(BaseModel):
    description: str | None = None
    amount: float | None = None
    date: date_type | None = None
    category_id: str | None = None


class TransactionOut(BaseModel):
    id: str
    description: str
    amount: float
    date: date_type
    category: CategoryOut | None = None
    category_source: str
    was_corrected: bool

    class Config:
        from_attributes = True

class CategoryBreakdownItem(BaseModel):
    category: str
    total: float


class MonthlyTotalItem(BaseModel):
    month: str
    total: float

class CSVImportError(BaseModel):
    row: int
    error: str


class CSVImportResult(BaseModel):
    imported: int
    skipped: int
    errors: list[CSVImportError]