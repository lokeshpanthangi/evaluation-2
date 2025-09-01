from fastapi import FastAPI
from models import User,Transaction
from schemas import User as userdata, Transaction as transactiondata
from database import Base, engine   
from sqlalchemy.orm import Session  

Base.metadata.create_all(bind=engine)



app = FastAPI()




@app.get("/health")
def health_check():
    return {"status": "healthy"}