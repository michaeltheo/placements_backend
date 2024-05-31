from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class QuestionnaireType(str, Enum):
    STUDENT = 'student'
    COMPANY = 'company'


class QuestionType(str, Enum):
    """
    Enum representing the different types of questions available in the system.

    Attributes:
        multiple_choice: A question allowing the selection of a single answer from multiple options.
        multiple_choice_with_text: A question allowing a single selection from multiple options, with an additional free-text response.
        free_text: A question allowing an unrestricted text response from the user.
    """
    multiple_choice = "multiple_choice"
    multiple_choice_with_text = "multiple_choice_with_text"
    free_text = "free_text"


class AnswerOptionCreate(BaseModel):
    """
    Schema for creating an answer option to be added to a question.

    Attributes:
        option_text (str): Text description of the answer option visible to users.
    """
    option_text: str


class QuestionCreate(BaseModel):
    """
    Schema for creating a new question with necessary attributes to specify how the question should be constructed and presented.

    Attributes:
        question_text (str): The prompt or query presented to the user.
        question_type (QuestionType): Defines the format and interaction style of the question.
        question_questionnaire (QuestionnaireType): Indicates the associated questionnaire type for the question.
        answer_options (Optional[List[AnswerOptionCreate]]): List of pre-defined answers applicable to the question. Defaults to an empty list.
        supports_multiple_answers (bool): True if multiple selections are permitted, otherwise False.
    """
    question_text: str
    question_type: QuestionType
    question_questionnaire: QuestionnaireType
    answer_options: Optional[List[AnswerOptionCreate]] = []
    supports_multiple_answers: bool = False

    class Config:
        from_attributes = True


class QuestionUpdate(BaseModel):
    """
    Schema for updating existing questions. All fields are optional to allow partial updates.

    Attributes:
        question_text (Optional[str]): Updated text for the question.
        question_type (Optional[QuestionType]): Updated question type.
        question_questionnaire (Optional[QuestionnaireType]): Updated questionnaire type.
        answer_options (Optional[List[AnswerOptionCreate]]): Updated list of answer options.
        supports_multiple_answers (Optional[bool]): Updated setting for allowing multiple answers.
    """
    question_text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    question_questionnaire: Optional[QuestionnaireType] = None
    answer_options: Optional[List[AnswerOptionCreate]] = None
    supports_multiple_answers: Optional[bool] = None

    class Config:
        from_attributes = True


class AnswerOption(BaseModel):
    """
    Model representing an answer option linked to a question.

    Attributes:
        id (int): Unique identifier of the answer option.
        option_text (str): Text description of the answer option.
    """
    id: int
    option_text: str

    class Config:
        from_attributes = True


class Question(BaseModel):
    """
    Model representing a question in the system along with its properties and associated answer options.

    Attributes:
        id (int): Unique identifier of the question.
        question_text (str): The text of the question presented to users.
        question_type (QuestionType): The type of the question determining interaction style.
        question_questionnaire (QuestionnaireType): Type of questionnaire to which the question belongs.
        supports_multiple_answers (bool): Indicates if the question permits multiple answers.
        answer_options (Optional[List[AnswerOption]]): Possible answer options available for the question, if applicable.

    Config:
        orm_mode (bool): Enable ORM mode for compatibility with ORM objects.
    """
    id: int
    question_text: str
    question_type: QuestionType
    question_questionnaire: QuestionnaireType
    supports_multiple_answers: bool
    answer_options: Optional[List[AnswerOption]] = []

    class Config:
        from_attributes = True
