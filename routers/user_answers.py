from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from crud.user_answer_crud import submit_user_answers, get_question_with_user_answers, delete_user_answers
from crud.user_crud import is_admin
from dependencies import get_db, get_current_user
from models import Users
from schemas.response import Message, ResponseWrapper
from schemas.user_answer_schema import AnswerSubmission, QuestionWithAnswers

router = APIRouter(prefix='/user_answers', tags=['user answers'])


@router.post("/submit-answers/", response_model=Message, status_code=status.HTTP_200_OK)
def submit_answers_endpoint(submissions: List[AnswerSubmission], db: Session = Depends(get_db),
                            current_user: Users = Depends(get_current_user)):
    """
    Submit answers for a user.

    This endpoint allows users to submit answers to questions. It accepts a list of answer submissions, each containing
    the question ID and the selected answer(s). If the user is submitting answers to a question that supports multiple
    answers, multiple answer IDs can be provided.

    Parameters:
    - submissions (List[AnswerSubmission]): A list of submissions, each containing a question ID and answer IDs.
    - db (Session): Dependency injection of the database session.
    - current_user (Users): The current user making the request. Used to verify that the user_id matches the current user's ID.

    Returns:
    - Message: A success message indicating that the answers were submitted successfully.

    Raises:
    - HTTPException: If the current_user's ID does not match the user_id, indicating an attempt to submit answers for another user.
    """
    submit_user_answers(db, current_user.id, submissions)
    return Message(detail='Οι απαντήσεις υποβλήθηκαν με επιτυχία.')


@router.get("/{user_id}", response_model=ResponseWrapper[List[QuestionWithAnswers]])
async def get_user_responses_endpoint(user_id: int, db: Session = Depends(get_db),
                                      current_user: Users = Depends(get_current_user)):
    """
    Get all responses for a given user.

    This endpoint retrieves all the questions along with the user's answers. It's designed to ensure that users can only
    access their own responses unless they're an admin, in which case they can access responses of any user.

    Parameters:
    - user_id (int): The ID of the user whose responses are being requested.
    - db (Session): Dependency injection of the database session.
    - current_user (Users): The current user making the request, injected automatically.

    Returns:
    - ResponseWrapper[List[QuestionWithAnswers]]: A wrapper containing the list of questions with the user's answers and a success message.
    """
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Η πρόσβαση περιορίζεται στις δικές σας απαντήσεις ή στον διαχειριστή.")
    user_responses = get_question_with_user_answers(db, user_id)
    return ResponseWrapper(data=user_responses, message=Message(detail="Οι απαντήσεις ανακτήθηκαν με επιτυχία."))


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_answers_endpoint(user_id: int, db: Session = Depends(get_db),
                                  current_user: Users = Depends(get_current_user)):
    """
    Delete all answers submitted by a user.

    This endpoint allows for the deletion of all answers submitted by a specified user. It checks if the current user
    is either the user whose answers are to be deleted or an admin. If not, it restricts the action.

    Parameters:
    - user_id (int): The ID of the user whose answers are to be deleted.
    - db (Session): Dependency injection of the database session.
    - current_user (Users): The current user making the request, injected automatically.

    Returns:
    - Message: a message indicating the outcome of the deletion process.
    """
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Η διαγραφή περιορίζεται στις δικές σας απαντήσεις ή στον διαχειριστή.")
    deletion_successful = delete_user_answers(db, user_id)
    if deletion_successful:
        return Message(
            detail=f"Όλες οι απαντήσεις του χρήστη έχουν διαγραφεί.")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκαν απαντήσεις για διαγραφή ή δεν ήταν δυνατή η διαγραφή."
        )
