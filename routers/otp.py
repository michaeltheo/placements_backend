# otp_router.py
from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.auth import create_short_lived_token
from core.config import settings
from crud import otp_crud
from crud.company_crud import get_company
from crud.intership_crud import get_user_internship
from dependencies import get_db, get_current_user
from models import Users
from schemas.otp_schema import OtpBase, OtpValid
from schemas.response import ResponseWrapper, Message

router = APIRouter(
    prefix='/otp',
    tags=['otp']
)

# Calculate the expiration time as 6 hours from the current time
expires_time = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES)
expires_in_seconds = settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60


@router.get('/generate', response_model=ResponseWrapper[OtpBase], status_code=status.HTTP_200_OK)
async def generate_otp(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Generate and send an OTP to the user.

    Parameters:
    - db (Session): The database session.

    Returns:
    - dict: A message indicating that the OTP has been sent.
    """
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:

        otp = otp_crud.generate_otp(db, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Send the OTP to the user's email or phone number (implementation not shown)
    # For simplicity, we will just print it here
    otp_response = OtpBase(code=otp.otp, expiry=otp.expiry)
    return ResponseWrapper(data=otp_response, message=Message(detail="OTP code  successufull created."))


@router.post('/validate', response_model=ResponseWrapper[OtpValid], status_code=status.HTTP_200_OK)
async def validate_otp(otp: str, db: Session = Depends(get_db)):
    """
    Validate the OTP provided by the user.

    Parameters:
    - otp (str): The OTP provided by the user.
    - response (Response): The response object to set the cookie.
    - db (Session): The database session.

    Returns:
    - dict: A message indicating the validation result.
    """
    user = otp_crud.validate_otp(db, otp)
    if user:
        internship = get_user_internship(db, user.id)
        if internship:
            company = get_company(db, internship.company_id)
            if not company.name:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This internship has no company")
            access_token = create_short_lived_token(data={"sub": str(user.id)})
            otp_response = OtpValid(
                user_id=user.id,
                internship_id=internship.id,
                internship_startDate=internship.start_date,
                internship_endDate=internship.end_date,
                internship_company=company.name,
                user_firstName=user.first_name,
                user_lastName=user.last_name,
                token=access_token,
            )
            return ResponseWrapper(data=otp_response, message=Message(detail="Otp code validation was successfull!"))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Internship was not found")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")
