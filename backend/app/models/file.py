from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class FileStatus(enum.Enum):
    pending_approval = "pending_approval"  #Waiting for admin approval (for child accounts)
    approved = "approved"                  #Approved and in production container (Passed scans and obtained needed approval)
    rejected = "rejected"                  #Rejected by admin, file dropped from quarantine


class PermissionType(enum.Enum):
    read = "read"        # Can view and download
    write = "write"      # Can view, download, and upload to shared folder


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)

    # The file's unique path in Azure Blob Storage
    object_key = Column(String, unique=True, nullable=False, index=True)

    # Display name shown to users (No UUID path, keeps interface clean)
    filename = Column(String, nullable=False)

    # MIME type (e.g. image/jpeg, video/mp4, audio/mp3), shows a preview, player or music player
    content_type = Column(String, nullable=False)

    # File size in bytes — used for quota tracking
    file_size = Column(BigInteger, nullable=False)

    # Foreign key linking file to its owner, enforced by the database
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Approval status — pending for child accounts, approved for everyone else
    status = Column(Enum(FileStatus), default=FileStatus.approved, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship back to the User model
    owner = relationship("User", back_populates="files")

    # Files shared with other users
    shared_access = relationship("SharedAccess", back_populates="file")


class SharedAccess(Base):
    __tablename__ = "shared_access"

    id = Column(Integer, primary_key=True, index=True)

    # Which file is being shared
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)

    # Who it is shared with
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # What they can do with it
    permission = Column(Enum(PermissionType), default=PermissionType.read, nullable=False)

    # When access was granted
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    file = relationship("File", back_populates="shared_access")
    shared_with_user = relationship("User")
