from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import TokenData, UserInDB, UserTable
from database import SessionLocal
from fastapi import HTTPException, status

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === Password hashing ===
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

# === User helpers ===
def get_user(db: Session, username: str):
    return db.query(UserTable).filter(UserTable.username == username).first()

def authenticate_user(username: str, password: str):
    db = SessionLocal()
    user = get_user(db, username)
    db.close()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return UserInDB(**user.__dict__)

# === JWT creation ===
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === JWT decoding + DB user retrieval ===
def decode_and_verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        db = SessionLocal()
        user = get_user(db, username)
        db.close()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return UserInDB(**user.__dict__)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
