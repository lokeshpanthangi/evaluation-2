from fastapi import APIRouter,Depends,HTTPException
from database import get_db
from sqlalchemy.orm import Session
from schemas import Transaction
from models import User,Transaction
from datetime import datetime

wallet_router = APIRouter()

@wallet_router.get("/wallet/{user_id}/balance")
def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    transaction = Transaction(
        user_id=user.id,
        transaction_type="BALANCE",
        amount=0,
        description="Checked balance",
        reference_transaction_id=None,
        recipient_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return {"balance": user.balance}

@wallet_router.put("/wallet/{user_id}/add_money")
def add_money(user_id: int, amount_add: float, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.balance += amount_add
    transaction = Transaction(
        user_id=user.id,
        transaction_type="CREDIT",
        amount=amount_add,
        description="Added money",
        reference_transaction_id=None,
        recipient_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    return {"balance": user.balance}

@wallet_router.post("/wallet/{user_id}/withdraw")
def withdraw(user_id: int, amount_out: float, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.balance < amount_out:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    user.balance -= amount_out
    transaction = Transaction(
        user_id=user.id,
        transaction_type="DEBIT",
        amount=amount_out,
        description="Withdrew money",
        reference_transaction_id=None,
        recipient_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return {"balance": user.balance}

