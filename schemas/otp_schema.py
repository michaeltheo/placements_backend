from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OtpBase(BaseModel):
    """
    OtpBase is a Pydantic model representing the basic structure of an OTP (One-Time Password).

    Attributes:
    - code (Optional[str]): The OTP code. It is optional and can be None.
    - expiry (Optional[datetime]): The expiry time of the OTP. It is optional and can be None.
    """
    code: Optional[str] = None
    expiry: Optional[datetime] = None


class OtpValid(BaseModel):
    """
    OtpValid is a Pydantic model representing the structure of a validated OTP response.

    Attributes:
    - user_id (int): The ID of the user associated with the OTP.
    - internship_id (int): The ID of the internship associated with the OTP.
    - internship_startDate (datetime): The start date of the internship.
    - internship_endDate (datetime): The end date of the internship.
    - internship_company (str): The name of the company associated with the internship.
    - user_firstName (str): The first name of the user associated with the OTP.
    - user_lastName (str): The last name of the user associated with the OTP.
    - token (str): The JWT token generated after validating the OTP.
    """
    user_id: int
    internship_id: int
    internship_startDate: datetime
    internship_endDate: datetime
    internship_company: str
    user_firstName: str
    user_lastName: str
    token: str
