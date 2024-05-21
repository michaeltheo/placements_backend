from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator


class InternshipProgram(str, Enum):
    """
    Enum for internship programs, defining the types of programs available.

    Values:
    - OAED: Represents the OAED program.
    - ESPA: Represents the ESPA program.
    - EMPLOYER_FINANCED: Represents internships exclusively financed by the employer.
    """
    OAED = "ΟΑΕΔ"
    ESPA = "ΕΣΠΑ"
    EMPLOYER_FINANCED = "Αποκλειστικά χρηματοδοτούμενη από εργοδότη"


class InternshipStatus(str, Enum):
    """
    Enum for internship statuses, defining the possible states of an internship.

    Values:
    - PENDING_REVIEW: Represents an internship pending review.
    - ACTIVE: Represents an active internship.
    - ENDED: Represents an ended internship.
    """
    PENDING_REVIEW = "Pending review"
    ACTIVE = "Active"
    ENDED = "Ended"


class InternshipBase(BaseModel):
    """
    Base model for internship, defining common attributes shared across different internship models.

    Attributes:
    - company_id (Optional[int]): The ID of the company associated with the internship.
    - program (InternshipProgram): The internship program.
    - start_date (Optional[datetime]): The start date of the internship.
    - end_date (Optional[datetime]): The end date of the internship.
    """
    company_id: Optional[int] = None
    program: InternshipProgram
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('end_date', always=True)
    def check_dates(cls, v, values, **kwargs):
        """
        Validator to ensure the end date is after the start date.

        Raises:
        - ValueError: If the end date is not after the start date.
        """
        if 'start_date' in values and values['start_date'] and v and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class InternshipCreate(InternshipBase):
    """
    Schema for creating a new internship. Inherits from InternshipBase.
    """
    pass


class InternshipUpdate(InternshipBase):
    """
    Schema for updating an internship. Inherits from InternshipBase and adds the status attribute.

    Attributes:
    - status (Optional[InternshipStatus]): The status of the internship.
    """
    status: Optional[InternshipStatus] = None


class InternshipRead(InternshipBase):
    """
    Schema for reading an internship. Inherits from InternshipBase and adds additional attributes.

    Attributes:
    - id (int): The unique identifier for the internship.
    - user_id (int): The ID of the user associated with the internship.
    - status (InternshipStatus): The status of the internship.
    """
    id: int
    user_id: int
    company_name: Optional[str] = None
    status: InternshipStatus

    class Config:
        from_attributes = True


class InternshipAllRead(BaseModel):
    """
    Schema for reading all details of an internship. Includes additional user and company information.

    Attributes:
    - id (int): The unique identifier for the internship.
    - program (InternshipProgram): The internship program.
    - start_date (Optional[datetime]): The start date of the internship.
    - end_date (Optional[datetime]): The end date of the internship.
    - status (InternshipStatus): The status of the internship.
    - user_id (int): The ID of the user associated with the internship.
    - user_first_name (str): The first name of the user.
    - user_last_name (str): The last name of the user.
    - user_am (str): The academic number or unique identifier of the user.
    - company_name (Optional[str]): The name of the company associated with the internship.
    """
    id: int
    program: InternshipProgram
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: InternshipStatus
    user_id: int
    user_first_name: str
    user_last_name: str
    user_am: str
    company_name: Optional[str]

    class Config:
        from_attributes = True
