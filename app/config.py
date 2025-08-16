from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/awards"
    HUGGINGFACE_TOKEN: str = ""  # optional, only if you login to HuggingFace

settings = Settings()