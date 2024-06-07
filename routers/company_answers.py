from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from jose import JWTError
from sqlalchemy.orm import Session
from starlette import status

from core.auth import verify_jwt
from crud.company_answer_crud import submit_company_answers, get_question_with_company_answers, delete_company_answers
from crud.user_crud import is_admin
from dependencies import get_db, get_current_user
from models import Users
from schemas.response import Message, ResponseWrapper
from schemas.user_answer_schema import AnswerSubmission, QuestionWithAnswers

router = APIRouter(prefix='/company_answers', tags=['company answers'])


@router.post("/submit-answers/{internship_id}", response_model=Message, status_code=status.HTTP_200_OK)
def submit_company_answers_endpoint(submissions: List[AnswerSubmission], internship_id: int,
                                    db: Session = Depends(get_db), token: str = Header(...)):
    """
    Submit answers for a company's questionnaire.

    This endpoint allows companies to submit answers to questions related to a specific internship. It requires a valid
    JWT token for authentication.

    Parameters:
    - submissions (List[AnswerSubmission]): A list of answer submissions.
    - internship_id (int): The ID of the internship for which answers are submitted.
    - db (Session): Dependency injection for the database session.
    - token (str): JWT token passed in the request header for authentication.

    Returns:
    - Message: A success message indicating that the answers were submitted successfully.

    Raises:
    - HTTPException: If the token is invalid or expired.
    """
    try:
        # Verify the provided JWT token
        payload = verify_jwt(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Μη έγκυρο ή ληγμένο token. Παρακαλώ εισάγετε νέο κωδικό OTP.")

    # Token is verified, proceed with submitting company answers
    submit_company_answers(db, internship_id, submissions)
    return Message(detail='Οι απαντήσεις της εταιρείας υποβλήθηκαν με επιτυχία.')


@router.get("/{internship_id}", response_model=ResponseWrapper[List[QuestionWithAnswers]])
async def get_company_responses_endpoint(internship_id: int, db: Session = Depends(get_db),
                                         current_user: Users = Depends(get_current_user)):
    """
    Get all responses submitted by a company for a specific internship.

    This endpoint retrieves all the questions along with the company's answers for a specific internship.

    Parameters:
    - internship_id (int): The ID of the internship whose responses are being requested.
    - db (Session): Dependency injection for the database session.
    - current_user (Users): The current user making the request, injected automatically.

    Returns:
    - ResponseWrapper[List[QuestionWithAnswers]]: A wrapper containing the list of questions with the company's answers and a success message.
    """
    company_responses = get_question_with_company_answers(db, internship_id)
    return ResponseWrapper(data=company_responses,
                           message=Message(detail="Οι απαντήσεις της εταιρείας ανακτήθηκαν με επιτυχία."))


@router.delete("/{internship_id}", status_code=status.HTTP_200_OK)
async def delete_company_answers_endpoint(internship_id: int, db: Session = Depends(get_db),
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
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Η διαγραφή περιορίζεται στις δικές σας απαντήσεις ή στον διαχειριστή.")
    deletion_successful = delete_company_answers(db, internship_id)
    if deletion_successful:
        return Message(
            detail=f"Όλες οι απαντήσεις της εταιρείας έχουν διαγραφεί.")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκαν απαντήσεις για διαγραφή ή δεν ήταν δυνατή η διαγραφή."
        )
