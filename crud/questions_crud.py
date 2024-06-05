from typing import List, Dict, Union, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette import status

from models import Question as Models_Question, AnswerOption as Models_Answer_Option, UserAnswer as Models_UserAnswer
from schemas.question_schema import QuestionCreate, QuestionType, QuestionUpdate, QuestionnaireType


def create_question_db(db: Session, question_data: QuestionCreate) -> Models_Question:
    """
    Create a new question in the database.

    Parameters:
        db (Session): The database session used for the operation.
        question_data (QuestionCreate): The schema object containing data for the new question.

    Returns:
        Models_Question: The newly created question object.

    Raises:
        HTTPException: If the question type requires answer options but none are provided.
    """
    if question_data.question_type in [QuestionType.multiple_choice,
                                       QuestionType.multiple_choice_with_text] and not question_data.answer_options:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Για τις ερωτήσεις πολλαπλής επιλογής απαιτείται μία απο τις επιλογές απάντησης.")

    db_question = Models_Question(
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        question_questionnaire=question_data.question_questionnaire,
        supports_multiple_answers=question_data.supports_multiple_answers
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    if question_data.answer_options and question_data.question_type != QuestionType.free_text:
        for option_data in question_data.answer_options:
            db_option = Models_Answer_Option(
                option_text=option_data.option_text,
                question_id=db_question.id
            )
            db.add(db_option)
        db.commit()
        db.refresh(db_option)

    return db_question


def get_questions(db: Session, questionnaire_type: Optional[QuestionnaireType] = None) -> List[Models_Question]:
    """
    Get all questions from the database, optionally filtering by questionnaire type.

    Parameters:
        db (Session): The database session used for the operation.
        questionnaire_type (Optional[QuestionnaireType]): The type of questionnaire to filter by (optional).

    Returns:
        List[Models_Question]: A list of all questions, optionally filtered by the questionnaire type.
    """
    query = db.query(Models_Question)
    if questionnaire_type:
        query = query.filter(Models_Question.question_questionnaire == questionnaire_type)
    return query.all()


def update_question(db: Session, question_id: int, question_update: QuestionUpdate) -> Union[Models_Question, None]:
    """
    Update an existing question in the database.

    Parameters:
        db (Session): The database session used for the operation.
        question_id (int): The ID of the question to update.
        question_update (QuestionUpdate): The schema object containing updated data for the question.

    Returns:
        Union[Models_Question, None]: The updated question object if found, otherwise None.

    Raises:
        ValueError: If attempting to add answer options to a free text question.
    """
    db_question = db.query(Models_Question).filter(Models_Question.id == question_id).first()
    if not db_question:
        return None

    if db_question.question_type == QuestionType.free_text and question_update.answer_options is not None:
        if len(question_update.answer_options) > 0:
            raise ValueError("Free text questions should not have answer options.")

    if question_update.question_text is not None:
        db_question.question_text = question_update.question_text
    if question_update.question_type is not None:
        db_question.question_type = question_update.question_type
    if question_update.question_questionnaire is not None:
        db_question.question_questionnaire = question_update.question_questionnaire
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
        db (Session): The database session used for the operation.
        question_id (int): The ID of the question to fetch.

    Returns:
        Union[Models_Question, None]: The question instance if found, or None otherwise.
    """
    return db.query(Models_Question).filter(Models_Question.id == question_id).first()


def delete_question(db: Session, question_id: int) -> bool:
    """
    Delete a question from the database.

    Parameters:
        db (Session): The database session used for the operation.
        question_id (int): The ID of the question to delete.

    Returns:
        bool: True if the question was successfully deleted, False otherwise.
    """
    db_question = db.query(Models_Question).filter(Models_Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False


def get_questions_statistics(db: Session, questionnaire_type: QuestionnaireType) -> List[Dict]:
    """
    Retrieve statistics for each question from the database, filtered by the questionnaire type.

    Parameters:
        db (Session): The database session used for the operation.
        questionnaire_type (QuestionnaireType): The type of questionnaire to filter questions by.

    Returns:
        List[Dict]: A list of dictionaries containing question statistics.
    """
    questions = db.query(Models_Question).filter(
        Models_Question.question_type.in_([QuestionType.multiple_choice, QuestionType.multiple_choice_with_text]),
        Models_Question.question_questionnaire == questionnaire_type
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
