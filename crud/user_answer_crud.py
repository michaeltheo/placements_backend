from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models import UserAnswer as Models_UserAnswer, Question as Models_Question, AnswerOption
from schemas.question_schema import QuestionType
from schemas.user_answer_schema import AnswerSubmission, QuestionWithAnswers, AnswerDetail


def submit_user_answers(db: Session, user_id: int, submissions: List[AnswerSubmission]):
    """
    Submits answers for a user, updating existing answers or adding new ones as needed.

    :param db: Database session.
    :param user_id: ID of the user submitting answers.
    :param submissions: List of `AnswerSubmission` objects containing the answers.
    """
    for submission in submissions:
        # Retrieve the question to ensure it exists
        question = db.query(Models_Question).filter(Models_Question.id == submission.question_id).first()
        if not question:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Question with ID {submission.question_id} not found.")

        # Validate for duplicated IDs in answer_option_ids
        if submission.answer_option_ids and len(submission.answer_option_ids) != len(set(submission.answer_option_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Duplicate answer option IDs found for question ID {submission.question_id}.")
        # Validate each answer_option_id against the question's valid options
        valid_option_ids = {option.id for option in question.answer_options}
        invalid_option_ids = set(submission.answer_option_ids or []) - valid_option_ids
        if invalid_option_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid answer option IDs {list(invalid_option_ids)} for question ID {submission.question_id}.")

        # Delete existing answers for this question and user
        db.query(Models_UserAnswer).filter(
            Models_UserAnswer.user_id == user_id,
            Models_UserAnswer.question_id == submission.question_id
        ).delete(synchronize_session='fetch')
        db.flush()

        # Validate submissions for questions that do not support multiple answers
        # Ensure submission.answer_option_ids is not None before checking its length
        if not question.supports_multiple_answers and submission.answer_option_ids and len(
                submission.answer_option_ids) > 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="This question does not support multiple answers.")

        # Handle submissions based on question type
        if question.question_type == QuestionType.free_text and submission.answer_text:
            # Add free text answer
            db.add(Models_UserAnswer(
                user_id=user_id,
                question_id=submission.question_id,
                answer_text=submission.answer_text
            ))
        if question.question_type == QuestionType.multiple_choice_with_text:
            other_option_id = next((option.id for option in question.answer_options if option.option_text == "Άλλο"),
                                   None)
            if other_option_id and other_option_id in submission.answer_option_ids:
                # "Άλλο" option is selected and there is an answer text
                db.add(Models_UserAnswer(
                    user_id=user_id,
                    question_id=submission.question_id,
                    answer_option_id=other_option_id,
                    answer_text=submission.answer_text  # Save the answer text here
                ))
                # Remove the other_option_id from the answer_option_ids list to avoid adding it again
                submission.answer_option_ids.remove(other_option_id)

        # Handle multiple choice submissions
        if submission.answer_option_ids:
            for option_id in submission.answer_option_ids:
                db.add(Models_UserAnswer(
                    user_id=user_id,
                    question_id=submission.question_id,
                    answer_option_id=option_id,
                    answer_text=None  # Text is handled separately
                ))

        db.commit()


def get_question_with_user_answers(db: Session, user_id: int) -> List[QuestionWithAnswers]:
    """
    Retrieves all questions along with the user's answers.

    :param db: Database session.
    :param user_id: ID of the user whose answers are to be retrieved.
    :return: `List of QuestionWithAnswers` objects.
    """
    user_responses = []

    detailed_questions = db.query(Models_Question).all()

    for question in detailed_questions:
        user_answers = db.query(Models_UserAnswer).filter_by(user_id=user_id, question_id=question.id).all()
        if user_answers:
            question_detail = QuestionWithAnswers(
                id=question.id,
                question_text=question.question_text,
                question_type=question.question_type.value,
                supports_multiple_answers=question.supports_multiple_answers,
                user_answers=[
                    AnswerDetail(
                        answer_option_id=ans.answer_option_id,
                        answer_text=ans.answer_text,
                        answer_option_text=db.query(AnswerOption.option_text).filter_by(
                            id=ans.answer_option_id).scalar() if ans.answer_option_id else None
                    ) for ans in user_answers
                ]
            )
            user_responses.append(question_detail)

    return user_responses


def delete_user_answers(db: Session, user_id: int) -> bool:
    """
    Deletes all answers associated with a specific user.

    :param db: Database session.
    :param user_id: ID of the user whose answers are to be deleted.
    :return: True if any rows were deleted, otherwise False.
    """
    rows_deleted = db.query(Models_UserAnswer).filter(
        Models_UserAnswer.user_id == user_id
    ).delete(synchronize_session='fetch')
    db.commit()

    return rows_deleted > 0
