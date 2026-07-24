from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["users"])


## Response Models

#This function acts as an expanded version of the UserResponse from auth.py
#It invludes info so the dashboard can show how much space a user has and how much they've used
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    storage_quota_bytes: int
    storage_used_bytes: int

    class Config:
        from_attributes = True

#The following 3 functions are simple request models, each defining what is sent to the frontend
#They are seperate, in order to make each endpoint take the bare minimum of what is needed
class UpdateQuotaRequest(BaseModel):
    storage_quota_bytes: int


class UpdateRoleRequest(BaseModel):
    role: UserRole


class UpdateUploadApprovalRequest(BaseModel):
    requires_upload_approval: bool


# Get current logged in user
#The simplest endpoint, returns the currently logged in user and uses get_current_user from auth.py
#which validates the JWT token and returns the user object
#No database query needed. get_current_user already fetched
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# List all users — Owner and Admin only
#This function returns all users on the instance
#Which can only be accesses by users with Owner or Admin roles
@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner, UserRole.admin))
):
    return db.query(User).all()


# Update a user's storage quota — Owner only
#This function updates a user's storage quota, only Owner users can access this.
#The important safety check here is that quota cannot be set lower than storage already in use
@router.patch("/{user_id}/quota", response_model=UserResponse)
async def update_quota(
    user_id: int,
    request: UpdateQuotaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.storage_quota_bytes < user.storage_used_bytes:
        raise HTTPException(
            status_code=400,
            detail="Cannot set quota below current usage"
        )

    user.storage_quota_bytes = request.storage_quota_bytes
    db.commit()
    db.refresh(user)
    return user


# Update a user's role — Owner only
#Updates a user's role, feature only available to Owner, also user with Owner role cannot be demoted
@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_role(
    user_id: int,
    request: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.owner:
        raise HTTPException(
            status_code=400,
            detail="Cannot change the role of the Owner"
        )

    user.role = request.role
    db.commit()
    db.refresh(user)
    return user


# Toggle upload approval requirement — Owner and Admin only
#This is for the parental control upload gate, which can only be accessed by Admin or Owner users
#When is set to true, that user's uploads require approval from admin or owner before processing
#This only takes place when a child account tries to upload
@router.patch("/{user_id}/upload-approval", response_model=UserResponse)
async def update_upload_approval(
    user_id: int,
    request: UpdateUploadApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner, UserRole.admin))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.requires_upload_approval = request.requires_upload_approval
    db.commit()
    db.refresh(user)
    return user


# Deactivate or reactivate a user account — Owner and Admin only
#Someone always needs full access to the instance,
#a deactivated user gets a 403 error when they try to log in, but files remain untouched
@router.patch("/{user_id}/active", response_model=UserResponse)
async def update_active_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner, UserRole.admin))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.owner:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate the Owner account"
        )

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
