from datetime import timedelta, datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from starlette import status

from core.auth import create_access_token
from core.config import settings
from crud.user_crud import get_user_by_id, create_user, get_user_by_AM, is_admin, is_super_admin
from dependencies import get_db, get_current_user
from models import Users, UserRole, Department
from schemas.response import ResponseWrapper, Message, ResponseTotalItems
from schemas.user_schema import User, UserCreate

router = APIRouter(
    prefix='/user',
    tags=['user']
)
# Calculate the expiration time as 6 hours from the current time
expires_time = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES)
expires_in_seconds = settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60


@router.get('/department-types', response_model=ResponseWrapper[List[str]], status_code=status.HTTP_200_OK)
async def get_department_types_endpoint():
    """
       Provides a list of all available department types defined in the system.
       Returns:
       - ResponseWrapper[List[str]]: A wrapped response containing a list of department types with a success message.
       """
    return ResponseWrapper(data=Department, message=Message(detail="Λίστα όλων των τύπων Τμημάτων."))


@router.get('/', response_model=ResponseTotalItems[List[User]], status_code=status.HTTP_200_OK)
async def read_users_endpoint(
        db: Session = Depends(get_db),
        am: Optional[str] = Query(None, description="Filter users by Academic Number (AM)"),
        role: Optional[str] = Query(None, description="Filter users by role"),
        department: Optional[Department] = Query(None, description="Filter users by department"),
        page: int = Query(1, description="Page number"),
        items_per_page: int = Query(10, description="Number of items per page")):
    """
    Retrieve users from the database with optional filters for AM, role, and department.

    Parameters:
    - db (Session): The database session.
    - am (str): Filter by Academic Number.
    - role (str): Filter by role.
    - department (str): Filter by department.
    - page (int): Page number for pagination.
    - items_per_page (int): Number of items per page.

    Returns:
    - ResponseTotalItems[List[User]]: Response containing the filtered user list and total item count.
    """
    query = db.query(Users)

    if am:
        query = query.filter(Users.AM.ilike(f"%{am}%"))

    if role:
        try:
            query = query.filter(Users.role == UserRole(role))
        except KeyError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Μη έγκυρος ρόλος.")

    if department:
        try:
            query = query.filter(Users.department == Department(department))
        except KeyError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Μη έγκυρο τμήμα.")

    total_items = query.count()

    offset = (page - 1) * items_per_page
    if items_per_page == -1:
        users = query.offset(offset).all()
    else:
        users = query.offset(offset).limit(items_per_page).all()
    return ResponseTotalItems(
        data=users,
        total_items=total_items,
        message=Message(detail="Οι χρήστες ανακτήθηκαν με επιτυχία.")
    )


@router.post("/", response_model=ResponseWrapper, status_code=status.HTTP_200_OK)
async def create_return_user_endpoint(response: Response, user_data: UserCreate, db: Session = Depends(get_db)):
    """
       Endpoint to create a new user or return an existing one based on the Academic Number (AM).

       If a user with the given AM already exists, this endpoint will not create a new user but instead
       return the existing user's details along with a new access token.

       For new users, it creates the user in the database, generates an access token,
       and returns the user's details with the access token set in an HTTP-only cookie.

       Parameters:
       - response (Response): The FastAPI response object, used to set cookies.
       - user_data (UserCreate): The schema containing the data for the user to create.
       - db (Session): The database session dependency.

       Returns:
       - ResponseWrapper[UserCreateResponse]: A wrapped response containing the user's details and a success message.
       """
    # Check if a user with the provided AM exists in the database.
    db_user = get_user_by_AM(db, user_data.AM)
    if db_user:
        # If user exists, determine if they are an admin and generate a new access token.
        admin_status = is_admin(db_user)
        access_token = create_access_token(data={"sub": str(db_user.id)})
        response.set_cookie(
            key="placements_access_token",
            value=access_token,
            httponly=True,
            expires=expires_time,
            max_age=expires_in_seconds,
            secure=True,
            samesite="lax",  # Sets the SameSite attribute to Lax
            # TODO: Change 'path' to match the domain when deployed
        )
        # user_response = UserCreateResponse(
        #     id=db_user.id,
        #     first_name=db_user.first_name,
        #     last_name=db_user.last_name,
        #     AM=db_user.AM,
        #     role=db_user.role.value,
        #     isAdmin=admin_status,
        #     fathers_name=db_user.fathers_name,
        #     reg_year=db_user.reg_year,
        #     email=db_user.email,
        #     telephone_number=db_user.telephone_number,
        #     accessToken=access_token
        # )
    else:
        # If no existing user, convert the Pydantic model to a dict and exclude unset fields for user creation.
        user_dict = user_data.dict(exclude_unset=True)
        print(user_dict)
        # Create a new user in the database.
        new_user = create_user(db=db, user=user_dict)
        # Determine if the new user is an admin and generate a new access token.
        admin_status = is_admin(new_user)
        access_token = create_access_token(data={"sub": str(new_user.id)})
        response.set_cookie(key="placements_access_token", value=access_token, httponly=True, expires=expires_time,
                            samesite="lax", secure=True
                            )
        # user_response = UserCreateResponse(
        #     id=new_user.id,
        #     first_name=new_user.first_name,
        #     last_name=new_user.last_name,
        #     AM=new_user.AM,
        #     role=new_user.role.value,
        #
        #     fathers_name=new_user.fathers_name,
        #     reg_year=new_user.reg_year,
        #     email=new_user.email,
        #     telephone_number=new_user.telephone_number,
        #     isAdmin=admin_status,
        #     accessToken=access_token,
        # )
    return ResponseWrapper(data={'access_token': access_token}, message=Message(detail="User processed successfully"))


@router.get("/{user_id}/", response_model=ResponseWrapper[User], status_code=status.HTTP_200_OK)
async def get_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db),
                                  current_user: Users = Depends(get_current_user)):
    """
        Retrieves a specific user by their database ID.

        This endpoint implements access control to ensure that a user can only access their own information
        unless they have an admin role, which grants access to any user's information.

        Parameters:
        - user_id (int): The ID of the user to retrieve.
        - db (Session): Dependency injection of the database session to access the database.
        - current_user (Users): The user making the request, obtained through dependency injection.

        Raises:
        - HTTPException: 403 Forbidden if the current user is neither the user being requested nor an admin.
        - HTTPException: 404 Not Found if no user with the specified ID exists.

        Returns:
        - ResponseWrapper[User]: The requested user's information wrapped in a standard response structure.
        """
    # Check if the current user is trying to access someone else's information without being an admin.
    if user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Δεν έχετε εξουσιοδότηση να αποκτήσετε πρόσβαση σε αυτόν τον χρήστη.")
    # Attempt to retrieve the requested user from the database.
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        # No user found with the provided ID.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ο χρήστης δεν βρέθηκε.")
    # User found, return the user's information.
    return ResponseWrapper(data=db_user,
                           message=Message(detail="Ο χρήστης ανακτήθηκε με επιτυχία"))


@router.put("/set-admin/{user_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def set_user_as_admin(user_id: int, db: Session = Depends(get_db),
                            current_user: Users = Depends(get_current_user)):
    """
    Promote a user to admin if the current user is a superadmin.

    Parameters:
    - user_id (int): The ID of the user to promote.
    - db (Session): The database session.
    - current_user (Users): The current authenticated user.

    Raises:
    - HTTPException 403: If the current user is not a superadmin.
    - HTTPException 404: If the target user does not exist.

    Returns:
    - Message: A message indicating the promotion status.
    """
    if not is_super_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ο χρήστης δεν είναι Super διαχειριστής.')
    # Attempt to retrieve the requested user from the database.
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ο χρήστης δεν βρέθηκε.')
    db_user.role = UserRole.ADMIN
    db.commit()
    db.refresh(db_user)
    return Message(
        detail=f"Ο χρήστης: {db_user.first_name} {db_user.last_name} προήχθη σε διαχειριστή.")


@router.put("/set-student/{user_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def set_user_as_student(user_id: int, db: Session = Depends(get_db),
                              current_user: Users = Depends(get_current_user)):
    """
    Demote a user to student if the current user is a superadmin.

    Parameters:
    - user_id (int): The ID of the user to demote.
    - db (Session): The database session.
    - current_user (Users): The current authenticated user.

    Raises:
    - HTTPException 403: If the current user is not a superadmin.
    - HTTPException 404: If the target user does not exist.

    Returns:
    - Message: A message indicating the demotion status.
    """
    if not is_super_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ο χρήστης δεν είναι Super διαχειριστής.')
    # Attempt to retrieve the requested user from the database.
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ο χρήστης δεν βρέθηκε.')
    db_user.role = UserRole.STUDENT
    db.commit()
    db.refresh(db_user)
    return Message(
        detail=f"Ο χρήστης: {db_user.first_name} {db_user.last_name} υποβαθμίστηκε σε φοιτητή.")
