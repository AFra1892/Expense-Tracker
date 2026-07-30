from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _get_owned_transaction(db: Session, transaction_id: str, user: models.User) -> models.Transaction:
    txn = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.user_id == user.id)
        .first()
    )
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return txn


@router.get("", response_model=list[schemas.TransactionOut])
def list_transactions(
    category_id: str | None = None,
    start_date: date_type | None = None,
    end_date: date_type | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = (
        db.query(models.Transaction)
        .options(joinedload(models.Transaction.category))
        .filter(models.Transaction.user_id == current_user.id)
    )
    if category_id:
        query = query.filter(models.Transaction.category_id == category_id)
    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)

    return query.order_by(models.Transaction.date.desc()).all()


@router.post("", response_model=schemas.TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    txn_in: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if txn_in.category_id:
        category = db.query(models.Category).filter(models.Category.id == txn_in.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    txn = models.Transaction(
        description=txn_in.description,
        amount=txn_in.amount,
        date=txn_in.date,
        category_id=txn_in.category_id,
        user_id=current_user.id,
        category_source="manual",
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@router.put("/{transaction_id}", response_model=schemas.TransactionOut)
def update_transaction(
    transaction_id: str,
    txn_in: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    txn = _get_owned_transaction(db, transaction_id, current_user)
    update_data = txn_in.model_dump(exclude_unset=True)

    if "category_id" in update_data and txn.category_source == "model":
        txn.was_corrected = True

    for field, value in update_data.items():
        setattr(txn, field, value)

    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    txn = _get_owned_transaction(db, transaction_id, current_user)
    db.delete(txn)
    db.commit()