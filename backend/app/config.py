from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    EMBEDDING_MODEL: str
    DATABASE_URL: str
    UPLOAD_DIR: str
    SEARCH_GAP: float
    SEARCH_LIMIT: int
    
    # WhatsApp / Twilio Ayarları (Hata vermemesi için Optional/Default)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    BASE_PUBLIC_URL: Optional[str] = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore" # .env içinde burada olmayan bir şey varsa görmezden gel

settings = Settings()
