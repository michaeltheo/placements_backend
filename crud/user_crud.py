from typing import Optional, Tuple

from sqlalchemy.orm import Session

from models import Users, UserRole, Department


def get_user_by_AM(db: Session, AM: str) -> Optional[Users]:
    """
    Retrieve a user by their AM value.

    Parameters:
    - db (Session): The database session.
    - AM (str): The AM value of the user.

    Returns:
    - Optional[Users]: An instance of the Users model or None if not found.
    """
    return db.query(Users).filter(Users.AM == AM).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[Users]:
    """
    Retrieve a user by their database ID.

    Parameters:
    - db (Session): The database session.
    - user_id (int): The ID of the user in the database.

    Returns:
    - Optional[Users]: An instance of the Users model or None if not found.
    """
    return db.query(Users).filter(Users.id == user_id).first()


def create_user(db: Session, user: dict) -> Users:
    """
    Create a new user in the database.

    Parameters:
    - db (Session): The database session.
    - user (dict): A dictionary containing the user's information.

    Returns:
    - Users: An instance of the newly created Users model.
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
    return user.role == UserRole.ADMIN or user.role == UserRole.SUPER_ADMIN


def is_super_admin(user: Users) -> bool:
    """
    Check if a given user has a super admin role.

    Parameters:
    - user (Users): An instance of the Users model.

    Returns:
    - bool: True if the user is a super admin, False otherwise.
    """
    return user.role == UserRole.SUPER_ADMIN


def split_full_name(fullName: str) -> Optional[Tuple[str, str]]:
    """
    Split a full name into first and last names.

    Parameters:
    - fullName (str): The full name to split.

    Returns:
    - Optional[Tuple[str, str]]: A tuple containing the first name and last name.
    """
    if fullName:
        names = fullName.split()
        first_name = names[0]
        last_name = ' '.join(names[1:]) if len(names) > 1 else ''
        return first_name, last_name
    return None, None


def determine_department(am: Optional[str]) -> Optional[Department]:
    """
    Determine the department based on the AM value.

    Parameters:
    - am (Optional[str]): The AM value.

    Returns:
    - Optional[Department]: The determined department or None if the AM value is invalid.
    """
    if am is None:
        return None
    if am.startswith('1'):
        return Department.IT_TEITHE
    elif am.startswith('5'):
        return Department.EL_TEITHE
    elif am.startswith('2'):
        return Department.IHU_IEE
    else:
        return None
