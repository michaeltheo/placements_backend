from datetime import datetime

from pydantic import BaseModel


class DikaiologitikaBase(BaseModel):
    type: str


class DikaiologitikaCreate(DikaiologitikaBase):
    pass


class Dikaiologitika(DikaiologitikaBase):
    id: int
    user_id: int
    file_path: str
    date: datetime

    class Config:
        from_attributes = True
