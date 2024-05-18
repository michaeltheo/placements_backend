from typing import List, Dict, Union

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Question as Models_Question, AnswerOption as Models_Answer_Option, UserAnswer as Models_UserAnswer
from schemas.question_schema import QuestionCreate, QuestionType


def create_question_db(db: Session, question_data: QuestionCreate) -> Models_Question:
    """
    Create a new question in the database.

    Parameters:
    - db (Session): Database session.
    - question_data (QuestionCreate): Data for creating the question.

    Returns:
    - Models_Question: The created question instance.

    Raises:
    - HTTPException: If answer options are missing for multiple choice questions.
    """
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
        db.refresh(db_option)  # Optionally refresh each option or the question to update ORM relationships

    return db_question


def get_questions(db: Session) -> List[Models_Question]:
    """
    Get all questions from the database.

    Parameters:
    - db (Session): Database session.

    Returns:
    - List[Models_Question]: List of all questions.
    """
    return db.query(Models_Question).all()


def update_question(db: Session, question_id: int, question_update: QuestionCreate) -> Union[Models_Question, None]:
    """
    Update an existing question in the database with new information.

    Parameters:
    - db (Session): Database session.
    - question_id (int): The ID of the question to update.
    - question_update (QuestionCreate): New data to update the question with.

    Returns:
    - Models_Question: The updated question instance, or None if the question does not exist.

    Raises:
    - ValueError: If attempting to add answer options to a free text question.
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


def get_question_by_id(db: Session, question_id: int) -> Union[Models_Question, None]:
    """
    Fetch a single question by its ID.

    Parameters:
    - db (Session): Database session.
    - question_id (int): The ID of the question to fetch.

    Returns:
    - Models_Question: The question instance if found, or None otherwise.
    """
    return db.query(Models_Question).filter(Models_Question.id == question_id).first()


def delete_question(db: Session, question_id: int) -> bool:
    """
    Delete a question from the database.

    Parameters:
    - db (Session): Database session.
    - question_id (int): The ID of the question to delete.

    Returns:
    - bool: True if the question was successfully deleted, False otherwise.
    """
    db_question = db.query(Models_Question).filter(Models_Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False


def get_questions_statistics(db: Session) -> List[Dict]:
    """
    Retrieve statistics for each question from the database.

    Parameters:
    - db (Session): Database session.

    Returns:
    - List[Dict]: List of dictionaries containing question statistics.
    """
    questions = db.query(Models_Question).filter(
        Models_Question.question_type.in_([QuestionType.multiple_choice, QuestionType.multiple_choice_with_text])
    ).all()

    stats_list = []
    for question in questions:
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

        other_option_details = next(
            ({'option_id': oc.answer_option_id, 'text': oc.option_text, 'count': 0} for oc in option_counts if
             oc.option_text == "Άλλο"), None)

        statistics_dict = {}
        for oc in option_counts:
            if oc.answer_option_id in statistics_dict:
                statistics_dict[oc.answer_option_id]['count'] += oc.count
            else:
                statistics_dict[oc.answer_option_id] = {
                    'option_id': oc.answer_option_id,
                    'text': oc.option_text,
                    'count': oc.count
                }

        all_options = db.query(Models_Answer_Option).filter(
            Models_Answer_Option.question_id == question.id
        ).all()
        for option in all_options:
            if option.id not in statistics_dict:
                statistics_dict[option.id] = {
                    'option_id': option.id,
                    'text': option.option_text,
                    'count': 0
                }

        statistics = list(statistics_dict.values())

        free_text_responses = []
        if question.question_type == QuestionType.multiple_choice_with_text and other_option_details:
            free_text_answers = db.query(Models_UserAnswer.answer_text).filter(
                Models_UserAnswer.question_id == question.id,
                Models_UserAnswer.answer_option_id == other_option_details['option_id'],
                Models_UserAnswer.answer_text.isnot(None)
            ).all()
            free_text_responses = [answer.answer_text for answer in free_text_answers]
            unique_responses = set(free_text_responses)
            other_option_details['count'] = len(unique_responses)
            statistics_dict[other_option_details['option_id']] = other_option_details

        total_responses = sum(stat['count'] for stat in statistics_dict.values())

        stats_list.append({
            'question_id': question.id,
            'question_text': question.question_text,
            'statistics': statistics,
            'free_text_responses_count': len(free_text_responses),
            'free_text_responses': free_text_responses,
            'total_responses': total_responses
        })

    return stats_list
