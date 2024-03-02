from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from core.auth import verify_jwt
from crud.user_crud import get_user_by_id
from database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(HTTPBearer())):
    try:
        payload = verify_jwt(token.credentials)
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=400, detail="Invalid token payload.")
        # Fetch the user from the database using the user_id
        user = get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token.")
