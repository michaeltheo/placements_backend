from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from starlette import status

from core.auth import create_access_token
from crud.user_crud import get_user_by_id, create_user, get_user_by_AM, is_admin
from dependencies import get_db, get_current_user
from models import Users
from schemas.response import ResponseWrapper, Message
from schemas.user_schema import User, UserCreate, UserCreateResponse

router = APIRouter(
    prefix='/user',
    tags=['user']
)


@router.get('/', response_model=ResponseWrapper[List[User]], status_code=status.HTTP_200_OK)
async def read_users_endpoint(db: Session = Depends(get_db)):
    """
    Retrieves a list of all users registered in the system.

    This endpoint does not implement specific access control and is intended to provide a comprehensive
    list of users. Implementing access controls, such as allowing only admins to fetch this list, may be necessary
    depending on the application's security requirements.

    Parameters:
    - db (Session): Dependency injection of the database session to access the database.

    Returns:
    - ResponseWrapper[List[User]]: A list of all users wrapped in a standard response structure, along with a success message.
    """
    # Retrieve all users from the database.
    users = db.query(Users).all()
    # Return the list of users.
    return ResponseWrapper(data=users, message=Message(detail="Users fetched succesfully"))


@router.post("/", response_model=ResponseWrapper[UserCreateResponse], status_code=status.HTTP_200_OK)
def create_return_user_endpoint(response: Response, user_data: UserCreate, db: Session = Depends(get_db)):
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
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        user_response = UserCreateResponse(
            id=db_user.id,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            AM=db_user.AM,
            role=db_user.role.value,
            isAdmin=admin_status
        )
    else:
        # If no existing user, convert the Pydantic model to a dict and exclude unset fields for user creation.
        user_dict = user_data.dict(exclude_unset=True)
        # Create a new user in the database.
        new_user = create_user(db=db, user=user_dict)
        # Determine if the new user is an admin and generate a new access token.
        admin_status = is_admin(new_user)
        access_token = create_access_token(data={"sub": str(new_user.id)})
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        user_response = UserCreateResponse(
            id=new_user.id,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            AM=new_user.AM,
            role=new_user.role.value,
            isAdmin=admin_status
        )
    return ResponseWrapper(data=user_response, message=Message(detail="User processed successfully"))


@router.get("/{user_id}/", response_model=ResponseWrapper[User], status_code=status.HTTP_200_OK)
def get_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db),
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user.")
    # Attempt to retrieve the requested user from the database.
    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        # No user found with the provided ID.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    # User found, return the user's information.
    return ResponseWrapper(data=db_user,
                           message=Message(detail="User retrieved successfully"))
