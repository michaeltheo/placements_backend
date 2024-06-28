import random
import string
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from core.config import settings
from models import OTP, Users


def cleanup_expired_otps(db: Session):
    """
    Delete all expired OTPs from the database.

    Parameters:
    - db (Session): The database session.
    """
    now = datetime.now()
    expired_otps = db.query(OTP).filter(OTP.expiry < now).all()
    for otp in expired_otps:
        db.delete(otp)
    db.commit()


def generate_otp(db: Session, user_id: int) -> OTP:
    """
    Generate a new OTP for the given user. If an existing OTP is still valid, return it.

    Parameters:
    - db (Session): The database session.
    - user_id (int): The ID of the user for whom the OTP is generated.

    Returns:
    - OTP: The generated or existing OTP object.
    """
    # Check if an existing OTP is still valid
    existing_otp = db.query(OTP).filter(OTP.user_id == user_id).first()
    if existing_otp and existing_otp.expiry >= datetime.now():
        return existing_otp

    # Generate a new OTP
    otp = ''.join(random.choices(string.digits, k=6))
    # OTP IS VALID FOR 1 hour
    expiry = datetime.now() + timedelta(minutes=settings.OTP_CODE_EXPIRES_MINUTES)

    # Delete any existing OTPs for the user
    if existing_otp:
        db.delete(existing_otp)
        db.commit()

    # Create and store the new OTP
    db_otp = OTP(user_id=user_id, otp=otp, expiry=expiry)
    db.add(db_otp)
    db.commit()

    return db_otp


def delete_otp(db: Session, otp: str) -> bool:
    """
    Delete the provided OTP from the database.

    Parameters:
    - db (Session): The database session.
    - otp (str): The OTP to delete.

    Returns:
    - bool: True if the OTP was deleted, False otherwise.
    """
    db_otp = db.query(OTP).filter(OTP.otp == otp).first()
    if db_otp:
        db.delete(db_otp)
        db.commit()
        return True
    return False


def validate_otp(db: Session, otp: str) -> Optional[Users]:
    """
    Validate the provided OTP. If valid, return the associated user.

    Parameters:
    - db (Session): The database session.
    - otp (str): The OTP to validate.

    Returns:
    - Optional[Users]: The user associated with the OTP if valid, otherwise None.
    """
    db_otp = db.query(OTP).filter(OTP.otp == otp).first()
    if db_otp and db_otp.expiry >= datetime.now():
        delete_otp(db, otp)
        user = db.query(Users).filter(Users.id == db_otp.user_id).first()
        return user
    return None
