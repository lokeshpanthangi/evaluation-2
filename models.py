from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(Integer)
    balance = Column(Integer)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    transaction_type = Column(String)
    amount = Column(Integer)
    description = Column(String)
    reference_transaction_id = Column(Integer)
    recipient_user_id = Column(Integer)
