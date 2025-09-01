from fastapi import FastAPI
from models import Base
from database import engine
from routers.user import user_router
from routers.transactions import transaction_router
from routers.wallet import wallet_router

Base.metadata.create_all(bind=engine)




app = FastAPI()
app.include_router(user_router)

app.include_router(wallet_router)

app.include_router(transaction_router)