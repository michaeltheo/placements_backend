import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import models
from core.config import settings
from crud.otp_crud import cleanup_expired_otps
from database import engine, SessionLocal
from routers.auth import router as auth_router
from routers.companies import router as companies_router
from routers.company_answers import router as company_answers_router
from routers.dikaiologitika import router as dikaiologitika_router
from routers.internship import router as internship_router
from routers.otp import router as otp_router
from routers.questions import router as question_router
from routers.user_answers import router as user_answers_router
from routers.users import router as users_router

# Define allowed origins for CORS
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app = FastAPI()

# Set cookie expiration time
cookie_expire_time = settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Accept", 'token'],
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

# Background task for cleanup OTP
# Background task for cleanup OTP
async def schedule_cleanup_otp(interval: int):
    while True:
        await asyncio.sleep(interval)
        db = SessionLocal()
        try:
            cleanup_expired_otps(db)
        finally:
            db.close()


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_cleanup_otp(3600))  # 1 Hour


# Include routers
app.include_router(users_router)
app.include_router(dikaiologitika_router)
app.include_router(question_router)
app.include_router(user_answers_router)
app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(internship_router)
app.include_router(otp_router)
app.include_router(company_answers_router)

# Create database tables
models.Base.metadata.create_all(bind=engine)
