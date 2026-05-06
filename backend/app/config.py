from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    EMBEDDING_MODEL: str
    DATABASE_URL: str
    UPLOAD_DIR: str
    SEARCH_THRESHOLD: float

    class Config:
        env_file = ".env"

settings = Settings()
