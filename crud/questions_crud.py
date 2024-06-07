from typing import List, Dict, Union, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette import status

from models import Question as Models_Question, AnswerOption as Models_Answer_Option, UserAnswer as Models_UserAnswer, \
    CompanyAnswer as Models_CompanyAnswers
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
        if questionnaire_type == QuestionnaireType.STUDENT:
            stats = get_student_question_statistics(db, question)
        elif questionnaire_type == QuestionnaireType.COMPANY:
            stats = get_company_question_statistics(db, question)
        stats_list.append(stats)

    return stats_list


def get_student_question_statistics(db: Session, question: Models_Question) -> Dict:
    """
    Fetch statistics for student questionnaire questions.

    Parameters:
        db (Session): The database session used for the operation.
        question (Models_Question): The question for which statistics are being fetched.

    Returns:
        Dict: A dictionary containing the statistics for the question.
    """
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

    statistics_dict, other_option_details = process_option_counts(option_counts)

    all_options = db.query(Models_Answer_Option).filter(
        Models_Answer_Option.question_id == question.id
    ).all()
    update_statistics_with_all_options(statistics_dict, all_options)

    statistics = list(statistics_dict.values())

    free_text_responses = []
    if question.question_type == QuestionType.multiple_choice_with_text and other_option_details:
        free_text_responses, other_option_details = process_free_text_answers(db, question, other_option_details,
                                                                              Models_UserAnswer)
        statistics_dict[other_option_details['option_id']] = other_option_details

    total_responses = sum(stat['count'] for stat in statistics_dict.values())

    return {
        'question_id': question.id,
        'question_text': question.question_text,
        'statistics': statistics,
        'free_text_responses_count': len(free_text_responses),
        'free_text_responses': free_text_responses,
        'total_responses': total_responses
    }


def get_company_question_statistics(db: Session, question: Models_Question) -> Dict:
    """
    Fetch statistics for company questionnaire questions.

    Parameters:
        db (Session): The database session used for the operation.
        question (Models_Question): The question for which statistics are being fetched.

    Returns:
        Dict: A dictionary containing the statistics for the question.
    """
    option_counts = db.query(
        Models_CompanyAnswers.answer_option_id,
        Models_Answer_Option.option_text,
        func.count(Models_CompanyAnswers.answer_option_id).label('count')
    ).join(
        Models_Answer_Option, Models_Answer_Option.id == Models_CompanyAnswers.answer_option_id
    ).filter(
        Models_CompanyAnswers.question_id == question.id
    ).group_by(
        Models_CompanyAnswers.answer_option_id, Models_Answer_Option.option_text
    ).all()

    statistics_dict, other_option_details = process_option_counts(option_counts)

    all_options = db.query(Models_Answer_Option).filter(
        Models_Answer_Option.question_id == question.id
    ).all()
    update_statistics_with_all_options(statistics_dict, all_options)

    statistics = list(statistics_dict.values())

    free_text_responses = []
    if question.question_type == QuestionType.multiple_choice_with_text and other_option_details:
        free_text_responses, other_option_details = process_free_text_answers(db, question, other_option_details,
                                                                              Models_CompanyAnswers)
        statistics_dict[other_option_details['option_id']] = other_option_details

    total_responses = sum(stat['count'] for stat in statistics_dict.values())

    return {
        'question_id': question.id,
        'question_text': question.question_text,
        'statistics': statistics,
        'free_text_responses_count': len(free_text_responses),
        'free_text_responses': free_text_responses,
        'total_responses': total_responses
    }


def process_option_counts(option_counts) -> (Dict, Dict):
    """
    Process option counts and identify 'Other' option details.

    Parameters:
        option_counts (List): The list of option counts from the database query.

    Returns:
        (Dict, Dict): A tuple containing the statistics dictionary and details of the 'Other' option.
    """
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
    return statistics_dict, other_option_details


def update_statistics_with_all_options(statistics_dict: Dict, all_options) -> None:
    """
    Ensure that all options for a question are included in the statistics dictionary.

    Parameters:
        statistics_dict (Dict): The dictionary containing current statistics.
        all_options (List): The list of all options for the question.

    Returns:
        None
    """
    for option in all_options:
        if option.id not in statistics_dict:
            statistics_dict[option.id] = {
                'option_id': option.id,
                'text': option.option_text,
                'count': 0
            }


def process_free_text_answers(db: Session, question: Models_Question, other_option_details: Dict, answer_model) -> (
        List[str], Dict):
    """
    Process free text answers for 'Other' option.

    Parameters:
        db (Session): The database session used for the operation.
        question (Models_Question): The question for which free text answers are being processed.
        other_option_details (Dict): Details of the 'Other' option.
        answer_model: The model class for the answer table (UserAnswer or CompanyAnswer).

    Returns:
        (List[str], Dict): A tuple containing the list of free text responses and updated 'Other' option details.
    """
    free_text_answers = db.query(answer_model.answer_text).filter(
        answer_model.question_id == question.id,
        answer_model.answer_option_id == other_option_details['option_id'],
        answer_model.answer_text.isnot(None)
    ).all()
    free_text_responses = [answer.answer_text for answer in free_text_answers]
    unique_responses = set(free_text_responses)
    other_option_details['count'] = len(unique_responses)
    return free_text_responses, other_option_details
