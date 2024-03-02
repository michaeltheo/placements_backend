from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from starlette import status

from core.auth import create_access_token
from crud.user_crud import get_user_by_id, create_user, get_user_by_AM, is_admin
from dependencies import get_db, get_current_user
from models import Users
from schemas.response import ResponseWrapper, Message
from schemas.user_schema import User, UserCreate

router = APIRouter(
    prefix='/user',
    tags=['user']
)
db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/')
async def read_users(db: db_dependency):
    return db.query(Users).all()


@router.post("/", response_model=ResponseWrapper[User])
def create_user_endpoint(response: Response, user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_AM(db, user.AM)
    if db_user:
        # Generate token for existing user
        access_token = create_access_token(data={"sub": str(db_user.id)})
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return ResponseWrapper(data=db_user, message=Message(detail="User already exists"))
    else:
        # Create new user and generate token
        new_user = create_user(db=db, user=user.dict())
        access_token = create_access_token(data={"sub": str(new_user.id)})
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return ResponseWrapper(data=new_user,
                               message=Message(detail="User created successfully"))


@router.get("/{user_id}/", response_model=ResponseWrapper[User])
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    if user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user.")

    db_user = get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return ResponseWrapper(data=db_user,
                           message=Message(detail="User retrieved successfully"))
