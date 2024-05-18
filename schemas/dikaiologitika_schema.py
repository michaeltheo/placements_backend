from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class DikaiologitikaType(str, Enum):
    """
    Enum defining the possible types of documents (Dikaiologitika).
    Each type represents a different category of document that a user can submit.
    """
    BebaiosiPraktikis = "BebaiosiPraktikis"
    AitisiForeaGiaApasxolisiFoititi = "AitisiForeaGiaApasxolisiFoititi"
    BebaiosiApasxolisis = "BebaiosiApasxolisis"
    AsfalisiAskoumenou = "AsfalisiAskoumenou"


class SubmissionTime(str, Enum):
    START = "Έναρξη"
    END = "Λήξη"


class DikaiologitikaBase(BaseModel):
    """
    Base model for document data, specifying the type of document.

    Attributes:
    - type (DikaiologitikaType): The type of the document, based on the DikaiologitikaType enum.
    - submission_time (SubmissionTime): The submission time of the document.
    """
    type: DikaiologitikaType
    submission_time: Optional[SubmissionTime] = None


class DikaiologitikaCreate(DikaiologitikaBase):
    """
    Schema for creating a new document. Inherits from DikaiologitikaBase.
    This is used when a user submits a new document, specifying its type and submission time.
    """
    pass


class Dikaiologitika(DikaiologitikaBase):
    """
    Full document model including additional details about the document.

    Attributes:
    - id (int): The unique identifier of the document.
    - user_id (int): The ID of the user who owns the document.
    - file_name (str): The name of the file.
    - file_path (str): The file path where the document is stored.
    - date (datetime): The date when the document was uploaded.
    - description (Optional[str]): Optional description of the document.
    """
    id: int
    user_id: int
    file_name: str
    file_path: str
    date: datetime
    description: Optional[str] = None

    class Config:
        from_attributes = True
