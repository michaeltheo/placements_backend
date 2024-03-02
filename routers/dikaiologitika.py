import os
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from starlette import status

from crud.dikaiologitika_crud import create_dikaiologitika, get_files_by_user_id, get_all_files, update_file_path, \
    get_file_by_id, delete_file
from crud.user_crud import get_user_by_id, is_admin
from dependencies import get_db, get_current_user
from models import Users
from schemas.dikaiologitika_schema import DikaiologitikaCreate, Dikaiologitika
from schemas.response import ResponseWrapper, Message, FileAndUser

router = APIRouter(prefix='/dikaiologitika',
                   tags=['dikaiologitika'])


@router.post("/", response_model=ResponseWrapper, status_code=status.HTTP_200_OK)
async def upload_dikaiologitika(
        file: UploadFile = File(...),
        type: str = Form(...),  # Correctly receiving the type as part of the form data
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a PDF")

    # Ensuring the directory for the current user exists
    file_location = f"files/{current_user.id}/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Create the dikaiologitika record in the database
    dikaiologitika = create_dikaiologitika(
        db=db,
        dikaiologitika=DikaiologitikaCreate(type=type),
        user_id=current_user.id,
        file_path=file_location
    )

    return ResponseWrapper(
        data={"filename": file.filename, "file_location": file_location},
        message=Message(detail="File uploaded successfully")
    )


@router.get("/user/{user_id}/files", response_model=ResponseWrapper[FileAndUser],
            status_code=status.HTTP_200_OK)
async def read_files_for_user(
        user_id: int,
        db: Session = Depends(get_db),
        file_type: str = None,
        current_user: Users = Depends(get_current_user)
):
    # Ensure the requesting user is the owner of the files or an admin
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access these files.")

    files = get_files_by_user_id(db, user_id=user_id, file_type=file_type)
    user = get_user_by_id(db, user_id)
    files_and_user = FileAndUser(files=files, user=user)
    return ResponseWrapper(data=files_and_user, message=Message(detail="Files retrieved"))


@router.get("/admin/files", response_model=ResponseWrapper[List[Dikaiologitika]], status_code=status.HTTP_200_OK)
async def get_all_files_for_admin_endpoint(
        file_type: str = None,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource.")

    files = get_all_files(db, file_type=file_type)
    return ResponseWrapper(data=files, message=Message(detail="Files retrieved"))


@router.put("/{dikaiologitika_id}/", response_model=ResponseWrapper, status_code=status.HTTP_200_OK)
async def update_dikaiologitika_file(
        dikaiologitika_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a PDF")

    # Fetch the file record to ensure it exists and belongs to the current user
    dikaiologitika = get_file_by_id(db, dikaiologitika_id)
    if not dikaiologitika or dikaiologitika.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found or not accessible.")

    # Optional: Handle the old file (delete, archive, etc.)

    # Define the new file location and save the new file
    new_file_location = f"files/{current_user.id}/{file.filename}"
    os.makedirs(os.path.dirname(new_file_location), exist_ok=True)
    with open(new_file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Update the database record with the new file path
    update_file_path(db, dikaiologitika_id, new_file_location)

    return ResponseWrapper(
        data={"filename": file.filename, "file_location": new_file_location},
        message=Message(detail="File updated successfully")
    )


@router.delete("/{file_id}/", response_model=ResponseWrapper)
async def delete_file_endpoint(
        file_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if not is_admin(current_user):
        # Verify if the file belongs to the current user
        db_file = get_files_by_user_id(db, user_id=current_user.id, file_id=file_id)
        if not db_file:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to delete this file.")
    success = delete_file(db, file_id=file_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    return ResponseWrapper(data={}, message=Message(detail="File successfully deleted"))
