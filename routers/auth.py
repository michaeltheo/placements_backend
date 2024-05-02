# auth_router.py
import secrets
import urllib

from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.responses import RedirectResponse
from jose import jwt
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from core.auth import verify_jwt
from core.config import settings
from crud.user_crud import get_user_by_id, is_admin
from dependencies import get_db
from schemas.response import Message, ResponseWrapper
from schemas.user_schema import UserCreateResponse

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)


@router.get("/redirect")
async def auth_redirect_endpoint(request: Request):
    redirect_uri = "http://localhost:3000/auth"
    scope = "profile,ldap,id,cn,announcements"
    client_id = settings.CLIENT_ID
    state = secrets.token_hex(16)
    request.session['oauth_state'] = state

    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state
    }
    url = f"https://login.it.teithe.gr/authorization/?{urllib.parse.urlencode(params)}"
    print(url)
    return RedirectResponse(url)


@router.get("/verify-token", response_model=ResponseWrapper[UserCreateResponse], status_code=status.HTTP_200_OK)
def verify_token_endpoint(access_token: str = Cookie(None, alias="placements_access_token"),
                          db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not provided")
    try:
        # Verify the JWT and decode it to get the user information
        payload = verify_jwt(access_token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        # Fetch the user from the database using the user ID
        user = get_user_by_id(db, int(user_id))
        admin_status = is_admin(user)
        user_response = UserCreateResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            AM=user.AM,
            role=user.role.value,
            isAdmin=admin_status,
            accessToken=access_token
        )
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        # Prepare a custom message
        success_message = f"Token verification was successful for user: {user.first_name} {user.last_name}"
        # Return the custom message
        return ResponseWrapper(data=user_response, message=Message(detail=success_message))
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed")
