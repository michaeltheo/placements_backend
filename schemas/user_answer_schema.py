from typing import List, Optional

from pydantic import BaseModel

from schemas.user_schema import User


class UserAnswerBase(BaseModel):
    question_id: int
    answer_option_id: int


class UserAnswerCreate(UserAnswerBase):
    pass


class AnswerOptionModel(BaseModel):
    id: int
    option_text: str

    class Config:
        from_attributes = True


class QuestionModel(BaseModel):
    id: int
    question_text: str
    selected_answer: Optional[AnswerOptionModel] = None

    class Config:
        from_attributes = True


class UserAnswerModel(BaseModel):
    question_details: QuestionModel

    class Config:
        from_attributes = True


class DetailedUserAnswersResponse(BaseModel):
    questions_answers: List[UserAnswerModel]
    user_details: User  # Ensure this model is defined elsewhere and includes orm_mode=True if needed.

    class Config:
        from_attributes = True


class UserAnswer(UserAnswerBase):
    id: int
    question_text: str
    answer_text: str
    user_id: int

    class Config:
        from_attributes = True
