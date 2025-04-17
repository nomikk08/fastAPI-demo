from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import User, Token
from auth import (
    authenticate_user,
    create_access_token,
    decode_and_verify_token,
)
from sqlalchemy.orm import Session
from database import SessionLocal
from langdetect import detect, LangDetectException
from translatepy import Translator

app = FastAPI()
translator = Translator()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_and_verify_token(token)
    return user

@app.get("/me", response_model=User)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/detect_language")
async def detect_language(text: str = Body(...)):
    try:
        lang_code = detect(text)
        return {"language_code": lang_code}
    except LangDetectException:
        raise HTTPException(status_code=400, detail="Unable to detect language")

@app.post("/translate")
async def translate(
        text: str = Body(...),
        original_language: str = Body(...)
):
    try:
        target_languages = ["en", "fr", "de", "es", "hi", "it", "zh"]
        translations = {}

        for lang in target_languages:
            if lang == original_language:
                continue
            try:
                result = translator.translate(text, source_language=original_language, destination_language=lang)
                translations[lang] = [result.result]
            except Exception:
                translations[lang] = ["Translation failed"]

        return {"translations": translations}
    except Exception:
        raise HTTPException(status_code=500, detail="Translation error")
