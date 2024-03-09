from typing import TypeVar, Generic, Optional, List

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from schemas.dikaiologitika_schema import Dikaiologitika
from schemas.user_schema import User

DataT = TypeVar('DataT')


class Message(BaseModel):
    """
        A model representing a generic message response from the API.

        Attributes:
            detail (str): A descriptive message detailing the result of the operation, which can be used for logging, debugging, or displaying to end-users.
        """
    detail: str = Field(None, example="Operation completed successfully")


class FileAndUser(BaseModel):
    """
    A composite model that encapsulates a list of files (Dikaiologitika) associated with a user.

    Attributes:
        files (List[Dikaiologitika]): A list of Dikaiologitika objects, representing various documents or files associated with the user.
        user (User): The user object associated with the files.
    """

    files: List[Dikaiologitika]
    user: User

    class Config:
        from_attributes = True


class ResponseWrapper(GenericModel, Generic[DataT]):
    """
    A generic response wrapper model to standardize the structure of API responses.

    This model is designed to be flexible and can wrap around any type of data by utilizing Pydantic generics.
    It provides a consistent response format for the API, including both the data payload and an optional message.

    Type Parameters:
        DataT: The type of the data field, allowing for any type (e.g., List[User], Dict, custom Pydantic models).

    Attributes:
        data (Optional[DataT]): The main content of the response. Can be any type specified by the DataT type variable.
        message (Optional[Message]): An optional message providing additional context or information about the response.
    """

    data: Optional[DataT]
    message: Optional[Message]

    class Config:
        from_attributes = True
