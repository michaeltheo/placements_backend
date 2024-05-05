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

app = FastAPI()

app.include_router(users_router)
app.include_router(dikaiologitika_router)
app.include_router(question_router)
app.include_router(user_answers_router)
app.include_router(auth_router)

models.Base.metadata.create_all(bind=engine)

origins = ["http://localhost:3000"]

# Add CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Which origins are allowed
    allow_credentials=True,  # Whether to support cookies
    allow_methods=["*"],  # Which HTTP methods are allowed
    allow_headers=["*"],  # Which HTTP headers are allowed
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="CSRF_TOKEN",  # Name of the cookie to store session data
    max_age=10000,  # Optional: set max age for the session cookie, in seconds
    https_only=False,  # Set to True in production to send cookie only over HTTPS
)
