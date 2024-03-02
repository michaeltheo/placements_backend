from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from crud.user_answer_crud import create_or_update_user_answer, get_user_answers_with_details
from dependencies import get_db, get_current_user
from models import Users, Question, AnswerOption, UserAnswer
from schemas.question_schema import QuestionWithAnswers, AnswerWithQuestion, QuestionModel
from schemas.response import ResponseWrapper, Message, DetailedUserAnswersResponse, DetailedUserAnswersResponseZ
from schemas.user_answer_schema import UserAnswerCreate
from schemas.user_answer_schema import UserAnswerModel, AnswerOptionModel

router = APIRouter(prefix='/user_answers', tags=['user answers'])


@router.post('/', response_model=ResponseWrapper[DetailedUserAnswersResponse], status_code=status.HTTP_200_OK)
async def submit_answers(
        answers_data: List[UserAnswerCreate],
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

    for answer_data in answers_data:
        create_or_update_user_answer(db=db, user_id=current_user.id, **answer_data.dict())

    user_answers = db.query(UserAnswer).filter(UserAnswer.user_id == current_user.id).join(Question).join(
        AnswerOption).all()

    questions_answers = []
    for user_answer in user_answers:
        question = db.query(Question).filter(Question.id == user_answer.question_id).first()
        answer = db.query(AnswerOption).filter(AnswerOption.id == user_answer.answer_option_id).first()

        question_with_answers = QuestionWithAnswers(
            id=question.id,
            text=question.question_text,
            answers=[answer]
        )

        answer_with_user = AnswerWithQuestion(
            question=question_with_answers,
        )

        questions_answers.append(answer_with_user)

    # Construct the final response
    response_data = DetailedUserAnswersResponse(
        questions_answers=questions_answers,
        user_details=current_user
    )

    return ResponseWrapper(data=response_data, message=Message(detail="Answers submitted successfully"))


@router.get('/', response_model=ResponseWrapper[DetailedUserAnswersResponseZ],
            status_code=status.HTTP_200_OK)
async def get_detailed_user_answers_endpoint(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

    user_answers_details = get_user_answers_with_details(db, current_user.id)
    print(user_answers_details)
    detailed_answers = []
    for user_answer, question, selected_answer in user_answers_details:
        question_model = QuestionModel(
            id=question.id,
            question_text=question.question_text
        )
        question_model.selected_answer = AnswerOptionModel.from_orm(selected_answer)

        user_answer_model = UserAnswerModel(question_details=question_model)
        detailed_answers.append(user_answer_model)

    response_data = DetailedUserAnswersResponseZ(
        questions_answers=detailed_answers,
        user_details=current_user
    )
    return ResponseWrapper(data=response_data, message=Message(detail="Detailed user answers fetched successfully"))
