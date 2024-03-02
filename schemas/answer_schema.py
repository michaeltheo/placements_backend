from pydantic import BaseModel


class AnswerBase(BaseModel):
    question_id: int
    answer_text: str


class AnswerCreate(AnswerBase):
    pass


class Answer(AnswerBase):
    id: int

    class Config:
        from_attributes = True
