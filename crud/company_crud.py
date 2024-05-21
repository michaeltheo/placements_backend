from typing import Optional, Type, List

from sqlalchemy.orm import Session

from models import Companies
from schemas.company_schema import CompanyBase


def get_all_companies(db: Session, name: Optional[str] = None, page: Optional[int] = None,
                      items_per_page: Optional[int] = None) -> (
        List[Type[Companies]], int):
    """
    Retrieves all companies from the database with optional name filtering and pagination.

    Parameters:
    - db (Session): Database session.
    - name (str, optional): Filter companies by name.
    - page (int, optional): Page number for pagination.
    - items_per_page (int, optional): Number of items per page.

    Returns:
    - list: A list of company instances.
    - int: Total number of companies.
    """
    query = db.query(Companies)

    if name:
        query = query.filter(Companies.name.ilike(f"%{name}%"))

    total_items = query.count()

    if page is not None and items_per_page is not None:
        offset = (page - 1) * items_per_page
        query = query.offset(offset).limit(items_per_page)

    companies = query.all()

    return companies, total_items


def get_company_by_AFM(db: Session, AFM: str) -> Optional[Companies]:
    """
    Retrieves a company by its AFM (tax identification number).

    Parameters:
    - db (Session): Database session.
    - AFM (str): The AFM of the company to retrieve.

    Returns:
    - Companies: The company instance if found, else None.
    """
    return db.query(Companies).filter(Companies.AFM == AFM).first()


def create_company(db: Session, company_data: CompanyBase) -> Companies:
    """
    Creates a new company record in the database.

    Parameters:
    - db (Session): Database session.
    - company_data (CompanyBase): The data of the company to create.

    Returns:
    - Companies: The created company instance.
    """
    company = Companies(**company_data.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def get_company(db: Session, company_id: int) -> Optional[Companies]:
    """
    Retrieves a company by its database ID.

    Parameters:
    - db (Session): Database session.
    - company_id (int): The ID of the company to retrieve.

    Returns:
    - Companies: The company instance if found, else None.
    """
    return db.query(Companies).filter(Companies.id == company_id).first()


def update_company(db: Session, company_id: int, company_data: CompanyBase) -> Optional[Companies]:
    """
    Updates an existing company record.

    Parameters:
    - db (Session): Database session.
    - company_id (int): The ID of the company to update.
    - company_data (dict): Dictionary of data to update.

    Returns:
    - Companies: The updated company instance if successful, else None.
    """
    company = get_company(db, company_id)
    if company:
        update_data = company_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company, key, value)
        db.commit()
        db.refresh(company)
        return company
    return None


def delete_company(db: Session, company_id: int) -> bool:
    """
    Deletes a company from the database.

    Parameters:
    - db (Session): Database session.
    - company_id (int): The ID of the company to delete.

    Returns:
    - bool: True if the company was deleted, False otherwise.
    """
    company = get_company(db, company_id)
    if company:
        db.delete(company)
        db.commit()
        return True
    return False
