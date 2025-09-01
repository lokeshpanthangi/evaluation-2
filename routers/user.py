from fastapi import APIRouter,Depends,HTTPException
from database import get_db
from sqlalchemy.orm import Session
from schemas import User as UserSchema,UpdateUser
from models import User


user_router = APIRouter()

@user_router.get("/get_all_users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@user_router.post("/create_user")
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


@user_router.get("/get_user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.put("/update_user/{user_id}")
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

