from typing import List, Optional

from pydantic import BaseModel, Field

from schemas.question_schema import AnswerOption, Question


class UserAnswerDetail(BaseModel):
    """
    Detailed representation of a user's answer including the question and selected options or text response.

    Attributes:
    - question (Question): The full question object related to this answer.
    - selected_option_ids (Optional[List[int]]): Optional list of IDs for the answer options selected by the user.
    - answer_text (Optional[str]): Optional free-text answer provided by the user.
    """
    question: Question
    selected_option_ids: Optional[List[int]] = None
    answer_text: Optional[str] = None


class AnswerDetail(BaseModel):
    """
    Represents details of an answer submission, including option ID and/or text.

    Attributes:
    - answer_option_id (Optional[int]): The ID of the selected answer option, if applicable.
    - answer_text (Optional[str]): The text of the user's answer, for questions allowing text responses.

    Config:
    - from_attributes: Enables ORM mode for compatibility with ORM objects.
    """
    answer_option_id: Optional[int] = None
    answer_text: Optional[str] = None

    class Config:
        from_attributes = True


class UserAnswersResponse(BaseModel):
    """
    Wraps the answers provided by a user along with a message.

    Attributes:
    - answers (List[AnswerOption]): List of answer options provided by the user.
    - message (str): A message about the response, such as success or error information.
    """
    answers: List[AnswerOption]
    message: str


class AnswerSubmission(BaseModel):
    """
    Schema for submitting answers to questions. It can accommodate multiple choice, multiple selection, and text answers.

    Attributes:
    - question_id (int): The ID of the question to which the answer is being submitted.
    - answer_option_ids (Optional[List[int]]): IDs for selected answer options, for questions that are not free-text only.
    - answer_text (Optional[str]): User's text response for free-text questions or alongside selected options.
    """
    question_id: int
    answer_option_ids: Optional[List[int]] = Field(default=None, description="IDs of selected answer options.")
    answer_text: Optional[str] = Field(default=None, description="User's text response, if applicable.")


class QuestionWithAnswers(BaseModel):
    """
    Combines a question with its answers for presentation in response to user queries.

    Attributes:
    - id (int): Unique identifier for the question.
    - question_text (str): The text of the question itself.
    - question_type (str): The type of the question (e.g., multiple choice, text).
    - supports_multiple_answers (bool): Indicates whether the question supports multiple answers.
    - user_answers (List[AnswerDetail]): A list of answers provided by the user for this question.
    """
    id: int
    question_text: str
    question_type: str
    supports_multiple_answers: bool
    user_answers: List[AnswerDetail]

    class Config:
        from_attributes = True
