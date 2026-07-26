from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.models.file import File, FileStatus, SharedAccess, PermissionType
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/files", tags=["files"])


# Response Models

#Defines what the API returns when someone requests when someone requests file information
#Only the object_key is included, the frontend requests a presigned download URL when it requires file access
class FileResponse(BaseModel):
    id: int
    object_key: str
    filename: str
    content_type: str
    file_size: int
    status: FileStatus
    owner_id: int

    class Config:
        from_attributes = True

#When sharing a file, the front end send this: who to share and permissions which they get
class ShareRequest(BaseModel):
    user_id: int
    permission: PermissionType

#Admin sends true to approve child's upload, false to reject it
class ApprovalRequest(BaseModel):
    approved: bool


# List all files owned by the current user
@router.get("/", response_model=List[FileResponse])
async def list_my_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #Returns only files owned by the logged in user, a user musn't see another user's files
    #through this endpoint, therefore, the filter enforces it at database level
    return db.query(File).filter(File.owner_id == current_user.id).all()


# List files shared with the current user
@router.get("/shared", response_model=List[FileResponse])
async def list_shared_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #Finds all SharedAccess records, where the current user is the recipient, then returns
    #the actual File objects from those records
    shared = db.query(SharedAccess).filter(
        SharedAccess.shared_with_user_id == current_user.id
    ).all()
    return [access.file for access in shared]


# List all pending approval files — Admin and Owner only
@router.get("/pending", response_model=List[FileResponse])
async def list_pending_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner, UserRole.admin))
):
    #Returns all files waiting for approval, this is what the admin dashboard displays when a child made an upload request which needs to be reviewed
    return db.query(File).filter(File.status == FileStatus.pending_approval).all()


# Approve or reject a pending file — Admin and Owner only
@router.patch("/{file_id}/approve", response_model=FileResponse)
async def approve_file(
    file_id: int,
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner, UserRole.admin))
):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    #Checks the file is actually pending before doing anything, then approves or denies using the admin's decision.
    #A rejected file won't be accessible for download but stays in the database as a record
    if file.status != FileStatus.pending_approval:
        raise HTTPException(
            status_code=400,
            detail="File is not pending approval"
        )

    if request.approved:
        file.status = FileStatus.approved
    else:
        file.status = FileStatus.rejected

    db.commit()
    db.refresh(file)
    return file


# Share a file with another user
@router.post("/{file_id}/share", response_model=dict)
async def share_file(
    file_id: int,
    request: ShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Only the file owner or an admin/owner can share files, standard user is unable to
    if file.owner_id != current_user.id and current_user.role not in [UserRole.owner, UserRole.admin]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to share this file"
        )

    # Check if access already exists, it it does, it updates the permission only 
    # This check is done to prevent multiple records of the same file
    existing = db.query(SharedAccess).filter(
        SharedAccess.file_id == file_id,
        SharedAccess.shared_with_user_id == request.user_id
    ).first()

    if existing:
        existing.permission = request.permission
        db.commit()
        return {"message": "Access updated successfully"}

    access = SharedAccess(
        file_id=file_id,
        shared_with_user_id=request.user_id,
        permission=request.permission
    )
    db.add(access)
    db.commit()
    return {"message": "File shared successfully"}


# Delete a file — owner only
@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if file.owner_id != current_user.id and current_user.role not in [UserRole.owner, UserRole.admin]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this file"
        )

    # Update owner's storage usage
    owner = db.query(User).filter(User.id == file.owner_id).first()

    #During file deletion, this deletes the record of that file
    owner.storage_used_bytes -= file.file_size

    db.delete(file)
    db.commit()
    return {"message": "File deleted successfully"}
