from fastapi import Depends, HTTPException, Cookie
from jose import JWTError
from sqlalchemy.orm import Session
from starlette import status

from core.auth import verify_jwt
from core.messages import Messages
from crud.user_crud import get_user_by_id
from database import SessionLocal


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get the current user
def get_current_user(db: Session = Depends(get_db), placements_access_token: str = Cookie(None)):
    try:
        # Check if the token is present
        if placements_access_token is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=Messages.TOKEN_VALIDATION_ERROR)

        # Verify the JWT token
        payload = verify_jwt(placements_access_token)

        # Extract user ID from the token payload
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Messages.INVALID_TOKEN)

        # Fetch the user from the database using the user ID
        user = get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.USER_NOT_FOUND)

        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.INVALID_TOKEN)
