from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models import CompanyAnswer as Models_CompanyAnswer, AnswerOption, QuestionnaireType
from models import Question as Models_Question
from schemas.question_schema import QuestionType
from schemas.user_answer_schema import AnswerSubmission, QuestionWithAnswers, AnswerDetail


def submit_company_answers(db: Session, internship_id: int, submissions: List[AnswerSubmission]):
    """
    Submit answers for a company's internship questionnaire.

    This function handles the submission of answers for company-related questionnaires. It ensures that each
    internship can only have one set of answers submitted by the company. If answers already exist, an exception is raised.

    Parameters:
    - db: Database session.
    - internship_id: ID of the internship for which the answers are submitted.
    - submissions: List of AnswerSubmission objects containing the submitted answers.

    Raises:
    - HTTPException: If answers have already been submitted, if the question is not found,
      if the question is not a company question, or if invalid answer option IDs are provided.
    """
    # Check if answers already exist for the given internship
    existing_answers = db.query(Models_CompanyAnswer).filter(
        Models_CompanyAnswer.internship_id == internship_id).first()
    if existing_answers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Company has already submitted answers for this internship.")

    for submission in submissions:
        # Retrieve the question by its ID
        question = db.query(Models_Question).filter(Models_Question.id == submission.question_id).first()
        if not question:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Question with ID {submission.question_id} not found.")

        # Ensure the question is meant for company questionnaires
        if question.question_questionnaire != QuestionnaireType.COMPANY:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Question with ID {submission.question_id} is not a company question.")

        # Validate the provided answer option IDs
        valid_option_ids = {option.id for option in question.answer_options}
        invalid_option_ids = set(submission.answer_option_ids or []) - valid_option_ids
        if invalid_option_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid answer option IDs {list(invalid_option_ids)} for question ID {submission.question_id}.")

        # Delete any existing answers for the given question and internship
        db.query(Models_CompanyAnswer).filter(Models_CompanyAnswer.internship_id == internship_id,
                                              Models_CompanyAnswer.question_id == submission.question_id).delete(
            synchronize_session='fetch')
        db.flush()

        # Ensure that questions that do not support multiple answers receive only one answer
        if not question.supports_multiple_answers and submission.answer_option_ids and len(
                submission.answer_option_ids) > 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="This question does not support multiple answers.")

        # Handle free text answers
        if question.question_type == QuestionType.free_text and submission.answer_text:
            db.add(Models_CompanyAnswer(internship_id=internship_id, question_id=submission.question_id,
                                        answer_text=submission.answer_text))

        # Handle multiple choice with text answers
        if question.question_type == QuestionType.multiple_choice_with_text:
            other_option_id = next((option.id for option in question.answer_options if option.option_text == "Άλλο"),
                                   None)
            if other_option_id and other_option_id in submission.answer_option_ids:
                db.add(Models_CompanyAnswer(internship_id=internship_id, question_id=submission.question_id,
                                            answer_option_id=other_option_id, answer_text=submission.answer_text))
                submission.answer_option_ids.remove(other_option_id)

        # Handle multiple choice answers
        if submission.answer_option_ids:
            for option_id in submission.answer_option_ids:
                db.add(Models_CompanyAnswer(internship_id=internship_id, question_id=submission.question_id,
                                            answer_option_id=option_id, answer_text=None))
        db.commit()


def get_question_with_company_answers(db: Session, internship_id: int) -> List[QuestionWithAnswers]:
    """
    Retrieve all questions along with the company's answers for a given internship.

    This function fetches all questions and the answers provided by the company for the specified internship.

    Parameters:
    - db: Database session.
    - internship_id: ID of the internship for which the answers are retrieved.

    Returns:
    - List[QuestionWithAnswers]: A list of questions with the company's answers.
    """
    company_responses = []

    # Retrieve all questions
    detailed_questions = db.query(Models_Question).all()

    for question in detailed_questions:
        # Retrieve answers for the current question and internship
        company_answers = db.query(Models_CompanyAnswer).filter_by(internship_id=internship_id,
                                                                   question_id=question.id).all()
        if company_answers:
            # Create a detailed response for each question
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
                    ) for ans in company_answers
                ]
            )
            company_responses.append(question_detail)

    return company_responses


def delete_company_answers(db: Session, internship_id: int) -> bool:
    """
     Deletes all answers associated with a specific company for an internship.

     :param db: Database session.
     :param internship_id: ID of the internship whose company answers are to be deleted.
     :return: True if any rows were deleted, otherwise False.
     """
    rows_deleted = db.query(Models_CompanyAnswer).filter(
        Models_CompanyAnswer.internship_id == internship_id
    ).delete(synchronize_session='fetch')
    db.commit()

    return rows_deleted > 0
