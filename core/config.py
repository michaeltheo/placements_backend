from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 360
    ACCESS_TOKEN_FOR_COMPANIES_QUESTIONNAIRE_EXPIRES_MINUTES: int = 60
    OTP_CODE_EXPIRES_MINUTES: int = 1440
    CLIENT_ID: str
    CLIENT_SECRET: str
    ENVIRONMENT: str

    # Environment-specific settings
    DATABASE_URL: str
    COOKIE_SECURE: bool = False  # Default to False for development
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    TRUSTED_HOSTS: list = ["localhost", '127.0.0.1']
    REDIRECT_URI: str = 'http://localhost:3000/auth'

    # Client id / Secret id  of the application used to get access token from ihu
    CLIENT_ID: str
    CLIENT_SECRET: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    class Config:
        # Path to the .env file from which environment-specific variables can be read.
        env_file = ".env"


# Create an instance of the Settings class to be used throughout the application.
settings = Settings()

if settings.ENVIRONMENT == "production":
    settings.COOKIE_SECURE = True
    settings.CORS_ORIGINS = ["placements.iee.ihu.gr"]
    settings.TRUSTED_HOSTS = ["placements.iee.ihu.gr", "*.placements.iee.ihu.gr"]
    settings.REDIRECT_URI = 'https://placements.iee.ihu.gr/auth'
