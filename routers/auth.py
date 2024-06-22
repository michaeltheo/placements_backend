import secrets
import urllib
from datetime import timedelta, datetime, timezone
from typing import Optional, Dict, Union

import httpx
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response
from fastapi.responses import RedirectResponse
from jose import jwt
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from core.auth import create_access_token
from core.auth import verify_jwt
from core.config import settings
from core.messages import Messages
from crud.user_crud import get_user_by_id, create_user, get_user_by_AM, is_admin, split_full_name, determine_department
from dependencies import get_db
from schemas.response import Message, ResponseWrapper
from schemas.user_schema import UserCreateResponse, UserLoginResponse

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

# Calculate the expiration time as X minutes from the current time
expires_time = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES)
# Convert the expiration time from minutes to seconds
expires_in_seconds = settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60


@router.get("/redirect", status_code=status.HTTP_200_OK)
async def auth_redirect_endpoint(request: Request, response: Response):
    """
    Redirects the user to the authentication provider for authorization.

    Parameters:
    - request: The request object.

    Returns:
    - RedirectResponse: Redirects the user to the authentication provider.
    """
    redirect_uri = "http://localhost:3000/auth"
    scope = "profile,ldap,id,cn,announcements"
    client_id = settings.CLIENT_ID
    state = secrets.token_hex(16)
    request.session['oauth_state'] = state  # Store in session
    print(f"Session OAuth State: {request.session['oauth_state']}")

    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state
    }
    url = f"https://login.it.teithe.gr/authorization/?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@router.post('/login', response_model=ResponseWrapper[UserLoginResponse], status_code=status.HTTP_200_OK)
async def authenticate_login(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Authenticates the user login by fetching token and profile data from the authentication provider.

    Parameters:
    - request (Request): The request object.
    - response (Response): The response object.
    - db (Session): The database session.

    Returns:
    - ResponseWrapper[UserLoginResponse]: Response containing user details and tokens.
    """
    # Extract data from the request
    data = await request.json()
    # Retrieve state and code from the data
    state = data.get('state')
    code = data.get('code')
    # Retrieve OAuth state from the session
    session_state = request.session.get('oauth_state')
    # Validate the state parameter
    if session_state != state:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.INVALID_STATE)

    # Fetch Token from IHU IEE
    token = await fetch_token(code)
    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Messages.FETCH_TOKEN_ERROR)

    # Fetch profile data from IHU IEE using the obtained token
    profile_data = await fetch_profile(token)
    if profile_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Messages.FETCH_PROFILE_ERROR)

    # Retrieve academic number (AM) from profile data and check if the user exists in the database
    am = profile_data.get('am')
    db_user = get_user_by_AM(db, am)
    if db_user:
        # Determine if the user is an admin
        admin_status = is_admin(db_user)
        # Create access token for the user
        access_token = create_access_token(data={"sub": str(db_user.id)})
        # Set access token as cookie
        response.set_cookie(
            key="placements_access_token",
            value=access_token,
            httponly=False,
            expires=expires_time,
            secure=False,
            max_age=expires_in_seconds,
            samesite="lax",
        )
        # Create response for existing user
        user_response = UserCreateResponse(
            id=db_user.id,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            AM=db_user.AM,
            reg_year=db_user.reg_year,
            fathers_name=db_user.fathers_name,
            telephone_number=db_user.telephone_number,
            email=db_user.email,
            role=db_user.role.value,
            department=db_user.department,
            isAdmin=admin_status,
        )
    else:
        # Split full name into first name and last name
        first_name, last_name = split_full_name(profile_data.get('cn;lang-el'))
        # Find students department
        department = determine_department(am)
        # Create new user data from profile data
        new_user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'AM': am,
            'department': department,
            'reg_year': profile_data.get('regyear'),
            'fathers_name': profile_data.get('fathersname;lang-el'),
            'telephone_number': profile_data.get('telephoneNumber'),
            'email': profile_data.get('mail')
        }
        # Create new user in the database
        new_user = create_user(db=db, user=new_user_data)
        # Determine if the new user is an admin and generate a new access token
        admin_status = is_admin(new_user)
        access_token = create_access_token(data={"sub": str(new_user.id)})
        # Set access token as cookie
        response.set_cookie(
            key="placements_access_token",
            value=access_token,
            httponly=False,
            expires=expires_time,
            secure=False,
            max_age=expires_in_seconds,
            samesite="lax",
        )
        user_response = UserCreateResponse(
            id=new_user.id,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            reg_year=new_user.reg_year,
            fathers_name=new_user.fathers_name,
            telephone_number=new_user.telephone_number,
            email=new_user.email,
            AM=new_user.AM,
            department=new_user.department,
            role=new_user.role.value,
            isAdmin=admin_status,
        )
    # Construct tokens dictionary
    tokens = {
        "placement_token": access_token,
        "ihu_access_token": token.get('access_token'),
        "ihu_refresh_token": token.get('refresh_token')
    }
    login_response = UserLoginResponse(user=user_response, tokens=tokens)

    return ResponseWrapper(data=login_response, message=Message(detail=Messages.SUCCESSFULLY_LOGIN))


@router.get("/verify-token", response_model=ResponseWrapper[UserCreateResponse], status_code=status.HTTP_200_OK)
def verify_token_endpoint(access_token: str = Cookie(None, alias="placements_access_token"),
                          db: Session = Depends(get_db)):
    """
    Verifies the access token and returns user information.

    Parameters:
    - access_token (str, optional): The access token obtained during authentication.
    - db (Session): The database session.

    Returns:
    - ResponseWrapper[UserCreateResponse]: Response containing user details.
    """
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="")
    try:
        # Verify the JWT and decode it to get the user information
        payload = verify_jwt(access_token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.INVALID_TOKEN)
        # Fetch the user from the database using the user ID
        user = get_user_by_id(db, int(user_id))
        admin_status = is_admin(user)
        user_response_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "AM": user.AM,
            "reg_year": user.reg_year,
            "fathers_name": user.fathers_name,
            "telephone_number": user.telephone_number,
            "email": user.email,
            "department": user.department,
            "role": user.role.value,
            "isAdmin": admin_status,
            "accessToken": access_token
        }
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.USER_NOT_FOUND)
            # Convert fields to None if they are None in the database
        for field in ["fathers_name", "telephone_number", "reg_year", "email"]:
            if user_response_data[field] is None:
                user_response_data[field] = None

        user_response = UserCreateResponse(**user_response_data)
        # Return the custom message
        return ResponseWrapper(data=user_response, message=Message(detail=Messages.SUCCESSFULLY_LOGIN))
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.TOKEN_VALIDATION_ERROR)


async def fetch_token(code: str) -> Optional[Dict[str, str]]:
    """
    Fetches the access token from the IHU IEE authentication provider.

    Parameters:
    - code (str): The authorization code obtained during the authentication flow.

    Returns:
    - Optional[Dict[str, str]]: Dictionary containing token data.
    """
    token_endpoint = "https://login.iee.ihu.gr/token"
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    grant_type = 'authorization_code'

    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type,
        "code": code,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_endpoint, data=body)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


async def fetch_profile(token_data: dict) -> Optional[Dict[str, Union[str, int]]]:
    """
    Fetches the user profile data from the IHU IEE profile endpoint.

    Parameters:
    - token_data (dict): Dictionary containing token data.

    Returns:
    - Optional[Dict[str, Union[str, int]]]: Dictionary containing profile data.
    """
    access_token = token_data.get('access_token')
    if not access_token:
        return None

    profile_endpoint = "https://api.iee.ihu.gr/profile"
    headers = {"x-access-token": access_token}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(profile_endpoint, headers=headers)
            response.raise_for_status()
            profile_data = response.json()
            return profile_data
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
