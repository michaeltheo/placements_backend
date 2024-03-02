from datetime import datetime
from typing import Type, Optional

from sqlalchemy.orm import Session

from models import Dikaiologitika
from schemas.dikaiologitika_schema import DikaiologitikaCreate


def create_dikaiologitika(db: Session, dikaiologitika: DikaiologitikaCreate, user_id: int, file_path: str):
    db_dikaiologitika = Dikaiologitika(
        user_id=user_id,
        file_path=file_path,
        date=datetime.utcnow(),
        type=dikaiologitika.type
    )
    db.add(db_dikaiologitika)
    db.commit()
    db.refresh(db_dikaiologitika)
    return db_dikaiologitika


def get_files_by_user_id(db: Session, user_id: int, file_id: Optional[int] = None, file_type: Optional[str] = None) -> \
        list[Type[Dikaiologitika]]:
    query = db.query(Dikaiologitika).filter(Dikaiologitika.user_id == user_id)
    if file_type:
        query = query.filter(Dikaiologitika.type == file_type and Dikaiologitika.id == user_id)
    if file_id:
        query = query.filter(Dikaiologitika.id == file_id)
    return query.all()


def get_all_files(db: Session, file_type: str = None):
    query = db.query(Dikaiologitika)
    if file_type:
        query = query.filter(Dikaiologitika.type == file_type)
    return query.all()


def get_file_by_id(db: Session, file_id: int):
    return db.query(Dikaiologitika).filter(Dikaiologitika.id == file_id).first()


def update_file_path(db: Session, file_id: int, new_file_path: str):
    db_file = db.query(Dikaiologitika).filter(Dikaiologitika.id == file_id).first()
    if db_file:
        db_file.file_path = new_file_path
        db.commit()
        return True
    return False


def update_file(db: Session, file_id: int, user_id: int, update_data: dict) -> Dikaiologitika or None:
    db_file = db.query(Dikaiologitika).filter(Dikaiologitika.id == file_id, Dikaiologitika.user_id == user_id).first()
    if db_file is None:
        return None
    for key, value in update_data.items():
        setattr(db_file, key, value)
    db.commit()
    db.refresh(db_file)
    return db_file


def delete_file(db: Session, file_id: int, user_id: int) -> bool:
    db_file = db.query(Dikaiologitika).filter(Dikaiologitika.id == file_id, Dikaiologitika.user_id == user_id).first()
    if db_file is None:
        return False
    db.delete(db_file)
    db.commit()
    return True
