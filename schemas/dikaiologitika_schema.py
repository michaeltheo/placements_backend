from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class DikaiologitikaType(str, Enum):
    """
    Enum defining the possible types of documents (Dikaiologitika).
    Each type represents a different category of document that a user can submit.
    """
    Type1 = "Type1"
    Type2 = "Type2"
    Type3 = "Type3"


class DikaiologitikaBase(BaseModel):
    """
    Base model for document data, specifying the type of document.
    Attributes:
    - type (DikaiologitikaType): The type of the document, based on the DikaiologitikaType enum.
    """
    type: DikaiologitikaType


class DikaiologitikaCreate(DikaiologitikaBase):
    """
    Schema for creating a new document. Inherits from DikaiologitikaBase.
    This is used when a user submits a new document, specifying its type.
    """
    pass


class Dikaiologitika(DikaiologitikaBase):
    """
    Full document model including additional details about the document.
    Attributes:
    - id (int): The unique identifier of the document.
    - user_id (int): The ID of the user who owns the document.
    - file_path (str): The file path where the document is stored.
    - date (datetime): The date when the document was uploaded.
    """
    file_name: str
    id: int
    user_id: int
    file_path: str
    date: datetime

    class Config:
        from_attributes = True  # Enables ORM mode for compatibility with ORMs like SQLAlchemy.
