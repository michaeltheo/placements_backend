from typing import TypeVar, Generic, Optional, List

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from schemas.dikaiologitika_schema import Dikaiologitika
from schemas.question_schema import AnswerWithQuestion
from schemas.user_answer_schema import UserAnswerModel
from schemas.user_schema import User

DataT = TypeVar('DataT')


class Message(BaseModel):
    detail: str = Field(None, example="Operation completed successfully")


class FileAndUser(BaseModel):
    files: List[Dikaiologitika]
    user: User


class DetailedUserAnswersResponse(BaseModel):
    questions_answers: List[AnswerWithQuestion]
    user_details: User


class DetailedUserAnswersResponseZ(BaseModel):
    questions_answers: List[UserAnswerModel]
    user_details: User


class ResponseWrapper(GenericModel, Generic[DataT]):
    data: Optional[DataT]
    message: Optional[Message]
