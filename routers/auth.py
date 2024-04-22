# auth_router.py
from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, Cookie, Response
from fastapi.responses import RedirectResponse, JSONResponse
from jose import jwt
from sqlalchemy.orm import Session
from starlette import status

from core.auth import verify_jwt
from crud.user_crud import get_user_by_id, is_admin
from dependencies import get_db
from schemas.response import ResponseWrapper, Message
from schemas.user_schema import UserCreateResponse

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)


@router.get("/verify-token", response_model=ResponseWrapper[UserCreateResponse], status_code=status.HTTP_200_OK)
def verify_token_endpoint(response: Response, access_token: str = Cookie(None, alias="placements_access_token"),
                          db: Session = Depends(get_db)):
    # Generate a CSRF token in every call
    # csrf_token = token_urlsafe(16)
    print(access_token)
    try:
        if not access_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not provided")

        # Attempt to verify the JWT and decode it to get the user information
        payload = verify_jwt(access_token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        # Fetch the user from the database using the user ID
        user = get_user_by_id(db, int(user_id))
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        admin_status = is_admin(user)
        user_response = UserCreateResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            AM=user.AM,
            role=user.role,
            isAdmin=admin_status,
            accessToken=access_token
        )

        # Prepare a custom message
        success_message = f"Token verification was successful for user: {user.first_name} {user.last_name}"

        # Wrap the data and message in the response wrapper
        response_data = ResponseWrapper(data=user_response, message=Message(detail=success_message))

        # Set the CSRF token in the cookie
        # response.set_cookie(key="csrf_token", value=csrf_token, httponly=True)
        return response_data

    except jwt.JWTError:
        # Even if the token is invalid, issue a CSRF token for consistent behavior
        # response.set_cookie(key="csrf_token", value=csrf_token, httponly=True)
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Token verification failed"})


@router.get("/login", response_class=RedirectResponse)
def login(response: RedirectResponse):
    # Generate a CSRF token
    csrf_token = token_urlsafe()
    print('login', csrf_token)
    # You might want to store this CSRF token in a database associated with the session/user
    # For simplicity, we're storing it in a cookie here

    # response.set_cookie(key="csrf_token", value=csrf_token, httponly=True, samesite='none', secure=True)
    response.set_cookie(key="csrf_token", value=csrf_token, httponly=False, secure=True, samesite="lax")

    # Define your parameters
    client_id = "64493671d44156030a26af5c"
    response_type = "code"
    scope = "profile,ldap,id,cn,announcements"
    redirect_uri = "http://localhost:3000/auth"

    # Construct the redirect URL
    auth_url = f"https://login.it.teithe.gr/authorization/?client_id={client_id}&response_type={response_type}&scope={scope}&redirect_uri={redirect_uri}&state={csrf_token}"
    return RedirectResponse(url=auth_url)


@router.get("/auth")
async def auth(code: str, state: str, csrf_token: str = Cookie(None)):
    print(state, csrf_token)
    if not csrf_token or state != csrf_token:
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    # If the token is valid, you would proceed with your logic, such as exchanging the code for an access token

    return {"message": "CSRF token validated successfully"}
