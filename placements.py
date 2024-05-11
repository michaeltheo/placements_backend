from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import models
from core.config import settings
from database import engine
from routers.auth import router as auth_router
from routers.dikaiologitika import router as dikaiologitika_router
from routers.questions import router as question_router
from routers.user_answers import router as user_answers_router
from routers.users import router as users_router

origins = ["http://localhost:3000"]  # Update this as necessary

app = FastAPI()
cookie_expire_time = settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Enable credentials for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="auth_session",  # Use a unique cookie name
    max_age=cookie_expire_time,  # Example: set max age for the session cookie, in seconds
    https_only=False,  # Change to `True` in production with HTTPS
    same_site='lax',
)
# app.add_middleware(
#     TrustedHostMiddleware, allowed_hosts=["localhost"]
# )
app.include_router(users_router)
app.include_router(dikaiologitika_router)
app.include_router(question_router)
app.include_router(user_answers_router)
app.include_router(auth_router)

models.Base.metadata.create_all(bind=engine)
