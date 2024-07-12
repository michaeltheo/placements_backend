from typing import Optional, List, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.messages import Messages
from crud.company_answer_crud import delete_company_answers
from crud.company_crud import get_company
from crud.user_answer_crud import delete_user_answers
from crud.user_crud import get_user_by_id
from models import Internship as InternshipModel, InternshipProgram, InternshipStatus, Users, Companies, Dikaiologitika, \
    Department
from schemas.internship_schema import InternshipCreate, InternshipAllRead


def create_or_update_internship(db: Session, user_id: int, internship_data: InternshipCreate) -> InternshipModel:
    """
    Create a new internship or update an existing one for a given user.

    Parameters:
    - db (Session): Database session.
    - user_id (int): The ID of the user.
    - internship_data (InternshipCreate): The data for the internship.

    Returns:
    - InternshipModel: The created or updated internship.
    """
    # Update an existing internship (used for admins to add start date end date)
    if internship_data.id:
        # Find internship by internship_id
        existing_internship = db.query(InternshipModel).filter_by(id=internship_data.id).first()
        if not existing_internship:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.INTERNSHIP_NOT_FOUND)

        # Update existing internship
        existing_internship.company_id = internship_data.company_id
        existing_internship.department = internship_data.department
        existing_internship.program = internship_data.program
        existing_internship.start_date = internship_data.start_date
        existing_internship.end_date = internship_data.end_date
        db.commit()
        db.refresh(existing_internship)
        return existing_internship

    # Update internship by user (used from students to update their internship add company)
    existing_internship = get_user_internship(db, user_id)

    if existing_internship:
        # Update existing internship
        existing_internship.company_id = internship_data.company_id
        existing_internship.department = internship_data.department
        existing_internship.program = internship_data.program
        existing_internship.start_date = internship_data.start_date
        existing_internship.end_date = internship_data.end_date
        db.commit()
        db.refresh(existing_internship)
        return existing_internship
    else:
        if internship_data.company_id:
            company = get_company(db, internship_data.company_id)
            if company is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.COMPANY_NOT_FOUND)
        # Create new internship
        new_internship = InternshipModel(
            user_id=user_id,
            company_id=internship_data.company_id,
            program=internship_data.program,
            department=internship_data.department,
            start_date=internship_data.start_date,
            end_date=internship_data.end_date,
            status=InternshipStatus.PENDING_REVIEW
        )
        db.add(new_internship)
        db.commit()
        db.refresh(new_internship)
        return new_internship


def update_internship_status(db: Session, internship_id: int, internship_status: InternshipStatus) -> InternshipModel:
    """
    Update the status of an internship.

    Parameters:
    - db (Session): Database session.
    - internship_id (int): The ID of the internship.
    - internship_status (InternshipStatus): The new status of the internship.

    Returns:
    - InternshipModel: The updated internship.

    Raises:
    - HTTPException: If the internship is not found.
    """
    internship = get_internship_by_id(db, internship_id)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.INTERNSHIP_NOT_FOUND)

    internship.status = internship_status
    db.commit()
    db.refresh(internship)
    return internship


def get_user_internship(db: Session, user_id: int) -> Optional[InternshipModel]:
    """
    Get the internship associated with a user.

    Parameters:
    - db (Session): Database session.
    - user_id (int): The ID of the user.

    Returns:
    - Optional[InternshipModel]: The internship of the user, if it exists.
    """
    return db.query(InternshipModel).filter(InternshipModel.user_id == user_id).first()


def get_internship_by_id(db: Session, internship_id: int) -> Optional[InternshipModel]:
    """
    Get an internship by its ID.

    Parameters:
    - db (Session): Database session.
    - internship_id (int): The ID of the internship.

    Returns:
    - Optional[InternshipModel]: The internship if found, else None.
    """
    return db.query(InternshipModel).filter(InternshipModel.id == internship_id).first()


def delete_internship(db: Session, internship_id: int) -> bool:
    """
    Delete an internship from the database, along with all associated files.

    Parameters:
    - db (Session): Database session.
    - internship_id (int): The ID of the internship to delete.

    Returns:
    - bool: True if the internship was deleted, False otherwise.
    """
    internship = get_internship_by_id(db, internship_id)
    if internship:
        # Delete all associated files
        files = db.query(Dikaiologitika).filter(Dikaiologitika.user_id == internship.user_id).all()
        for file in files:
            db.delete(file)
        # delete user answers for internship
        delete_user_answers(db, internship.user_id)
        # delete company answers for internship
        delete_company_answers(db, internship.id)

        # Delete the internship
        db.delete(internship)
        db.commit()
        return True
    return False


def get_all_internships(
        db: Session,
        internship_status: Optional[InternshipStatus] = None,
        program: Optional[InternshipProgram] = None,
        department: Optional[Department] = None,
        user_am: Optional[str] = None,
        company_name: Optional[str] = None,
        page: int = 1,
        items_per_page: int = 10
) -> Tuple[List[InternshipAllRead], int]:
    """
    Get all internships with optional filtering by status, program, department, user academic number, and company name, with pagination.

    Parameters:
    - db (Session): Database session.
    - internship_status (Optional[InternshipStatus]): The status to filter by.
    - program (Optional[InternshipProgram]): The program to filter by.
    - department (Optional[Department]): The department to filter by.
    - user_am (Optional[str]): The academic number to filter by.
    - company_name (Optional[str]): The company name to filter by.
    - page (int): The page number for pagination.
    - items_per_page (int): The number of items per page.

    Returns:
    - Tuple[List[InternshipAllRead], int]: A list of internships with detailed information and the total count.
    """
    query = db.query(InternshipModel)

    if department:
        query = query.filter(InternshipModel.department == department)
    if internship_status:
        query = query.filter(InternshipModel.status == internship_status)
    if program:
        query = query.filter(InternshipModel.program == program)
    if user_am:
        query = query.join(Users).filter(Users.AM.ilike(f"%{user_am}%"))
    if company_name:
        query = query.join(Companies).filter(Companies.name.ilike(f"%{company_name}%"))

    total_items = query.count()
    offset = (page - 1) * items_per_page
    internships = query.offset(offset).limit(items_per_page).all()

    internship_reads = []
    for internship in internships:
        user = get_user_by_id(db, internship.user_id)
        company = get_company(db, internship.company_id)
        internship_reads.append(
            InternshipAllRead(
                id=internship.id,
                user_id=internship.user_id,
                department=internship.department,
                program=internship.program,
                start_date=internship.start_date,
                end_date=internship.end_date,
                status=internship.status,
                user_first_name=user.first_name if user else "",
                user_last_name=user.last_name if user else "",
                user_am=user.AM if user else "",
                company_name=company.name if company else None,
                company_id=company.id if company else None,
            )
        )

    return internship_reads, total_items
