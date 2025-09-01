from fastapi import APIRouter,Depends,HTTPException
from database import get_db
from sqlalchemy.orm import Session
from models import User,Transaction
from datetime import datetime




transaction_router = APIRouter()

@transaction_router.get("/get_user_transactions/{user_id}")
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return {
        "transactions": transactions,
        "total": len(transactions),
        "page": len(transactions) // 10 + 1,
        "limit": 10
    }

@transaction_router.get("/get_transaction_data/{transaction_id}")
def get_transaction_data(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@transaction_router.get("/get_transaction_types")
def get_transaction_types():
    return ["DEBIT", "CREDIT", "TRANSFER_IN", "TRANSFER_OUT"]



@transaction_router.post("/wallet/{user_id}/transfer")
def transfer(user_id: int, amount: float, recipient_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    user.balance -= amount
    recipient.balance += amount
    transaction = Transaction(
        user_id=user.id,
        transaction_type="TRANSFER_OUT",
        amount=amount,
        description=f"Transferred to user {recipient_id}",
        reference_transaction_id=None,
        recipient_user_id=recipient.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    transaction = Transaction(
        user_id=user.id,
        transaction_type="TRANSFER_IN",
        amount=amount,
        description=f"Transferred to user {recipient_id}",
        reference_transaction_id=None,
        recipient_user_id=recipient.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return {"balance": user.balance, "recipient_balance": recipient.balance}


@transaction_router.get("/get_transfer/{transfer_id}")
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(Transaction).filter(Transaction.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer