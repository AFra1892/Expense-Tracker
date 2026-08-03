from datetime import date as date_type, datetime
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user
from ..ml_client import predict_category, CONFIDENCE_THRESHOLD

router = APIRouter(prefix="/transactions", tags=["transactions"])

REQUIRED_CSV_COLUMNS = {"date", "description", "amount"}
DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]


def _parse_date(raw: str) -> date_type:
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: '{raw}'")
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

@router.post("/import-csv", response_model=schemas.CSVImportResult)
async def import_transactions_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv")

    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None or not REQUIRED_CSV_COLUMNS.issubset(
        {f.strip().lower() for f in reader.fieldnames}
    ):
        raise HTTPException(
            status_code=400,
            detail="CSV must have columns: date, description, amount (category is optional)",
        )

    category_lookup = {c.name.lower(): c.id for c in db.query(models.Category).all()}

    imported = 0
    errors: list[dict] = []

    for row_num, row in enumerate(reader, start=2):
        normalized = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
        try:
            txn_date = _parse_date(normalized["date"])
            description = normalized["description"]
            if not description:
                raise ValueError("Description cannot be empty")
            amount = float(normalized["amount"])

            category_id = None
            category_name = normalized.get("category", "").lower()
            if category_name:
                category_id = category_lookup.get(category_name)

            db.add(
                models.Transaction(
                    description=description,
                    amount=amount,
                    date=txn_date,
                    category_id=category_id,
                    user_id=current_user.id,
                    category_source="manual",
                )
            )
            imported += 1
        except (ValueError, KeyError) as e:
            errors.append({"row": row_num, "error": str(e)})

    db.commit()
    return {"imported": imported, "skipped": len(errors), "errors": errors[:20]}

@router.post("/{transaction_id}/auto-categorize", response_model=schemas.AutoCategorizeResult)
def auto_categorize_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    txn = _get_owned_transaction(db, transaction_id, current_user)

    category_name, confidence = predict_category(txn.description)
    if category_name is None:
        raise HTTPException(status_code=503, detail="Categorization model is unavailable")

    category = db.query(models.Category).filter(models.Category.name == category_name).first()
    applied = category is not None and confidence >= CONFIDENCE_THRESHOLD

    if applied:
        txn.category_id = category.id
        txn.category_source = "model"
        txn.was_corrected = False
        db.commit()

    return {
        "transaction_id": txn.id,
        "predicted_category": category_name,
        "confidence": confidence,
        "applied": applied,
    }


@router.post("/auto-categorize-all", response_model=schemas.BulkAutoCategorizeResult)
def auto_categorize_all(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    uncategorized = (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == current_user.id, models.Transaction.category_id.is_(None))
        .all()
    )

    category_by_name = {c.name: c for c in db.query(models.Category).all()}

    applied_count = 0
    low_confidence_count = 0
    results = []

    for txn in uncategorized:
        category_name, confidence = predict_category(txn.description)
        applied = False

        if category_name is not None:
            category = category_by_name.get(category_name)
            if category and confidence >= CONFIDENCE_THRESHOLD:
                txn.category_id = category.id
                txn.category_source = "model"
                applied = True
                applied_count += 1
            else:
                low_confidence_count += 1

        results.append({
            "transaction_id": txn.id,
            "predicted_category": category_name,
            "confidence": confidence,
            "applied": applied,
        })

    db.commit()

    return {
        "total_uncategorized": len(uncategorized),
        "applied": applied_count,
        "low_confidence_skipped": low_confidence_count,
        "results": results,
    }
    
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