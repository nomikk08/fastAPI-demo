from pydantic import BaseModel

class APITokenResponse(BaseModel):
    api_key: str
    api_secret: str
