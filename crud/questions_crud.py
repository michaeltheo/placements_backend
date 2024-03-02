from typing import Type

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Question, AnswerOption, UserAnswer
from schemas.question_schema import QuestionCreate


# Assuming you're creating a Question along with AnswerOptions
def create_question_db(db: Session, question_data: QuestionCreate) -> Question:
    # Create the Question instance
    db_question = Question(question_text=question_data.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    # If there are answer options, create and associate AnswerOption instances
    if question_data.answer_options:
        for answer_option_data in question_data.answer_options:
            db_answer_option = AnswerOption(
                option_text=answer_option_data.option_text,
                question_id=db_question.id  # Associate with the newly created question
            )
            db.add(db_answer_option)
        db.commit()  # Commit the new AnswerOption instances to the database

    db.refresh(db_question)  # Refresh to load the created answer options into the db_question instance
    return db_question


def update_question(db: Session, question_id: int, question: QuestionCreate) -> Question or None:
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if question.question_text is not None:
        db_question.question_text = question.question_text

    if question.answer_options is not None:
        db.query(AnswerOption).filter(AnswerOption.question_id == question_id).delete()

        for answer_options_data in question.answer_options:
            db_answer_option = AnswerOption(
                option_text=answer_options_data.option_text,
                question_id=db_question.id
            )
            db.add(db_answer_option)
    db.commit()
    db.refresh(db_question)
    return db_question


def delete_question(db: Session, question_id: int):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()


def get_questions(db: Session) -> list[Type[Question]]:
    return db.query(Question).all()


def get_question_by_id(db: Session, question_id: int) -> Type[Question] | None:
    return db.query(Question).filter(Question.id == question_id).first()


def get_detailed_question_statistics(db: Session):
    stats = db.query(
        Question.id.label('question_id'),
        Question.question_text.label('question_text'),
        AnswerOption.id.label('answer_id'),
        AnswerOption.option_text.label('answer_text'),
        func.count(UserAnswer.id).label('count')
    ).join(AnswerOption, Question.id == AnswerOption.question_id) \
        .outerjoin(UserAnswer, AnswerOption.id == UserAnswer.answer_option_id) \
        .group_by(Question.id, AnswerOption.id) \
        .order_by(Question.id, AnswerOption.id) \
        .all()

    return stats
