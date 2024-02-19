from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, SessionLocal
import models
from models import Users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

origins = ["*"]

# Add CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Which origins are allowed
    allow_credentials=True,  # Whether to support cookies
    allow_methods=["*"],  # Which HTTP methods are allowed
    allow_headers=["*"],  # Which HTTP headers are allowed
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get('/')
async def first_api():
    return {"message": "Hello there"}


@app.get('/users')
async def read_users(db: db_dependency):
    return db.query(Users).all()
