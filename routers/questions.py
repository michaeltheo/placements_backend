from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from crud.questions_crud import create_question_db, get_questions, update_question, delete_question, \
    get_questions_statistics
from crud.user_crud import is_admin
from dependencies import get_db, get_current_user
from models import Users, Question
from schemas.question_schema import Question, QuestionCreate, QuestionUpdate, QuestionType, QuestionnaireType
from schemas.question_statistics import QuestionStatistics
from schemas.response import ResponseWrapper, Message

router = APIRouter(prefix='/question', tags=['question'])


@router.get('/types', response_model=ResponseWrapper[List[str]], status_code=status.HTTP_200_OK)
async def get_questions_types_endpoint(
):
    """
    Fetches and returns a list of all possible question types.

    Returns:
        A list of question type values wrapped in a `ResponseWrapper` with a success message.
    """
    question_list = [e.value for e in QuestionType]
    return ResponseWrapper(data=question_list, message=Message(detail="Λίστα όλων των τύπων ερωτήσεων"))


@router.post("/", response_model=ResponseWrapper[List[Question]], status_code=status.HTTP_200_OK)
async def admin_create_questions_endpoint(
        questions_data: List[QuestionCreate],
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
    Allows an admin to create multiple questions at once.

    Parameters:
    - questions_data: A list of question creation objects.
    - db: Database session dependency.
    - current_user: Current user dependency to check for admin privileges.

    Returns:
        A list of the created question objects wrapped in a `ResponseWrapper` with a success message.
    Raises:
        HTTPException if the current user is not an admin.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Ο χρήστης δεν είναι εξουσιοδοτημένος να εκτελέσει αυτήν την ενέργεια.")
    new_questions = []
    for question_data in questions_data:
        new_question = create_question_db(db, question_data)
        pydantic_question = Question.from_orm(new_question)
        new_questions.append(pydantic_question)

    return ResponseWrapper(data=new_questions, message=Message(detail="Οι ερωτήσεις δημιουργήθηκαν με επιτυχία."))


@router.get('/', response_model=ResponseWrapper[List[Question]], status_code=status.HTTP_200_OK)
def get_all_questions_endpoint(
        questionnaire_type: Optional[QuestionnaireType] = None,
        db: Session = Depends(get_db)
):
    """
    Retrieves all questions from the database, optionally filtering by questionnaire type.

    Parameters:
    - questionnaire_type: Optional parameter to filter questions by their questionnaire type.
    - db: Database session dependency.

    Returns:
        A list of all question objects wrapped in a `ResponseWrapper` with a success message.
    """
    db_questions = get_questions(db=db, questionnaire_type=questionnaire_type)
    return ResponseWrapper(data=db_questions, message=Message(detail="Οι ερωτήσεις ανακτήθηκαν με επιτυχία."))


@router.put('/{id}', response_model=ResponseWrapper[Question], status_code=status.HTTP_200_OK)
def admin_update_question_endpoint(
        question_id: int, question_update: QuestionUpdate, db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
    Allows an admin to update an existing question.

    Parameters:
    - question_id: The ID of the question to update.
    - question_update: Data object containing the question's updated information.
    - db: Database session dependency.
    - current_user: Current user dependency to check for admin privileges.

    Returns:
        The updated question object wrapped in a `ResponseWrapper` with a success message.
    Raises:
        HTTPException if the current user is not an admin or if the question cannot be updated (e.g., invalid updates for free text questions).
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Ο χρήστης δεν είναι εξουσιοδοτημένος να εκτελέσει αυτήν την ενέργεια.")
    if question_update.question_type == QuestionType.free_text and question_update.answer_options:
        if len(question_update.answer_options) > 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Οι ερωτήσεις ελεύθερου κειμένου δεν μπορούν να έχουν επιλογές απάντησης.")
    updated_question = update_question(db=db, question_id=question_id, question_update=question_update)
    if updated_question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Η ερώτηση δεν βρέθηκε.")
    return ResponseWrapper(data=updated_question,
                           message=Message(detail="Η ερώτηση ενημερώθηκε με επιτυχία"))


@router.delete('/{question_id}', response_model=Message, status_code=status.HTTP_200_OK)
async def admin_delete_question_endpoint(
        question_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
    Allows an admin to delete a question from the database.

    Parameters:
    - question_id: The ID of the question to delete.
    - db: Database session dependency.
    - current_user: Current user dependency to check for admin privileges.

    Returns:
        A success message if the question was deleted.
    Raises:
        HTTPException if the current user is not an admin or if the question does not exist or could not be deleted.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Ο χρήστης δεν είναι εξουσιοδοτημένος να εκτελέσει αυτήν την ενέργεια.")

    deletion_successful = delete_question(db=db, question_id=question_id)
    if not deletion_successful:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Η ερώτηση δεν βρέθηκε ή δεν ήταν δυνατή η διαγραφή της.")

    return Message(detail="Η ερώτηση διαγράφηκε")


@router.get('/stats/answers', response_model=ResponseWrapper[List[QuestionStatistics]], status_code=status.HTTP_200_OK)
async def admin_get_answers_statistics_endpoint(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user),
        questionnaire_type: QuestionnaireType = Query(...,
                                                      description="The type of questionnaire to filter statistics by")
):
    """
    Fetches and returns statistics for questions based on the questionnaire type, accessible only to admins.

    This endpoint compiles statistics for each question in the database, focusing on multiple choice and
    multiple choice with free text questions. For each question, it calculates how many times each option was selected
    and, for questions allowing free text responses, aggregates those responses as well.

    Parameters:
    - db (Session): Dependency injection of the database session, used for querying the database.
    - current_user (Users): The current user making the request, injected automatically. This is used to verify
                             admin privileges before providing access to sensitive statistical data.
    - questionnaire_type (QuestionnaireType): The type of questionnaire to filter statistics by.

    Returns:
    - ResponseWrapper[List[QuestionStatistics]]: A structured response that encapsulates the compiled statistics
                                                  within a `ResponseWrapper`, alongside a generic message.
                                                  The data field contains a list, where each item is a
                                                  `QuestionStatistics` object detailing the statistics for a single question.

    Raises:
    - HTTPException: If the current user is not an admin, an HTTP 403 Forbidden error is raised, restricting access
                     to this endpoint to admin users only.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Ο χρήστης δεν είναι εξουσιοδοτημένος να εκτελέσει αυτήν την ενέργεια.")
    stats_list = get_questions_statistics(db=db, questionnaire_type=questionnaire_type)
    return ResponseWrapper(data=stats_list, message=Message(detail="Τα στατιστικά ανακτήθηκαν με επιτυχία"))
