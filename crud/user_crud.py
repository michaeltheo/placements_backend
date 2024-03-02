from sqlalchemy.orm import Session

from models import Users


def get_user_by_AM(db: Session, AM: str):
    return db.query(Users).filter(Users.AM == AM).first()


def get_user_by_id(db: Session, ID: int):
    return db.query(Users).filter(
        Users.id == ID).first()


def create_user(db: Session, user: dict):
    db_user = Users(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def is_admin(user: Users) -> bool:
    return user.role == 'admin'
