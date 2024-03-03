from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    """
    Enum for user roles within the application.
    Defines the possible roles a user can have.
    """
    STUDENT = "student"
    ADMIN = "admin"


class UserBase(BaseModel):
    """
    Base user model defining common attributes for a user.
    Used as a foundation for more specific user schemas.
    """
    first_name: str
    last_name: str
    AM: str  # Academic number or unique identifier for the user.


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    Inherits from UserBase and adds a role with a default value.
    """
    role: UserRole = UserRole.STUDENT  # Default role for new users.


class User(UserBase):
    """
    User model for representing a user in the system.
    Extends UserBase with an id and role for complete user representation.
    """
    id: int
    role: str


class UserCreateResponse(User):
    """
    Response schema for user creation.
    Extends the User model with an isAdmin field to indicate admin status.
    """
    isAdmin: bool  # Indicates if the user has an admin role.

    class Config:
        from_attributes = True  # This might be a custom Pydantic configuration.
