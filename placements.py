from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import models
from core.config import settings
from database import engine
from routers.auth import router as auth_router
from routers.companies import router as companies_router
from routers.dikaiologitika import router as dikaiologitika_router
from routers.internship import router as internship_router  # Corrected the import name
from routers.questions import router as question_router
from routers.user_answers import router as user_answers_router
from routers.users import router as users_router

# Define allowed origins for CORS
origins = ["http://localhost:3000"]

app = FastAPI()

# Set cookie expiration time
cookie_expire_time = settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="auth_session",
    max_age=cookie_expire_time,
    # TODO:  Change to `True` in production with HTTPS
    https_only=False,
    same_site='lax',
)

# Uncomment and configure TrustedHostMiddleware for additional security in production
# app.add_middleware(
#     TrustedHostMiddleware, allowed_hosts=["localhost"]
# )

# Include routers
app.include_router(users_router)
app.include_router(dikaiologitika_router)
app.include_router(question_router)
app.include_router(user_answers_router)
app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(internship_router)

# Create database tables
models.Base.metadata.create_all(bind=engine)
