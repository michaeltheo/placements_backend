from typing import List

from pydantic import BaseModel


class AnswerStatistics(BaseModel):
    answer_id: int
    answer_text: str
    count: int


class QuestionStatistics(BaseModel):
    question_id: int
    question_text: str
    answers: List[AnswerStatistics]
