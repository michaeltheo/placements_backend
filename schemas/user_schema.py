from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: str
    AM: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True
