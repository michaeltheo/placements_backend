# otp_crud.py
import random
import string
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from models import OTP, Users


def generate_otp(db: Session, user_id: int) -> OTP:
    existing_otp = db.query(OTP).filter(OTP.user_id == user_id).first()
    if existing_otp and existing_otp.expiry >= datetime.now():
        return existing_otp

    # Generate new OTP
    otp = ''.join(random.choices(string.digits, k=6))
    expiry = datetime.now() + timedelta(hours=10)  # OTP is valid for 10 hours

    # Delete any existing OTPs for the user
    if existing_otp:
        db.delete(existing_otp)
        db.commit()

    db_otp = OTP(user_id=user_id, otp=otp, expiry=expiry)
    db.add(db_otp)
    db.commit()

    return db_otp


def validate_otp(db: Session, otp: str) -> Optional[Users]:
    db_otp = db.query(OTP).filter(OTP.otp == otp).first()
    print('validate otp', db_otp)
    if db_otp and db_otp.expiry >= datetime.now():
        user = db.query(Users).filter(Users.id == db_otp.user_id).first()
        db.delete(db_otp)
        db.commit()
        return user
    return None
