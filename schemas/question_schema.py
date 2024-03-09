from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class QuestionType(str, Enum):
    """
    Enum representing the different types of questions that can exist within the system.

    Attributes:
    - multiple_choice: A question that allows the user to select a single answer from a list of options.
    - multiple_choice_with_text: Similar to multiple choice, but also allows for a free-text response.
    - free_text: A question that allows the user to provide a free-text answer.
    """
    multiple_choice = "multiple_choice"
    multiple_choice_with_text = "multiple_choice_with_text"
    free_text = "free_text"


class AnswerOptionCreate(BaseModel):
    """
    Schema for creating an answer option. Used when adding options to a new or existing question.

    Attributes:
    - option_text (str): The text of the answer option that will be displayed to the user.
    """
    option_text: str


class QuestionCreate(BaseModel):
    """
    Schema for creating a new question. This model captures all necessary details to create a question in the system.

    Attributes:
    - question_text (str): The text of the question itself.
    - question_type (QuestionType): The type of the question, determining how it should be presented and answered.
    - answer_options (Optional[List[AnswerOptionCreate]]): A list of answer options for the question, if applicable. Defaults to an empty list.
    - supports_multiple_answers (bool): Indicates whether the question supports selecting multiple answer options. Defaults to False.
    """
    question_text: str
    question_type: QuestionType
    answer_options: Optional[List[AnswerOptionCreate]] = []
    supports_multiple_answers: bool = False


class QuestionUpdate(BaseModel):
    """
    Schema for updating an existing question. All fields are optional, allowing for partial updates.

    Attributes:
    - question_text (Optional[str]): New text for the question, if updating.
    - question_type (Optional[QuestionType]): New type for the question, if changing.
    - answer_options (Optional[List[AnswerOptionCreate]]): New set of answer options, if modifying.
    - supports_multiple_answers (Optional[bool]): Updated indicator of whether multiple answers are supported, if changing.
    """
    question_text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    answer_options: Optional[List[AnswerOptionCreate]] = None
    supports_multiple_answers: Optional[bool] = None


class AnswerOption(BaseModel):
    """
    Model representing an answer option for a question.

    Attributes:
    - id (int): Unique identifier for the answer option.
    - option_text (str): The text content of the answer option.

    Config:
    - from_attributes (bool): Enable ORM mode for compatibility with ORM objects. The 'from_attributes' setting seems misplaced and should likely be 'from_attributes=True'.
    """
    id: int
    option_text: str

    class Config:
        from_attributes = True


class Question(BaseModel):
    """
    Model representing a question within the system, including its answer options.

    Attributes:
    - id (int): Unique identifier for the question.
    - question_text (str): The text of the question.
    - question_type (QuestionType): The type of question, affecting how it's answered.
    - supports_multiple_answers (bool): Whether the question allows for multiple answers to be selected.
    - answer_options (Optional[List[AnswerOption]]): The list of possible answer options for the question, if applicable.

    Config:
    - from_attributes (bool): Enable ORM mode for compatibility with ORM objects. As before, 'from_attributes' might be incorrect and should be 'from_attributes=True'.
    """
    id: int
    question_text: str
    question_type: QuestionType
    supports_multiple_answers: bool
    answer_options: Optional[List[AnswerOption]] = []

    class Config:
        from_attributes = True
