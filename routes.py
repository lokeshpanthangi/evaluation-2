from fastapi import APIRouter,Depends,HTTPException
from database import get_db
from sqlalchemy.orm import Session
from schemas import User as UserSchema,UpdateUser,Transaction as TransactionSchema
from models import User,Transaction
from datetime import datetime


router = APIRouter()

#User Operations

@router.get("/get_all_users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.post("/create_user")
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password,
        phone_number=user.phone_number,
        balance=user.balance
    )
    if user.balance <= 0:
        raise HTTPException(status_code=400, detail="Balance must be positive")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/get_user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/update_user/{user_id}")
def update_user(user_id: int, user: UpdateUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email
    if user.password is not None:
        db_user.password = user.password
    if user.phone_number is not None:
        db_user.phone_number = user.phone_number
    if user.balance is not None:
        db_user.balance = user.balance
    db.commit()
    db.refresh(db_user)
    return db_user


#Transaction Operations

@router.post("/create_transaction")
def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
    db_transaction = Transaction(
        user_id=transaction.user_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
        reference_transaction_id=transaction.reference_transaction_id,
        recipient_user_id=transaction.recipient_user_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/get_user_transactions/{user_id}")
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return transactions

@router.get("/get_transaction_data/{transaction_id}")
def get_transaction_data(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/get_transaction_types")
def get_transaction_types():
    return ["DEBIT", "CREDIT", "TRANSFER_IN", "TRANSFER_OUT"]



#Wallet Operations 

@router.get("/wallet/{user_id}/balance")
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

@router.put("/wallet/{user_id}/add_money")
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

@router.post("/wallet/{user_id}/withdraw")
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


#Transfer_data

@router.post("/wallet/{user_id}/transfer")
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


@router.get("/get_transfer/{transfer_id}")
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(Transaction).filter(Transaction.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer