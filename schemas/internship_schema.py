from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator

from schemas.user_schema import Department


class InternshipProgram(str, Enum):
    """
    Enum for internship programs, defining the types of programs available.

    Values:
    - OAED: Represents the OAED program.
    - ESPA: Represents the ESPA program.
    - EMPLOYER_FINANCED: Represents internships exclusively financed by the employer.
    """
    TEITHE_OAED = "ΠΡΑΚΤΙΚΗ ΑΣΚΗΣΗ ΧΩΡΙΣ ΕΣΠΑ ( ΙΔΙΩΤΙΚΟΣ 'Η ΔΗΜΟΣΙΟΣ ΤΟΜΕΑΣ)"
    ESPA = "ΠΡΑΚΤΙΚΗ ΑΣΚΗΣΗ ΜΕ ΕΣΠΑ"
    TEITHE_JOB_RECOGNITION = "ΑΝΑΓΝΩΡΙΣΗ ΕΡΓΑΣΙΑΣ ΩΣ ΠΡΑΚΤΙΚΗ ΑΣΚΗΣΗ ΓΙΑ ΕΡΓΑΖΟΜΕΝΟΥΣ ΦΟΙΤΗΤΕΣ"
    EMPLOYER_DECLARATION_OF_RESPONSIBILITY = "ΚΑΛΥΨΗ ΤΗΣ ΑΜΟΙΒΗΣ ΤΟΥ ΦΟΙΤΗΤΗ ΑΠΟ ΤΟΝ ΦΟΡΕΑ"


class InternshipStatus(str, Enum):
    """
    Enum for internship statuses, defining the possible states of an internship.

    Values:
    - SUBMIT_START_FILES: Represents an internship pending start files  before review.
    - SUBMIT_END_FILES: Represents an internship pending ended files before review .
    - PENDING_REVIEW_START: Represents an internship pending review before it's acitve.
    - PENDING_REVIEW_END: Represents an internship pending review before it ends.
    - ACTIVE: Represents an active internship.
    - ENDED: Represents an ended internship.
    """
    SUBMIT_START_FILES = "Κατάθεση Δικαιολογητικών Έναρξης"
    SUBMIT_END_FILES = "Κατάθεση Δικαιολογητικών Λήξης"
    PENDING_REVIEW_START = "Έλεγχος Δικαιολογητικών Έναρξης"
    PENDING_REVIEW_END = "Έλεγχος Δικαιολογητικών Λήξης"
    ACTIVE = "Ενεργή Πρακτική Άσκηση"
    ENDED = "Ολοκληρωμένη Πρακτική Άσκηση"


class InternshipBase(BaseModel):
    """
    Base model for internships, defining common attributes shared across different internship models.
    This model captures key details about an internship, including the associated company, the specific program,
    and the supervisory and timing details of the internship period.

    Attributes:
    - company_id (Optional[int]): The ID of the company associated with the internship. Can be None if not yet assigned.
    - program (InternshipProgram): The specific internship program under which the internship is registered.
    - department (Department): The department within the educational institution or company where the internship takes place.
    - start_date (Optional[datetime]): The start date of the internship, can be None if dates are not finalized.
    - end_date (Optional[datetime]): The expected end date of the internship, should be later than the start date.
    - supervisor (Optional[str]): The name of the supervisor overseeing the internship, can be None if not applicable.
    """
    company_id: Optional[int] = None
    program: InternshipProgram
    department: Department
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    supervisor: Optional[str] = None

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
    id: Optional[int] = None


class InternshipUpdate(InternshipBase):
    """
    Schema for updating an internship. Inherits from InternshipBase and adds the status attribute.

    Attributes:
    - status (Optional[InternshipStatus]): The status of the internship.
    """
    status: Optional[InternshipStatus] = None
    supervisor: Optional[str] = None


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
     - supervisor (Optional[str]): The name of the supervisor overseeing the internship.
    """
    id: int
    program: InternshipProgram
    department: Department
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: InternshipStatus
    supervisor: Optional[str]
    user_id: int
    user_first_name: str
    user_last_name: str
    user_am: str
    company_name: Optional[str]
    company_id: Optional[int]

    class Config:
        from_attributes = True
