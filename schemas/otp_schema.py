from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OtpBase(BaseModel):
    code: Optional[str] = None
    expiry: Optional[datetime] = None


class OtpValid(BaseModel):
    user_id: int
    internship_id: int
    internship_startDate: datetime
    internship_endDate: datetime
    internship_company: str
    user_firstName: str
    user_lastName: str
    token: str
