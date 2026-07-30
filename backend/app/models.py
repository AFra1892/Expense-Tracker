import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")


class Category(Base):
    """Preset, global categories shared by all users (not user-owned)."""

    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False, unique=True)

    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=gen_uuid)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, default=date.today)

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)

    # Phase 3 hooks: was this category set by the model, and did the user later correct it?
    # These two fields are what let us build the "v1 vs v2" retraining feedback loop later.
    category_source = Column(String, default="manual")  # "manual" | "model"
    was_corrected = Column(Boolean, default=False)

    owner = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
