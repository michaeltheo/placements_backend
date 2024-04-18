from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database connection URL, using SQLite for local development.
    DATABASE_URL: str = "postgresql://postgres:root@localhost/PlacementsDatabase"

    # Secret key for encoding and decoding JWT tokens.
    # Should be a long, random string in production.
    SECRET_KEY: str = "MikeTest"

    # Algorithm used for JWT encoding and decoding.
    ALGORITHM: str = "HS256"

    # The duration in minutes after which an access token expires.
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 600

    class Config:
        # Path to the .env file from which environment-specific variables can be read.
        env_file = ".env"


# Create an instance of the Settings class to be used throughout the application.
settings = Settings()
