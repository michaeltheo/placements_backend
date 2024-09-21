from io import BytesIO
from typing import List, Optional, Union
from urllib.parse import quote

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import StreamingResponse

from core.messages import Messages
from crud.company_crud import get_company
from crud.intership_crud import get_user_internship, delete_internship, \
    create_or_update_internship, update_internship_status, get_all_internships, get_internship_by_id, \
    fetch_active_internships_with_details, fetch_supervisors
from crud.user_crud import is_admin, get_user_by_id, is_secretary
from dependencies import get_db, get_current_user
from models import Users, InternshipProgram, InternshipStatus, Department
from schemas.internship_schema import InternshipRead, InternshipCreate, InternshipAllRead, InternshipUpdate
from schemas.response import ResponseWrapper, Message, ResponseTotalItems

router = APIRouter(
    prefix='/internship',
    tags=['internship']
)


@router.get("/all/", response_model=ResponseTotalItems[List[InternshipAllRead]], status_code=status.HTTP_200_OK)
async def get_all_internships_endpoint(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user),
        department: Optional[Department] = Query(None, description='Filter by Department'),
        internship_status: Optional[InternshipStatus] = Query(None, description="Filter by Internship Status"),
        program: Optional[InternshipProgram] = Query(None, description="Filter by Internship Program"),
        user_am: Optional[str] = Query(None, description="Filter by User AM"),
        company_name: Optional[str] = Query(None, description="Filter by Company Name"),
        sendBySecretary: bool = Query(False,
                                      description="If true, filters by secretary-uploaded document (AitisiPraktikis)"),
        page: int = Query(1, description="Page number"),
        items_per_page: int = Query(10, description="Number of items per page")
):
    """
    Retrieves all internships, with optional filters for department, status, program, user academic number,
    and company name. If `sendBySecretary` is True and the request is made by a secretary, it returns only
    the internships where the user has uploaded a document of type 'AitisiPraktikis'.

    Parameters:
    - db (Session): Database session.
    - current_user (Users): The current authenticated user.
    - department (Optional[Department]): Filter by department.
    - internship_status (Optional[InternshipStatus]): Filter by internship status.
    - program (Optional[InternshipProgram]): Filter by internship program.
    - user_am (Optional[str]): Filter by user academic number.
    - company_name (Optional[str]): Filter by company name.
    - sendBySecretary (bool): If true, limits results to those where 'AitisiPraktikis' document was uploaded.
    - page (int): Page number for pagination.
    - items_per_page (int): Number of items per page.

    Returns:
    - ResponseTotalItems[List[InternshipAllRead]]: A list of internships with detailed information.
    """
    if not is_admin(current_user) and not is_secretary(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Messages.UNAUTHORIZED_USER)

    internships, total_items = get_all_internships(
        db=db,
        internship_status=internship_status,
        department=department,
        program=program,
        user_am=user_am,
        company_name=company_name,
        send_by_secretary=sendBySecretary if is_secretary(current_user) else False,
        page=page,
        items_per_page=items_per_page
    )

    return ResponseTotalItems(
        data=internships,
        total_items=total_items,
        message=Message(detail=Messages.ALL_INTERNSHIPS_RETRIEVED)
    )


@router.post("/", response_model=ResponseWrapper[InternshipRead], status_code=status.HTTP_200_OK)
async def create_or_update_internship_endpoint(
        internship: Union[InternshipCreate, InternshipUpdate],
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
    Create a new internship or update an existing one. The user can only create/update their own internship.
    """
    new_internship = create_or_update_internship(db=db, user_id=current_user.id, internship_data=internship)
    return ResponseWrapper(data=new_internship,
                           message=Message(detail=Messages.INTERNSHIP_CREATED_OR_UPDATED))


@router.get('/{user_id}', response_model=ResponseWrapper[InternshipRead], status_code=status.HTTP_200_OK)
async def get_internship_by_user_endpoint(user_id: int, db: Session = Depends(get_db),
                                          current_user: Users = Depends(get_current_user)):
    internship = get_user_internship(db, user_id)
    if internship is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=Messages.INTERNSHIP_NOT_FOUND)
    company = get_company(db, internship.company_id)
    internship_response = InternshipRead(
        id=internship.id,
        user_id=internship.user_id,
        company_id=internship.company_id,
        department=internship.department,
        program=internship.program,
        start_date=internship.start_date,
        supervisor=internship.supervisor,
        end_date=internship.end_date,
        status=internship.status,
        company_name=company.name if company else None
    )
    user_name = f"{current_user.first_name} {current_user.last_name}"
    return ResponseWrapper(data=internship_response, message=Message(
        detail=Messages.INTERNSHIP_RETRIEVED_FOR_USER.format(user_name=user_name)))


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
                            detail=Messages.UNAUTHORIZED_USER)

    deleted = delete_internship(db, internship_id)
    if deleted:
        return Message(detail=Messages.INTERNSHIP_DELETED_SUCCESS)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=Messages.INTERNSHIP_DELETION_FAILED)


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
    # Retrieve the internship by its ID
    internship = get_internship_by_id(db, internship_id)
    if not internship:
        # Raise 404 error if internship not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.INTERNSHIP_NOT_FOUND)

    # Check if the current user is authorized to update the internship
    if current_user.id != internship.user_id and not is_admin(current_user):
        # Raise 403 error if the user is not the owner or an admin
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Messages.UNAUTHORIZED_USER)

    # Additional checks for certain status updates
    if internship_status in {InternshipStatus.ACTIVE, InternshipStatus.ENDED}:
        if not is_admin(current_user):
            # Only admins can change status to ACTIVE or ENDED
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Messages.UNAUTHORIZED_USER)

    # Update the internship status
    updated_internship = update_internship_status(db=db, internship_id=internship_id,
                                                  internship_status=internship_status,
                                                  isCurrentUserAdmin=is_admin(current_user))
    get_user = get_user_by_id(db, internship.user_id)
    # if get_user and get_user.telephone_number and is_admin(current_user):
    #     if len(get_user.telephone_number) > 5:  # Ensure the telephone number length is more than 5
    #         formatted_phone = format_phone_number(get_user.telephone_number)
    #         print(formatted_phone)
    #         message = f"To Γραφείο Πρακτικής άλλαξε την κατάσταση της πρακτικής σου σε {internship_status.value}."
    #         try:
    #             send_sms(formatted_phone, message)
    #         except Exception as e:
    #             # Handle exceptions that might occur during SMS sending
    #             logger.error(f"Failed to send SMS to {formatted_phone}: {e}")
    # Return the updated internship details
    return ResponseWrapper(data=updated_internship, message=Message(detail=Messages.INTERNSHIP_STATUS_UPDATED))


@router.get("/export/active_internships/")
async def export_internships_to_excel(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user),
        department: Department = Query(None, description="Filter by department"),
        program: InternshipProgram = Query(None, description="Filter by internship program")
):
    """
    Exports details of active internships to an Excel file, filtered by department and program.
    This endpoint is accessible only to users with admin privileges.

    Parameters:
    - db (Session): Database session dependency injection.
    - current_user (Users): The current user performing the operation, must be an admin.
    - department (Department, optional): Filter internships by a specific department.
    - program (InternshipProgram, optional): Filter internships by a specific internship program.

    Returns:
    - StreamingResponse: An Excel file containing details of active internships filtered by the specified criteria.
      The file includes data such as the intern's name, academic number, email, phone number,
      internship dates, supervisor, and associated company details including company name,
      tax identification number, email, phone number, and city.

    Raises:
    - HTTPException: If the current user is not authorized as an admin.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=Messages.UNAUTHORIZED_USER)

    # Data retrieval
    internships = fetch_active_internships_with_details(db, program, department)

    # Prepare Excel data
    data = [{
        "ΟΝΟΜΑ": getattr(intern.user, 'first_name', None),
        "ΕΠΙΘΕΤΟ": getattr(intern.user, 'last_name', None),
        "ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ": getattr(intern.user, 'AM', None),
        "EMAIL": getattr(intern.user, 'email', None),
        "ΤΗΛΕΦΩΝΟ": getattr(intern.user, 'telephone_number', None),
        "ΗΜΕΡΟΜΗΝΙΑ ΕΝΑΡΞΗΣ ΠΡΑΚΤΙΚΗΣ": intern.start_date.strftime("%Y-%m-%d") if intern.start_date else None,
        "ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΠΡΑΚΤΙΚΗΣ": intern.end_date.strftime("%Y-%m-%d") if intern.end_date else None,
        "ΕΠΟΠΤΗΣ": intern.supervisor,
        "ΟΝΟΜΑ ΕΤΑΙΡΕΙΑΣ": getattr(intern.company, 'name', None) if intern.company else None,
        "ΑΦΜ ΕΤΑΙΡΕΙΑΣ": getattr(intern.company, 'AFM', None) if intern.company else None,
        "EMAIL ΕΤΑΙΡΕΙΑΣ": getattr(intern.company, 'email', None) if intern.company else None,
        "ΤΗΛΕΦΩΝΟ ΕΤΑΙΡΕΙΑΣ": getattr(intern.company, 'telephone', None) if intern.company else None,
        "ΠΟΛΗ ΕΤΑΙΡΕΙΑΣ": getattr(intern.company, 'city', None) if intern.company else None,
    } for intern in internships]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, index=False, sheet_name='Ενεργές Πρακτικές')
    output.seek(0)

    # Safe encoding for filename
    department_str = quote(department.value) if department else "All"
    program_str = quote(program.value) if program else "All"
    filename = f"Active_Internships_{department_str}_{program_str}.xlsx"

    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(content=output, headers=headers,
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/get_supervisors/", status_code=status.HTTP_200_OK)
async def get_supervisors(search: Optional[str] = None):
    """
    Fetch all supervisors from an external API and optionally filter them by a search term.
    """
    try:
        supervisors = fetch_supervisors()
        if search:
            supervisors = [name for name in supervisors if search.lower() in name.lower()]
        return supervisors
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
