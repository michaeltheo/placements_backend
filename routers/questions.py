from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from crud.questions_crud import create_question_db, get_questions, update_question, get_question_by_id, delete_question, \
    get_detailed_question_statistics
from crud.user_crud import is_admin
from dependencies import get_db, get_current_user
from models import Users
from schemas.question_schema import Question, QuestionUpdate, QuestionCreate
from schemas.question_statistics import QuestionStatistics, AnswerStatistics
from schemas.response import ResponseWrapper, Message

router = APIRouter(prefix='/question', tags=['question'])


@router.post("/", response_model=ResponseWrapper[List[Question]], status_code=status.HTTP_200_OK)
async def admin_create_questions(
        questions_data: List[QuestionCreate],
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin ONLY")

    new_questions = []
    for question_data in questions_data:
        new_question = create_question_db(db, question_data)
        new_questions.append(new_question)

    return ResponseWrapper(data=new_questions, message=Message(detail="Questions created"))


@router.put('/{question_id}', response_model=ResponseWrapper[Question], status_code=status.HTTP_200_OK)
async def admin_update_question_endpoint(
        question_id: int,
        question_update: QuestionUpdate,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin ONLY")

        # //TODO: Change ta detail
    question_exists = get_question_by_id(db=db, question_id=question_id)

    if not question_exists:
        raise HTTPException(status_code=404, detail="Question not found")
    updated_question = update_question(db=db, question_id=question_id, question=question_update)

    if not updated_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return ResponseWrapper(data=updated_question, message=Message(detail="Question updated"))


@router.delete('/{question_id}', response_model=ResponseWrapper, status_code=status.HTTP_200_OK)
async def admin_delete_question_endpoint(
        question_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin ONLY")

        # //TODO: Change ta detail

    question_exists = get_question_by_id(db=db, question_id=question_id)

    if not question_exists:
        raise HTTPException(status_code=404, detail="Question not found")

    delete_question(db=db, question_id=question_id)
    return ResponseWrapper(data=[], message=Message(detail="Question deleted"))


@router.get("/", response_model=ResponseWrapper[List[Question]], status_code=status.HTTP_200_OK)
async def get_all_questions_endpoint(db: Session = Depends(get_db)):
    questions = get_questions(db=db)
    return ResponseWrapper(data=questions, message=Message(detail="Questions retrieved successfully"))


@router.get('/statistics/detailed', response_model=ResponseWrapper[List[QuestionStatistics]])
async def get_detailed_questions_statistics(db: Session = Depends(get_db)):
    raw_stats = get_detailed_question_statistics(db)

    detailed_stats = {}
    for stat in raw_stats:
        if stat.question_id not in detailed_stats:
            detailed_stats[stat.question_id] = QuestionStatistics(
                question_id=stat.question_id,
                question_text=stat.question_text,
                answers=[]
            )
        detailed_stats[stat.question_id].answers.append(AnswerStatistics(
            answer_id=stat.answer_id,
            answer_text=stat.answer_text,
            count=stat.count
        ))

    statistics_models = list(detailed_stats.values())

    return ResponseWrapper(data=statistics_models,
                           message=Message(detail="Detailed question statistics fetched successfully"))
