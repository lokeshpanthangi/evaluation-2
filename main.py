from fastapi import FastAPI,Depends,HTTPException
from models import User,Transaction,Base
from schemas import User as UserSchema, Transaction as TransactionSchema
from database import engine, SessionLocal,get_db
from sqlalchemy.orm import Session
from routes import router
Base.metadata.create_all(bind=engine)




app = FastAPI()
app.include_router(router)





@app.get("/health")
def health_check():
    return {"status": "healthy"}