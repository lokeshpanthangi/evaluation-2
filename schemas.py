from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    email: str
    password : str
    phone_number: int
    balance: float  

class Transaction(BaseModel):
    user_id: int
    transaction_type: str
    amount: float
    description: Optional[str]
    reference_transaction_id: Optional[int]
    recipient_user_id: int
