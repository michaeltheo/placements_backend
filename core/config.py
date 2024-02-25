from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./placements.db"
    SECRET_KEY: str = "MikeTest"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
