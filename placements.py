from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers.users import router as users_router

app = FastAPI()

app.include_router(users_router)

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


@app.get('/')
async def first_api():
    return {"message": "Hello there"}
