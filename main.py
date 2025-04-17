from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal, Base, engine
from langdetect import detect, LangDetectException
from translatepy import Translator
import re

from dependencies import get_api_token
from models import APIToken
from schemas import APITokenResponse

app = FastAPI()
Base.metadata.create_all(bind=engine)
translator = Translator()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/generate-token", response_model=APITokenResponse)
def generate_token(db: Session = Depends(get_db)):
    token = APIToken()
    db.add(token)
    db.commit()
    db.refresh(token)
    return {
        "api_key": token.api_key,
        "api_secret": token.api_secret
    }

@app.get("/protected-route")
def read_protected_data(token: APIToken = Depends(get_api_token)):
    return {
        "message": "You have access to this protected route!",
        "your_api_key": token.api_key,
        "your_api_secret": token.api_secret
    }

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

def split_text_into_phrases(text: str):
    # Split by sentence-ending punctuation, keep it simple for now
    phrases = re.split(r'[.?!]\s*', text)
    return [p.strip() for p in phrases if p.strip()]

@app.post("/phrase_definitions")
async def phrase_definitions(text: str = Body(...)):
    phrases = split_text_into_phrases(text)
    target_languages = ["en", "fr", "de", "es", "hi", "it"]

    results = []

    for phrase in phrases:
        definitions = []
        for lang in target_languages:
            try:
                translated = translator.translate(phrase, destination_language=lang)
                definitions.append({
                    "text": translated.result,
                    "language": lang,
                    "reference": "menulance.com"
                })
            except Exception:
                definitions.append({
                    "text": "Translation failed",
                    "language": lang,
                    "reference": "menulance.com"
                })

        results.append({
            "phrase": phrase,
            "definitions": definitions
        })

    return {"result": results}