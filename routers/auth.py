# auth_router.py
import uuid
from datetime import datetime, timezone, timedelta
from secrets import token_urlsafe
from urllib.parse import urlencode

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response
from fastapi.responses import RedirectResponse, JSONResponse
from jose import jwt
from sqlalchemy.orm import Session
from starlette import status

from core.auth import verify_jwt, create_access_token
from core.config import Settings
from crud.user_crud import get_user_by_id, is_admin
from dependencies import get_db
from routers.users import create_return_user_endpoint
from schemas.response import ResponseWrapper, Message
from schemas.user_schema import UserCreateResponse

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

settings = Settings()
csrf_tokens = {}
expires_time = datetime.now(timezone.utc) + timedelta(hours=6)


@router.get("/verify-token", response_model=ResponseWrapper[UserCreateResponse], status_code=status.HTTP_200_OK)
def verify_token_endpoint(response: Response, access_token: str = Cookie(None, alias="placements_access_token"),
                          db: Session = Depends(get_db)):
    # Generate a CSRF token in every call
    # csrf_token = token_urlsafe(16)
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
    csrf_tokens[csrf_token] = uuid.uuid4()

    # Define your parameters
    client_id = settings.CLIENT_ID
    response_type = "code"
    scope = "profile,ldap,id,cn,announcements"
    redirect_uri = "http://localhost:3000/auth"

    # Construct the redirect URL
    auth_url = f"https://login.it.teithe.gr/authorization?client_id={client_id}&response_type={response_type}&scope={scope}&redirect_uri={redirect_uri}&state={csrf_token}"

    return RedirectResponse(url=auth_url)


class TokenResponse:
    def __init__(self, access_token: str, refresh_token: int, user: dict):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user = user


async def fetch_token(code: str) -> TokenResponse | None:
    body = {
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.IEE_TOKEN_ENDPOINT, data=urlencode(body), headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }) as response:
                data = await response.json()
                return TokenResponse(**data)
    except aiohttp.ClientError as e:
        print("Token fetch error:", e)
        return None


async def fetch_profile(access_token: str) -> dict | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.IEE_PROFILE_ENDPOINT, headers={
                "x-access-token": access_token,
            }) as response:
                data = await response.json()
                print(data)
                return data
    except aiohttp.ClientError as e:
        print("Profile fetch error:", e)
        return None


@router.get("/verifyLogin", status_code=status.HTTP_200_OK)
async def auth(response: Response, code: str, state: str, db: Session = Depends(get_db)):
    print(code, " ", state, csrf_tokens)
    if state not in csrf_tokens:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
    del csrf_tokens[state]
    # If the token is valid, you would proceed with your logic, such as exchanging the code for an access token

    token_response = await fetch_token(code)
    if not token_response or not token_response.access_token:
        raise HTTPException(status_code=401, detail="Failed to obtain access token")
    user_profile = await fetch_profile(token_response.access_token)

    if not user_profile:
        raise HTTPException(status_code=401, detail="Failed to fetch user profile")

    user_data = {
        "first_name": user_profile["cn"],
        "last_name": user_profile["sn"],
        "AM": user_profile["am"]
    }
    print(user_data)
    print(user_data.keys())
    db_user = create_return_user_endpoint(user_data, db)
    admin_status = is_admin(db_user)
    access_token = create_access_token(data={"sub": str(db_user.id)})
    response.set_cookie(
        key="placements_access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True when deploying over HTTPS
        expires=expires_time,
        samesite="none",  # Might need to be "None" for cross-origin requests, remember to use Secure as well
    )

    user_response = UserCreateResponse(
        id=db_user.id,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        AM=db_user.AM,
        role=db_user.role.value,
        isAdmin=admin_status,
        placementsAccessToken=access_token,
        ihuAccessToken=token_response.access_token,
        ihuRefreshToken=token_response.refresh_token
    )
    return response
