from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """
    Enum for user roles within the application, defining the possible roles a user can have.
    This ensures type safety and clarity when dealing with user roles in the system.

    Values:
    - STUDENT: Represents a user with student privileges.
    - ADMIN: Represents a user with administrator privileges, allowing for broader access and capabilities.
    """
    STUDENT = "student"
    ADMIN = "admin"


class UserBase(BaseModel):
    """
    Base user model defining common attributes shared across different user models.
    This model is used as a foundation to ensure consistency and reduce redundancy.

    Attributes:
    - first_name (str): The user's first name.
    - last_name (str): The user's last name.
    - AM (str): Academic number or unique identifier for the user, specific to the educational context.
    """
    first_name: str
    last_name: str
    AM: str


class UserCreate(UserBase):
    """
    Schema for creating a new user. It inherits from UserBase and adds additional attributes necessary for user creation.

    Attributes:
    - role (UserRole): The role of the new user, defaulting to STUDENT. This determines the user's access level and capabilities within the application.
    """
    role: UserRole = UserRole.STUDENT


class User(UserBase):
    """
    User model for representing a user in the system. It extends UserBase by adding attributes that are specific to a fully realized user entity.

    Attributes:
    - id (int): The unique identifier for the user, typically assigned by the database.
    - role (str): The role of the user, expressed as a string. This could be aligned with the UserRole enum for consistency.

    Config:
    - from_attributes (bool): Enable ORM mode for compatibility with databases. It appears there might be a typo or misconfiguration with 'from_attributes'. The intended usage likely was 'from_attributes=True'.
    """
    id: int
    role: str

    class Config:
        from_attributes = True  # Ensures compatibility with ORM objects by treating them as dictionaries.


class UserCreateResponse(User):
    """
    Response schema for user creation. Extends the User model by including a flag to indicate if the user is an administrator.

    Attributes:
    - isAdmin (bool): A computed field to easily indicate whether the user has administrative privileges, based on the 'role' attribute.

    Config:
    - The Config class might be misconfigured here with 'from_attributes'. If the intention is to enable ORM mode, it should be 'from_attributes=True'.
    """
    isAdmin: bool
    placementsAccessToken: str = Field(..., description="Access token for the user")
    ihuAccessToken: Optional[str] = Field(..., description="Access token for the user")
    ihuRefreshToken: Optional[str] = Field(..., description="Access token for the user")

    @property
    def isAdmin(self) -> bool:
        """Determine if the user is an admin based on the role."""
        return self.role == UserRole.ADMIN.value

    class Config:
        from_attributes = True
