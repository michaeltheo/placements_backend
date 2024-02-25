from typing import TypeVar, Generic, Optional

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

DataT = TypeVar('DataT')


class Message(BaseModel):
    detail: str = Field(None, examples="Operation completed successfully")


class ResponseWrapper(GenericModel, Generic[DataT]):
    data: Optional[DataT]
    message: Optional[Message]
