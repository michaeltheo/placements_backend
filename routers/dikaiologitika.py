import os
from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import FileResponse

from crud.dikaiologitika_crud import create_dikaiologitika, get_files_by_user_id, get_all_files, update_file_path, \
    get_file_by_id, delete_file
from crud.user_crud import get_user_by_id, is_admin
from dependencies import get_db, get_current_user
from models import Users, DikaiologitikaType, Dikaiologitika as DikaiologitikaModels
from schemas.dikaiologitika_schema import DikaiologitikaCreate, Dikaiologitika
from schemas.response import ResponseWrapper, Message, FileAndUser
from schemas.user_schema import User

router = APIRouter(prefix='/dikaiologitika',
                   tags=['dikaiologitika'])


@router.get("/types", response_model=ResponseWrapper[List[str]], status_code=status.HTTP_200_OK)
async def get_dikaiologitika_types_endpoint():
    """
       Provides a list of all available dikaiologitika types defined in the system. This endpoint allows users
       to understand what types of documents can be uploaded or queried, enhancing usability and data consistency.

       Returns:
       - ResponseWrapper[List[str]]: A wrapped response containing a list of dikaiologitika types with a success message.
       """
    types_list = [e.value for e in DikaiologitikaType]
    return ResponseWrapper(data=types_list, message=Message(detail="List of all Dikaiologitika types"))


@router.post("/", response_model=ResponseWrapper[Dikaiologitika], status_code=status.HTTP_200_OK)
async def upload_dikaiologitika_endpoint(
        file: UploadFile = File(...),
        type: DikaiologitikaType = Form(...),
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
      Uploads a new dikaiologitika (document) to the system, associating it with the current user. The endpoint
      performs checks to ensure the uploaded file is a PDF and does not duplicate existing files (by name) under
      the same user and type. It creates a new record in the database with the document's metadata.

      Parameters:
      - file (UploadFile): The document file to upload, must be a PDF.
      - type (DikaiologitikaType): The type of document being uploaded, selected from predefined options.
      - db (Session): The database session for performing operations.
      - current_user (Users): The user making the request, associated with the uploaded document.

      Returns:
      - ResponseWrapper[Dikaiologitika]: A wrapped response containing the newly created dikaiologitika record and a success message.
      """
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a PDF")

    # Ensuring the directory for the current user exists
    file_location = f"files/{current_user.id}/{type.value}/{file.filename}"
    existing_file = db.query(DikaiologitikaModels).filter_by(file_path=file_location).first()
    if existing_file:
        # Handle the existing file scenario. For example, inform the user.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A file with the same name already exists.")
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Create the dikaiologitika record in the database
    dikaiologitika = create_dikaiologitika(
        db=db,
        dikaiologitika=DikaiologitikaCreate(type=type.value),
        user_id=current_user.id,
        file_path=file_location
    )

    return ResponseWrapper(
        data=dikaiologitika,
        message=Message(detail="File uploaded successfully")
    )


@router.get("/user/{user_id}/files", response_model=ResponseWrapper[FileAndUser],
            status_code=status.HTTP_200_OK)
async def read_files_for_user_endpoint(
        user_id: int,
        db: Session = Depends(get_db),
        file_type: Optional[DikaiologitikaType] = None,
        current_user: Users = Depends(get_current_user)
):
    """
     Retrieves files for a specified user, filtered optionally by file type. Access is restricted to ensure
     that users can only access their own files or, if the requester is an admin, any user's files.

     Parameters:
     - user_id (int): ID of the user whose files are to be retrieved.
     - db (Session): Database session dependency for database operations.
     - file_type (Optional[DikaiologitikaType]): Specific type of files to filter by, optional.
     - current_user (Users): The user making the request, to check for permissions.

     Returns:
     - A response wrapper containing a list of files and the user object, along with a success message.
     """
    # Ensure the requesting user is the owner of the files or an admin
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access these files.")

    files = get_files_by_user_id(db, user_id=user_id, file_type=file_type)
    user = get_user_by_id(db, user_id)
    files_models = [Dikaiologitika.from_orm(file) for file in files]
    user_model = User.from_orm(user)
    files_and_user = FileAndUser(files=files_models, user=user_model)
    return ResponseWrapper(data=files_and_user, message=Message(detail="Files retrieved"))


@router.get("/admin/files", response_model=ResponseWrapper[List[FileAndUser]], status_code=status.HTTP_200_OK)
async def get_all_files_for_admin_endpoint(
        file_type: DikaiologitikaType = None,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
       Allows an admin to retrieve all files stored in the system, along with information about the users who uploaded them,
       with an optional filter for file type. This endpoint is restricted to users with admin privileges.

       Parameters:
       - file_type (Optional[DikaiologitikaType]): To filter files by their type.
       - db (Session): The database session for querying.
       - current_user (Users): The currently authenticated user, checked for admin status.

       Raises:
       - HTTPException: If the current user is not authorized as an admin, an HTTPException with status code 403 (Forbidden)
         is raised, indicating that the user does not have permission to access this resource.

       Returns:
       - ResponseWrapper[List[FileAndUser]]: A list of files with their associated user information, optionally filtered by type,
         wrapped in a success response. Each item in the list represents a file and its uploader, facilitating comprehensive
         oversight for administrators.
       """
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource.")
    files_and_users = []
    files = get_all_files(db, file_type=file_type)
    for file in files:
        user = get_user_by_id(db, file.user_id)  # Assuming each file has a user_id attribute
        files_and_users.append(FileAndUser(files=[file], user=user))
    return ResponseWrapper(data=files_and_users, message=Message(detail="Files retrieved"))


@router.put("/{dikaiologitika_id}/", response_model=Message, status_code=status.HTTP_200_OK)
async def update_dikaiologitika_file_endpoint(
        dikaiologitika_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
    Updates the file path of an existing document. Only the document owner or an admin can perform this action.
    The new file must be a PDF.

    Parameters:
    - dikaiologitika_id (int): The ID of the document to update.
    - file (UploadFile): The new file to upload.
    - db (Session): The database session for querying and updates.
    - current_user (Users): The currently authenticated user, for access control.

    Returns:
    - Message: A success message indicating the file was updated.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a PDF")

    # Fetch the file record to ensure it exists and belongs to the current user
    dikaiologitika = get_file_by_id(db, dikaiologitika_id)
    if not dikaiologitika or dikaiologitika.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found or not accessible.")

    # Define the new file location
    new_file_location = f"files/{current_user.id}/{dikaiologitika.type.value}/{file.filename}"

    # Check if the new file name already exists to prevent overwriting
    if os.path.exists(new_file_location):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File with this name already exists.")

    # Optional: Delete the old file from the filesystem
    try:
        os.remove(dikaiologitika.file_path)
    except FileNotFoundError:
        # The file was not found, handle this case as needed
        pass
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Save the new file
    os.makedirs(os.path.dirname(new_file_location), exist_ok=True)
    with open(new_file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Update the database record with the new file path
    new_update_file = update_file_path(db=db, file_id=dikaiologitika_id, new_file_path=new_file_location)
    if not new_update_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    return Message(detail="File updated successfully")


@router.get("/download/{file_id}")
async def download_file_endpoint(file_id: int, db: Session = Depends(get_db),
                                 current_user: Users = Depends(get_current_user)):
    """
    Downloads a file based on its ID, with access control checks to ensure
    that only the file owner or an admin can download the file.

    Parameters:
    - file_id (int): The ID of the file to download.
    - db (Session): Dependency injection of the database session to access the database.
    - current_user (Users): The user making the request, obtained through dependency injection.

    Raises:
    - HTTPException: 403 Forbidden if the current user is neither the file owner nor an admin.
    - HTTPException: 404 Not Found if no file with the specified ID exists or the file is not accessible.

    Returns:
    - FileResponse: The requested file to be downloaded.
    """
    # Retrieve the file's metadata from the database, including the user_id of the owner
    file_record = db.query(DikaiologitikaModels).filter(DikaiologitikaModels.id == file_id).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    # Check if the current user is the owner of the file or an admin
    if file_record.user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to download this file.")

    # Construct the full path to the file
    file_path = file_record.file_path
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found on server.")

    return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type='application/octet-stream')


@router.delete("/{file_id}/", response_model=Message)
async def delete_file_endpoint(
        file_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """
     Deletes a specified file from the database and filesystem, accessible only by the file's owner or an admin.
     This endpoint ensures that unauthorized deletions are prevented by verifying the user's role or ownership of the file.

     Parameters:
     - file_id (int): The ID of the file to delete.
     - db (Session): The database session for performing operations.
     - current_user (Users): The user making the request, for validating permissions.

     Returns:
     - Message: A success message indicating the outcome of the deletion operation.
     """
    if not is_admin(current_user):
        # Verify if the file belongs to the current user
        db_file = get_files_by_user_id(db, user_id=current_user.id, file_id=file_id)
        if not db_file:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to delete this file.")
    success = delete_file(db, file_id=file_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    return Message(detail="File successfully deleted")
