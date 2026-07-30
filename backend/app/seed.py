from sqlalchemy.orm import Session
from . import models
PRESET_CATEGORIES = [
    "Food & Dining", "Transport", "Housing & Rent", "Utilities",
    "Shopping", "Entertainment", "Health", "Income", "Other",
]

def seed_categories(db: Session) -> None:
    exsiting_names = {c.name for c in db.query(models.Category).all()}
    for name in PRESET_CATEGORIES:
        if name not in exsiting_names:
            db.add(models.Category(name=name))
    db.commit()