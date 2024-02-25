from sqlalchemy.orm import Session

import models


def get_user_by_AM(db: Session, AM: str):
    return db.query(models.Users).filter(models.Users.AM == AM).first()


def get_user_by_id(db: Session, ID: int):
    return db.query(models.Users).filter(models.Users.id == ID).first()


def create_user(db: Session, user: dict):
    db_user = models.Users(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
