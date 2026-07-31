from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_CLOUD_PROJECT: str = ""
    GCS_BUCKET_NAME: str = "360-field-check-media"
    GEMINI_API_KEY: str = ""
    FIREBASE_PROJECT_ID: str = ""
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/fieldcheck"
    JWT_SECRET: str = "changeme"

    class Config:
        env_file = ".env"

settings = Settings()
