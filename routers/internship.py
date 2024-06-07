from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from crud.company_crud import get_company
from crud.intership_crud import get_user_internship, get_internships_by_company, delete_internship, \
    create_or_update_internship, update_internship_status, get_all_internships
from crud.user_crud import is_admin
from dependencies import get_db, get_current_user
from models import Users, InternshipProgram, InternshipStatus
from schemas.internship_schema import InternshipRead, InternshipCreate, InternshipAllRead
from schemas.response import ResponseWrapper, Message, ResponseTotalItems

router = APIRouter(
    prefix='/internship',
    tags=['internship']
)


@router.get("/all", response_model=ResponseTotalItems[List[InternshipAllRead]], status_code=status.HTTP_200_OK)
async def get_all_internships_endpoint(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user),
        internship_status: Optional[InternshipStatus] = Query(None, description="Filter by Internship Status"),
        program: Optional[InternshipProgram] = Query(None, description="Filter by Internship Program"),
        user_am: Optional[str] = Query(None, description="Filter by User AM"),
        company_name: Optional[str] = Query(None, description="Filter by Company Name"),
        page: int = Query(1, description="Page number"),
        items_per_page: int = Query(10, description="Number of items per page")
):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Μόνο οι διαχειριστές μπορούν να έχουν πρόσβαση σε αυτήν την ενέργεια")

    internships, total_items = get_all_internships(
        db=db,
        internship_status=internship_status,
        program=program,
        user_am=user_am,
        company_name=company_name,
        page=page,
        items_per_page=items_per_page
    )

    return ResponseTotalItems(
        data=internships,
        total_items=total_items,
        message=Message(detail="Οι πρακτικές ασκήσεις ανακτήθηκαν με επιτυχία")
    )


@router.post("/", response_model=ResponseWrapper[InternshipRead], status_code=status.HTTP_200_OK)
async def create_or_update_internship_endpoint(
        internship: InternshipCreate,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
    Create a new internship or update an existing one. The user can only create/update their own internship.
    """
    new_internship = create_or_update_internship(db=db, user_id=current_user.id, internship_data=internship)
    return ResponseWrapper(data=new_internship,
                           message=Message(detail="Η πρακτική άσκηση δημιουργήθηκε ή ενημερώθηκε με επιτυχία."))


@router.get('/company/{company_id}', response_model=ResponseTotalItems[List[InternshipRead]],
            status_code=status.HTTP_200_OK)
async def get_internships_by_company_endpoint(
        company_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user),
        program: Optional[InternshipProgram] = Query(None, description="Filter by Internship Program"),
        internship_status: Optional[InternshipStatus] = Query(None, description="Filter by Internship Status"),
        page: int = Query(1, description="Page number"),
        items_per_page: int = Query(10, description="Number of items per page")
):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Ο χρήστης δεν είναι εξουσιοδοτημένος να εκτελέσει αυτήν την ενέργεια.')

    internships, total_items = get_internships_by_company(db, company_id, program, internship_status, page,
                                                          items_per_page)
    if not internships:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Δεν βρέθηκαν πρακτικές ασκήσεις για αυτήν την εταιρεία.")

    return ResponseTotalItems(
        data=internships,
        total_items=total_items,
        message=Message(detail='Οι πρακτικές ασκήσεις ανακτήθηκαν με επιτυχία')
    )


@router.get('/{user_id}', response_model=ResponseWrapper[InternshipRead], status_code=status.HTTP_200_OK)
async def get_internship_by_user_endpoint(user_id: int, db: Session = Depends(get_db),
                                          current_user: Users = Depends(get_current_user)):
    internship = get_user_internship(db, user_id)
    if internship is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Δεν βρέθηκε πρακτική άσκηση για αυτόν τον χρήστη.")
    company = get_company(db, internship.company_id)
    internship_response = InternshipRead(
        id=internship.id,
        user_id=internship.user_id,
        company_id=internship.company_id,
        program=internship.program,
        start_date=internship.start_date,
        end_date=internship.end_date,
        status=internship.status,
        company_name=company.name if company else None
    )
    return ResponseWrapper(data=internship_response, message=Message(
        detail=f'Η πρακτική άσκηση ανακτήθηκε για τον χρήστη {current_user.first_name} {current_user.last_name}'))


@router.get("/delete/{internship_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_internship_endpoint(internship_id: int, db: Session = Depends(get_db),
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
                            detail="Ο χρήστης δεν είναι εξουσιοδοτημένος να εκτελέσει αυτήν την ενέργεια.")

    deleted = delete_internship(db, internship_id)
    if deleted:
        return Message(detail="Η πρακτική άσκηση διαγράφηκε με επιτυχία.")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Η πρακτική άσκηση δεν βρέθηκε ή δεν ήταν δυνατή η διαγραφή της.")


@router.put("/{internship_id}", response_model=ResponseWrapper[InternshipRead], status_code=status.HTTP_200_OK)
async def update_internship_status_endpoint(
        internship_id: int,
        internship_status: InternshipStatus,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
    Update the details of an internship, including its status. Only accessible by admin users.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Μόνο οι διαχειριστές μπορούν να ενημερώσουν την κατάσταση της πρακτικής άσκησης")

    updated_internship = update_internship_status(db=db, internship_id=internship_id,
                                                  internship_status=internship_status)
    return ResponseWrapper(data=updated_internship, message=Message(detail="Η πρακτική άσκηση ενημερώθηκε με επιτυχία"))
