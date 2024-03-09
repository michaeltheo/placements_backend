from typing import Type, List

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Question as Models_Question, AnswerOption as Models_Answer_Option, UserAnswer as Models_UserAnswer
from schemas.question_schema import QuestionCreate, QuestionType, Question


def create_question_db(db: Session, question_data: QuestionCreate) -> Models_Question:
    if question_data.question_type in [QuestionType.multiple_choice,
                                       QuestionType.multiple_choice_with_text] and not question_data.answer_options:
        raise HTTPException(status_code=400, detail="Answer options are required for multiple choice questions.")
    db_question = Models_Question(
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        supports_multiple_answers=question_data.supports_multiple_answers
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    # If there are answer options and the question is not of type FREE_TEXT, associate them
    if question_data.answer_options and question_data.question_type != QuestionType.free_text:
        for option_data in question_data.answer_options:
            db_option = Models_Answer_Option(
                option_text=option_data.option_text,
                question_id=db_question.id
            )
            db.add(db_option)
        db.commit()
        # After committing, optionally refresh each option or the question to update ORM relationships
        db.refresh(db_option)

    return db_question


def get_questions(db: Session) -> list[Type[Question]]:
    return db.query(Models_Question).all()


def update_question(db: Session, question_id: int, question_update: QuestionCreate) -> Models_Question | None:
    """
        Updates an existing question in the database with new information.

        :param db: Database session.
        :param question_id: The ID of the question to update.
        :param question_update: New data to update the question with.
        :return: The updated question instance, or None if the question does not exist.

        Deletes old answer options and creates new ones if answer_options are provided in the update.
        Raises ValueError if attempting to add answer options to a free text question.
    """
    db_question = db.query(Models_Question).filter(Models_Question.id == question_id).first()
    if not db_question:
        return None
    # Check for "FREE_TEXT" question type and answer options
    if db_question.question_type == QuestionType.free_text and question_update.answer_options is not None:
        if len(question_update.answer_options) > 0:  # Ensure answer_options list is empty for FREE_TEXT questions
            raise ValueError("Free text questions should not have answer options.")
    if question_update.question_text is not None:
        db_question.question_text = question_update.question_text
    if question_update.question_type is not None:
        db_question.question_type = question_update.question_type
    if question_update.supports_multiple_answers is not None:
        db_question.supports_multiple_answers = question_update.supports_multiple_answers

    if question_update.answer_options is not None:
        db.query(Models_Answer_Option).filter(Models_Answer_Option.question_id == question_id).delete()
        for option_data in question_update.answer_options:
            new_option = Models_Answer_Option(
                question_id=question_id,
                option_text=option_data.option_text
            )
            db.add(new_option)
    db.commit()
    db.refresh(db_question)
    return db_question


def get_question_by_id(db: Session, question_id: int) -> Type[Question] | None:
    """
    Fetches a single question by its ID.

    :param db: Database session.
    :param question_id: The ID of the question to fetch.
    :return: The question instance if found, or None otherwise.
    """
    return db.query(Models_Question).filter(Models_Question.id == question_id).first()


def delete_question(db: Session, question_id: int) -> bool:
    """
    Deletes a question from the database.

    :param db: Database session.
    :param question_id: The ID of the question to delete.
    :return: True if the question was successfully deleted, False otherwise.
    """
    db_question = db.query(Models_Question).filter(Models_Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False


def get_questions_statistics(db: Session) -> List[dict]:
    questions = db.query(Models_Question).filter(
        Models_Question.question_type.in_([QuestionType.multiple_choice, QuestionType.multiple_choice_with_text])
    ).all()

    stats_list = []
    for question in questions:
        # Query to get option counts including "Other (Please specify)"
        option_counts = db.query(
            Models_UserAnswer.answer_option_id,
            Models_Answer_Option.option_text,
            func.count(Models_UserAnswer.answer_option_id).label('count')
        ).join(
            Models_Answer_Option, Models_Answer_Option.id == Models_UserAnswer.answer_option_id
        ).filter(
            Models_UserAnswer.question_id == question.id
        ).group_by(
            Models_UserAnswer.answer_option_id, Models_Answer_Option.option_text
        ).all()

        # Extract "Other" option details
        other_option_details = next(
            ({'option_id': oc.answer_option_id, 'text': oc.option_text, 'count': 0} for oc in option_counts if
             oc.option_text == "Other (Please specify)"), None)

        statistics = []
        for oc in option_counts:
            # Directly append predefined option counts
            if oc.option_text != "Other (Please specify)":
                statistics.append({
                    'option_id': oc.answer_option_id,
                    'text': oc.option_text,
                    'count': oc.count
                })

        free_text_responses = []
        if question.question_type == QuestionType.multiple_choice_with_text and other_option_details:
            # Fetch free text responses for "Other" option
            free_text_answers = db.query(Models_UserAnswer.answer_text).filter(
                Models_UserAnswer.question_id == question.id,
                Models_UserAnswer.answer_option_id == other_option_details['option_id'],
                Models_UserAnswer.answer_text.isnot(None)
            ).all()
            free_text_responses = [answer.answer_text for answer in free_text_answers]
            # Update "Other" option count to include free text responses
            other_option_details['count'] = len(free_text_responses)
            statistics.append(other_option_details)  # Append "Other" details with updated count

        total_responses = sum(stat['count'] for stat in statistics)

        stats_list.append({
            'question_id': question.id,
            'question_text': question.question_text,
            'statistics': statistics,
            'free_text_responses_count': len(free_text_responses),
            'free_text_responses': free_text_responses,
            'total_responses': total_responses
        })

    return stats_list
