from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/by-category", response_model=list[schemas.CategoryBreakdownItem])
def spending_by_category(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.Category.name, func.sum(models.Transaction.amount))
        .join(models.Transaction, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == current_user.id)
        .group_by(models.Category.name)
        .all()
    )
    return [{"category": name, "total": round(total, 2)} for name, total in rows]


@router.get("/monthly", response_model=list[schemas.MonthlyTotalItem])
def monthly_totals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    is_sqlite = db.bind.dialect.name == "sqlite"
    month_expr = (
        func.strftime("%Y-%m", models.Transaction.date)
        if is_sqlite
        else func.to_char(models.Transaction.date, "YYYY-MM")
    )

    rows = (
        db.query(month_expr.label("month"), func.sum(models.Transaction.amount))
        .filter(models.Transaction.user_id == current_user.id)
        .group_by("month")
        .order_by("month")
        .all()
    )
    return [{"month": month, "total": round(total, 2)} for month, total in rows]