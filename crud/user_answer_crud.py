from sqlalchemy.orm import Session

from models import UserAnswer, AnswerOption, Question


def create_or_update_user_answer(db: Session, user_id: int, question_id: int, answer_option_id: int):
    # Attempt to fetch the corresponding option_text
    answer_option = db.query(AnswerOption).filter(AnswerOption.id == answer_option_id).first()
    if not answer_option:
        raise ValueError(f"Invalid answer_option_id: {answer_option_id}")

    answer_text = answer_option.option_text

    # Check if an answer already exists to update or create a new one
    answer = db.query(UserAnswer).filter(
        UserAnswer.user_id == user_id,
        UserAnswer.question_id == question_id
    ).first()

    if answer:
        answer.answer_option_id = answer_option_id
        answer.answer_text = answer_text
    else:
        answer = UserAnswer(
            user_id=user_id,
            question_id=question_id,
            answer_option_id=answer_option_id,
            answer_text=answer_text
        )
        db.add(answer)

    db.commit()
    return answer


def get_user_answers(db: Session, user_id: int):
    return db.query(UserAnswer).filter_by(user_id=user_id).all()


def get_user_answers_with_question_text(db: Session, user_id: int):
    return db.query(UserAnswer, Question.question_text).join(Question, UserAnswer.question_id == Question.id).filter(
        UserAnswer.user_id == user_id).all()


def get_user_answers_with_details(db: Session, user_id: int):
    return db.query(UserAnswer, Question, AnswerOption) \
        .join(Question, UserAnswer.question_id == Question.id) \
        .join(AnswerOption, UserAnswer.answer_option_id == AnswerOption.id) \
        .filter(UserAnswer.user_id == user_id) \
        .all()
