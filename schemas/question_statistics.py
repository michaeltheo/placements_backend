from typing import List, Optional

from pydantic import BaseModel


class OptionCount(BaseModel):
    """
    Represents the count of responses for a specific option of a question.

    Attributes:
        option_id (int): The unique identifier of the answer option.
        count (int): The number of times this option was selected by users.
        text (Optional[str]): For multiple choice questions with free text ("other"), this captures the text response.
                              It is used to include what the "other" text might be when an option allows for a free text response.
    """
    option_id: int
    count: int
    text: Optional[str] = None


class QuestionStatistics(BaseModel):
    """
    Aggregates statistics for a single question, including counts of selected options and any free text responses.

    Attributes:
        question_id (int): The unique identifier of the question being analyzed.
        question_text (str): The text of the question itself.
        statistics (List[OptionCount]): A list of `OptionCount` objects representing the aggregated count of each answer option selected.
        free_text_responses_count (Optional[int]): The number of free text responses submitted for the question. Relevant for multiple choice with free text (MCFT) questions.
        free_text_responses (Optional[List[str]]): A list of free text responses submitted. This stores the actual text responses provided by users for MCFT questions.
    """
    question_id: int
    question_text: str
    statistics: List[OptionCount]
    free_text_responses_count: Optional[int] = 0
    free_text_responses: Optional[List[str]] = []
    total_responses: int = 0
