# schemas/question_schema.py
from typing import List, Optional

from pydantic import BaseModel, Field


class AnswerOptionBase(BaseModel):
    option_text: str


class AnswerOptionCreate(AnswerOptionBase):
    pass


class AnswerOptionUpdate(BaseModel):
    option_text: Optional[str] = None


class AnswerOption(AnswerOptionBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    question_text: str


class QuestionCreate(QuestionBase):
    answer_options: Optional[List[AnswerOptionCreate]] = Field(default=None)


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    answer_options: Optional[List[AnswerOptionCreate]] = Field(default=None)


class QuestionWithAnswers(BaseModel):
    id: int
    text: str
    answers: List[AnswerOption]


class AnswerWithQuestion(BaseModel):
    question: QuestionWithAnswers


class AnswerOptionModel(BaseModel):
    id: int
    option_text: str


class QuestionModel(BaseModel):
    id: int
    question_text: str
    selected_answer: Optional[AnswerOptionModel] = None  # The user's selected answer


class UserAnswerModel(BaseModel):
    question_details: QuestionModel


class Question(QuestionBase):
    id: int
    answer_options: List[AnswerOption] = []

    class Config:
        from_attributes = True
