from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from core.messages import Messages
from crud.company_crud import create_company, update_company, delete_company, get_all_companies, get_company_by_AFM
from crud.user_crud import is_admin
from dependencies import get_db, get_current_user
from models import Users
from schemas.company_schema import CompanyBase, Company
from schemas.response import ResponseWrapper, Message, ResponseTotalItems

router = APIRouter(
    prefix='/company',
    tags=['company']
)


@router.get("/companies", response_model=ResponseTotalItems[List[Company]], status_code=status.HTTP_200_OK)
async def read_all_companies_endpoint(
        db: Session = Depends(get_db),
        name: Optional[str] = Query(None, description="Filter companies by name"),
        page: Optional[int] = Query(None, description="Page number"),
        items_per_page: Optional[int] = Query(None, description="Number of items per page")
):
    """
    Fetches all companies from the database with optional name filtering and pagination.

    Parameters:
    - db (Session): Database session.
    - name (str, optional): Filter companies by name.
    - page (int, optional): Page number for pagination.
    - items_per_page (int, optional): Number of items per page.

    Returns:
    - ResponseWrapper[List[Companies]]: Filtered and optionally paginated list of companies wrapped in a response wrapper.
    """
    companies, total_items = get_all_companies(db, name, page, items_per_page)
    return ResponseTotalItems(data=companies, total_items=total_items,
                              message=Message(detail=Messages.ALL_COMPANIES_RETRIEVED))


@router.post("/", response_model=ResponseWrapper[Company], status_code=status.HTTP_200_OK)
async def create_company_endpoint(company_data: CompanyBase, db: Session = Depends(get_db),
                                  current_user: Users = Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=Messages.UNAUTHORIZED_USER)
    company_exists = get_company_by_AFM(db, company_data.AFM)
    if company_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Messages.COMPANY_ALREADY_EXISTS)
    company = create_company(db, company_data)
    return ResponseWrapper(data=company,
                           message=Message(detail=Messages.COMPANY_CREATED_SUCCESS.format(company_name=company.name)))


@router.put('/{company_id}', response_model=ResponseWrapper[Company], status_code=status.HTTP_200_OK)
async def update_company_endpoint(company_id: int, company_data: CompanyBase, db: Session = Depends(get_db),
                                  current_user: Users = Depends(get_current_user)):
    """
    Endpoint to update a company's information.

    Parameters:
    - company_id (int): ID of the company to update.
    - company_data (CompanyBase): Data to update the company with.
    - db (Session): Database session dependency injection.
    - current_user (Users): Current user performing the operation, injected from security context.

    Returns:
    - ResponseWrapper[Company]: Updated company information wrapped in a response wrapper.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=Messages.UNAUTHORIZED_USER)
    updated_company = update_company(db, company_id, company_data)
    if updated_company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.COMPANY_NOT_FOUND)
    return ResponseWrapper(data=updated_company,
                           message=Message(
                               detail=Messages.COMPANY_UPDATED_SUCCESS.format(company_name=updated_company.name)))


@router.get("/delete/{company_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_company_endpoint(company_id: int, db: Session = Depends(get_db),
                                  current_user: Users = Depends(get_current_user)):
    """
    Endpoint to delete a company. Only accessible by admin users.

    Parameters:
    - company_id (int): ID of the company to delete.
    - db (Session): Database session dependency injection.
    - current_user (Users): Current user performing the operation, injected from security context.

    Returns:
    - ResponseWrapper[Message]: A message indicating the outcome of the deletion process.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=Messages.UNAUTHORIZED_USER)

    deleted = delete_company(db, company_id)
    if deleted:
        return Message(detail=Messages.COMPANY_DELETED_SUCCESS)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=Messages.COMPANY_DELETION_FAILED)
