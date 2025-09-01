from fastapi import FastAPI
from models import Base
from database import engine
from wallet import wallet_router
from user import user_router
from transactions import transaction_router

Base.metadata.create_all(bind=engine)




app = FastAPI()
app.include_router(user_router)

app.include_router(wallet_router)

app.include_router(transaction_router)