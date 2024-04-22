from datetime import timedelta, datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from crud.user_crud import get_user_by_id, create_user, get_user_by_AM, is_admin
from dependencies import get_db, get_current_user
from models import Users
from schemas.response import ResponseWrapper, Message
from schemas.user_schema import User, UserBase

router = APIRouter(
    prefix='/user',
    tags=['user']
)
# Calculate the expiration time as 6 hours from the current time
expires_time = datetime.now(timezone.utc) + timedelta(hours=6)


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


# @router.post("/", response_model=ResponseWrapper[UserCreateResponse], status_code=status.HTTP_200_OK)
def create_return_user_endpoint(user_data: UserBase, db: Session):
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
    print(db)
    db_user = get_user_by_AM(db, user_data['AM'])
    if not db_user:
        # If no existing user, convert the Pydantic model to a dict and exclude unset fields for user creation.
        user_dict = user_data.dict(exclude_unset=True)
        # Create a new user in the database.
        db_user = create_user(db=db, user=user_dict)
    return db_user


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
