from datetime import datetime, timedelta

from jose import jwt

from core.config import settings


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.

    Parameters:
    - data (dict): The data to encode in the JWT.
    - expires_delta (timedelta, optional): The timedelta for when the token should expire.
      If not provided, it defaults to the ACCESS_TOKEN_EXPIRES_MINUTES setting.

    Returns:
    - str: A JWT encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_short_lived_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a short-lived JWT access token used for companies to submit their questionnaires.

    Parameters:
    - data (dict): The data to encode in the JWT.
    - expires_delta (timedelta, optional): The timedelta for when the token should expire.
      If not provided, it defaults to 1 hour.

    Returns:
    - str: A JWT encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_FOR_COMPANIES_QUESTIONNAIRE_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_jwt(token: str) -> dict:
    """
    Verify a JWT token and decode it.

    Parameters:
    - token (str): The JWT token to verify and decode.

    Returns:
    - dict: The decoded token data.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
