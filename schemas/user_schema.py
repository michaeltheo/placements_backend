from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    student = "student"
    admin = "admin"


class UserBase(BaseModel):
    first_name: str
    last_name: str
    AM: str


class UserCreate(UserBase):
    role: Role = Role.student
    pass


class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True
