from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from models import APIToken

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_token(api_key: str, api_secret: str, db: Session = Depends(get_db)):
    token = db.query(APIToken).filter_by(api_key=api_key, api_secret=api_secret).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API credentials")
    return token

def get_api_token(
        api_key: str = Header(..., alias="X-API-KEY"),
        api_secret: str = Header(..., alias="X-API-SECRET"),
        db: Session = Depends(get_db)
):
    token = db.query(APIToken).filter_by(api_key=api_key, api_secret=api_secret).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API credentials"
        )
    return token