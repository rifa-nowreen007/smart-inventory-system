from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..schemas import TransactionOut
from ..models import Transaction
from . import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.get("/", response_model=List[TransactionOut])
def list_transactions(skip: int=Query(0), limit: int=Query(100), db: Session=Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Transaction).options(joinedload(Transaction.product), joinedload(Transaction.user))
    if user.role == "staff": q = q.filter(Transaction.user_id == user.id)
    txs = q.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return [TransactionOut(id=t.id, product_id=t.product_id, user_id=t.user_id, type=t.type, qty=t.qty, unit_price=t.unit_price, total=t.total, note=t.note or "", created_at=t.created_at, product_name=t.product.name if t.product else None, product_sku=t.product.sku if t.product else None, user_name=t.user.name if t.user else None) for t in txs]
