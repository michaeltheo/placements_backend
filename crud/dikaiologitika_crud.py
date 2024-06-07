from datetime import datetime
from typing import Optional, List, Type

import pytz
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.constants import INTERNSHIP_PROGRAM_REQUIREMENTS
from models import Dikaiologitika, DikaiologitikaType, InternshipProgram, SubmissionTime
from schemas.dikaiologitika_schema import DikaiologitikaCreate


def determine_submission_time(internship_program: InternshipProgram,
                              dikaiologitika_type: DikaiologitikaType) -> SubmissionTime:
    # Retrieve the list of requirements for the specified internship program
    requirements = INTERNSHIP_PROGRAM_REQUIREMENTS.get(internship_program, [])

    # Initialize variables to store the submission times if found
    end_submission_time = None
    start_submission_time = None

    # Iterate through the requirements for the given internship program
    for requirement in requirements:
        # Check if the requirement type matches the provided dikaiologitika type
        if requirement['type'] == dikaiologitika_type.value:
            # If the submission time is END, store it in end_submission_time
            if requirement['submission_time'] == SubmissionTime.END.value:
                end_submission_time = SubmissionTime(requirement['submission_time'])
            # If the submission time is START, store it in start_submission_time
            elif requirement['submission_time'] == SubmissionTime.START.value:
                start_submission_time = SubmissionTime(requirement['submission_time'])

    # Raise an error if no matching submission time is found
    if end_submission_time:
        return end_submission_time
    if start_submission_time:
        return start_submission_time

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Submission time not found for type {dikaiologitika_type.value} in program {internship_program.value}")


def create_dikaiologitika(db: Session, dikaiologitika: DikaiologitikaCreate, user_id: int,
                          file_path: str, file_name: str, internship_program: InternshipProgram) -> Dikaiologitika:
    """
    Creates a new document (dikaiologitika) record in the database.

    Parameters:
    - db (Session): The database session.
    - dikaiologitika (DikaiologitikaCreate): The document data to be saved.
    - user_id (int): The ID of the user the document belongs to.
    - file_path (str): The file path where the document is stored.
    - file_name (str): The name of the file.
    - internship_program (InternshipProgram): The internship program the document is related to.

    Returns:
    - Dikaiologitika: The created document record.
    """
    if dikaiologitika.submission_time is None:
        dikaiologitika.submission_time = determine_submission_time(internship_program, dikaiologitika.type)

    utc_now = datetime.utcnow()
    utc_now = utc_now.replace(tzinfo=pytz.utc)  # Make the datetime timezone-aware in UTC
    local_tz = pytz.timezone('Europe/Athens')  # For Greece
    local_time = utc_now.astimezone(local_tz)  # Convert to local timezone

    db_dikaiologitika = Dikaiologitika(
        user_id=user_id,
        file_path=file_path,
        date=local_time,
        type=dikaiologitika.type,
        submission_time=dikaiologitika.submission_time,  # Add submission time here
        file_name=file_name
    )
    db.add(db_dikaiologitika)
    db.commit()
    db.refresh(db_dikaiologitika)
    return db_dikaiologitika


def get_files_by_user_id(db: Session, user_id: int, file_id: Optional[int] = None,
                         file_type: Optional[DikaiologitikaType] = None) -> list[Type[Dikaiologitika]]:
    """
    Retrieves documents based on the user ID, and optionally by document ID and type.

    Parameters:
    - db (Session): The database session.
    - user_id (int): The ID of the user.
    - file_id (Optional[int]): Optional specific document ID to filter by.
    - file_type (Optional[DikaiologitikaType]): Optional document type to filter by.

    Returns:
    - `List[Dikaiologitika]`: A list of document records matching the criteria.
    """
    query = db.query(Dikaiologitika).filter(Dikaiologitika.user_id == user_id)
    if file_type:
        query = query.filter(Dikaiologitika.type == file_type)
    if file_id:
        query = query.filter(Dikaiologitika.id == file_id)
    return query.all()


def get_all_files(db: Session, file_type: Optional[DikaiologitikaType] = None) -> List[Dikaiologitika]:
    """
    Retrieves all documents from the database, optionally filtered by document type.

    Parameters:
    - db (Session): The database session.
    - file_type (Optional[DikaiologitikaType]): Optional document type to filter by.

    Returns:
    - `List[Dikaiologitika]`: A list of all document records, possibly filtered by type.
    """
    query = db.query(Dikaiologitika)
    if file_type:
        query = query.filter(Dikaiologitika.type == file_type)
    return query.all()


def get_file_by_id(db: Session, file_id: int) -> Optional[Dikaiologitika]:
    """
    Retrieves a single document by its ID.

    Parameters:
    - db (Session): The database session.
    - file_id (int): The ID of the document to retrieve.

    Returns:
    - `Optional[Dikaiologitika]`: The document record if found, None otherwise.
    """
    return db.query(Dikaiologitika).filter(Dikaiologitika.id == file_id).first()


def update_file_path(db: Session, file_id: int, new_file_path: str, file_name: str) -> bool:
    """
    Updates the file path of an existing document.

    Parameters:
    - db (Session): The database session.
    - file_id (int): The ID of the document to update.
    - new_file_path (str): The new file path to set.

    Returns:
    - bool: True if the update was successful, False otherwise.
    """
    db_file = db.query(Dikaiologitika).filter(Dikaiologitika.id == file_id).first()
    utc_now = datetime.utcnow()
    utc_now = utc_now.replace(tzinfo=pytz.utc)  # Make the datetime timezone-aware in UTC
    local_tz = pytz.timezone('Europe/Athens')  # For Greece
    local_time = utc_now.astimezone(local_tz)  # Convert to local timezone
    if db_file:
        db_file.file_name = file_name
        db_file.file_path = new_file_path
        db_file.date = local_time
        db.commit()
        return True
    return False


def update_file(db: Session, file_id: int, user_id: int, update_data: dict) -> Optional[Dikaiologitika]:
    """
    Updates specified fields of a document.

    Parameters:
    - db (Session): The database session.
    - file_id (int): The ID of the document to update.
    - user_id (int): The ID of the user owning the document.
    - update_data (dict): A dictionary of fields to update.

    Returns:
    - `Optional[Dikaiologitika]`: The updated document record if found and updated, None otherwise.
    """
    db_file = db.query(Dikaiologitika).filter(Dikaiologitika.id == file_id, Dikaiologitika.user_id == user_id).first()
    if db_file is None:
        return None

    for key, value in update_data.items():
        if key == "type":
            value = DikaiologitikaType[value.upper()] if isinstance(value, str) else value
        setattr(db_file, key, value)

    db.commit()
    db.refresh(db_file)
    return db_file


def delete_file(db: Session, file_id: int, user_id: int) -> bool:
    """
    Deletes a document from the database.

    Parameters:
    - db (Session): The database session.
    - file_id (int): The ID of the document to delete.
    - user_id (int): The ID of the user owning the document.

    Returns:
    - bool: True if the document was successfully deleted, False if the document was not found.
    """
    db_file = db.query(Dikaiologitika).filter(Dikaiologitika.id == file_id, Dikaiologitika.user_id == user_id).first()
    if db_file is None:
        return False
    db.delete(db_file)
    db.commit()
    return True
