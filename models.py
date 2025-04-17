import uuid
import secrets
from sqlalchemy import Column, String
from database import Base

class APIToken(Base):
    __tablename__ = "api_tokens"

    api_key = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    api_secret = Column(String, nullable=False, default=lambda: secrets.token_hex(16))
