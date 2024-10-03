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
    SUPER_ADMIN = 'super_admin'
    SECRETARY = 'secretary'


class Department(str, Enum):
    """
    Enum for departments within the educational institution, representing the various academic departments a user can belong to.

    Values:
    - IT_TEITHE: Represents the former Department of Computer Engineering.
    - EL_TEITHE: Represents the former Department of Electronics.
    - IHU_IEE: Represents the Department of Computer and Electronic Systems Engineering at the International Hellenic University.
    """
    IT_TEITHE = 'ΠΡΩΗΝ ΤΜΗΜΑ ΜΗΧΑΝΙΚΩΝ ΠΛΗΡΟΦΟΡΙΚΗΣ'
    EL_TEITHE = 'ΠΡΩΗΝ ΤΜΗΜΑ ΜΗΧΑΝΙΚΩΝ ΗΛΕΚΤΡΟΝΙΚΗΣ'
    IHU_IEE = 'ΤΜΗΜΑ ΜΗΧΑΝΙΚΩΝ ΠΛΗΡΟΦΟΡΙΚΗΣ ΚΑΙ ΗΛΕΚΤΡΟΝΙΚΩΝ ΣΥΣΤΗΜΑΤΩΝ'


class UserBase(BaseModel):
    """
    Base user model defining common attributes shared across different user models.
    This model is used as a foundation to ensure consistency and reduce redundancy.

    Attributes:
    - first_name (str): The user's first name.
    - last_name (str): The user's last name.
    - AM (str): Academic number or unique identifier for the user, specific to the educational context.
    """
    first_name: Optional[str] = Field(..., description="The user's first name.")
    last_name: Optional[str] = Field(..., description="The user's last name.")
    AM: Optional[str] = Field(..., description="Academic number or unique identifier for the user.")
    department: Optional[Department] = Field(None, description="The department of the user.")


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
       - telephone_number (str, optional): The user's telephone number.
       - email (str): The user's email address.
       - reg_year (str, optional): The user's registration year.
       """
    id: int = Field(..., description="The unique identifier for the user.")
    role: str = Field(..., description="The role of the user.")
    telephone_number: Optional[str] = Field(None, description="The user's telephone number.")
    email: Optional[str] = Field(None, description="The user's email address.")
    reg_year: Optional[str] = Field(None, description="The user's registration year.")

    class Config:
        from_attributes = True


class UserCreateResponse(User):
    """
    Response schema for user creation. Extends the User model by including a flag to indicate if the user is an administrator.

    Attributes:
    - isAdmin (bool): A computed field to easily indicate whether the user has administrative privileges, based on the 'role' attribute.
    - isSecretary (bool): A computed field to easily indicate whether the user has secretary privileges, based on the 'role' attribute.
    """
    isAdmin: bool = Field(..., description="A flag indicating whether the user has administrative privileges.")
    isSecretary: bool = Field(..., description="A flag indicating whether the user has secretary privileges.")

    @property
    def isAdmin(self) -> bool:
        """Determine if the user is an admin based on the role."""
        return self.role == UserRole.ADMIN.value or self.role == UserRole.SUPER_ADMIN.value

    @property
    def isSecretary(self) -> bool:
        """Determine if the user is a secretary based on the role."""
        return self.role == UserRole.SECRETARY.value


class UserLoginResponse(BaseModel):
    """
    Response schema for user login. It includes user details and tokens for placement, IHU access, and IHU refresh.

    Attributes:
    - user (UserCreateResponse): User details.
    - tokens (dict): Tokens including placement, IHU access, and IHU refresh.
    """
    user: UserCreateResponse = Field(..., description="User details.")
    tokens: dict = Field(..., description="Tokens including placement, IHU access, and IHU refresh.")


class UserUpdate(BaseModel):
    """
    Schema for updating user profiles. This model excludes the 'role' field
    to ensure the role cannot be changed via this update.
    """
    first_name: Optional[str] = Field(None, description="The user's first name.")
    last_name: Optional[str] = Field(None, description="The user's last name.")
    AM: Optional[str] = Field(None, description="Academic number or unique identifier for the user.")
    department: Optional[Department] = Field(None, description="The department of the user.")
    telephone_number: Optional[str] = Field(None, description="The user's telephone number.")
    email: Optional[str] = Field(None, description="The user's email address.")
    reg_year: Optional[str] = Field(None, description="The user's registration year.")
