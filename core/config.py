from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database connection URL, using SQLite for local development.
    # DATABASE_URL: str = "postgresql://postgres:root@localhost/PlacementsDatabase"
    DATABASE_URL: str = 'sqlite:///./placements.db'

    # Secret key for encoding and decoding JWT tokens.
    # Should be a long, random string in production.
    SECRET_KEY: str = "MikeTest"

    # Algorithm used for JWT encoding and decoding.
    ALGORITHM: str = "HS256"

    # The duration in minutes after which an access token expires.
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 60
    ACCESS_TOKEN_FOR_COMPANIES_QUESTIONNARIE_EXPIRES_MINUTES: int = 60
    OTP_CODE_EXPIRES_MINUTES: int = 30

    # Client id / Secret id  of the application used to get access token from ihu
    CLIENT_ID: str
    CLIENT_SECRET: str

    class Config:
        # Path to the .env file from which environment-specific variables can be read.
        env_file = ".env"


# Create an instance of the Settings class to be used throughout the application.
settings = Settings()
