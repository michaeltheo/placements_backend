from typing import Type

from sqlalchemy.orm import Session

from models import Users, UserRole


def get_user_by_AM(db: Session, AM: str) -> Type[Users] | None:
    """
    Retrieve a user by their AM value.

    Parameters:
    - db (Session): The database session.
    - AM (str): The AM value of the user.

    Returns:
    - Users: An instance of the Users model or None if not found.
    """
    return db.query(Users).filter(Users.AM == AM).first()


def get_user_by_id(db: Session, user_id: int) -> Type[Users] | None:
    """
    Retrieve a user by their database ID.

    Parameters:
    - db (Session): The database session.
    - user_id (int): The ID of the user in the database.

    Returns:
    - `Users`: An instance of the Users model or None if not found.
    """
    return db.query(Users).filter(Users.id == user_id).first()


def create_user(db: Session, user: dict) -> Users:
    """
    Create a new user in the database.

    Parameters:
    - db (Session): The database session.
    - user (dict): A dictionary containing the user's information.

    Returns:
    - `Users`: An instance of the newly created Users model.
    """
    # Extract the role and remove it from the dictionary to avoid conflict
    role_str = user.pop('role', None)  # Remove role from user dict and store its value

    # Convert the role string to the UserRole enum, defaulting to STUDENT if not provided
    role_value = UserRole.STUDENT if role_str is None else UserRole[role_str.upper()]

    db_user = Users(**user, role=role_value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def is_admin(user: Users) -> bool:
    """
    Check if a given user has an admin role.

    Parameters:
    - user (Users): An instance of the Users model.

    Returns:
    - bool: True if the user is an admin, False otherwise.
    """
    return user.role == UserRole.ADMIN
