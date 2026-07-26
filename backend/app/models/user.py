#Imports the files.py relationship to the User model so the 2 models are properly linked
from sqlalchemy.orm import relationship
#Column, Integer, String, etc. — SQLAlchemy column types, each maps to a PostgreSQL data type
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime, Enum
#func: SQLAlchemy's way of calling database functions like 'now()' for timestamps
from sqlalchemy.sql import func
#Base: The base class from database.py that links this class to a database table
from app.database import Base
#enum: Python's built-in enum module for defining fixed sets of values
import enum

#Defining the 4 different roles as a fixed set, SQLAlchemy will create a PostgreSQL ENUM type from this,
#meaning the database itself enforces that a user's role can only ever be one of these four values.
class UserRole(enum.Enum):
    owner = "owner"
    admin = "admin"
    user = "user"
    child = "child"

#The User model, inheriting from Base tells SQLAlchemy this is a database table.
#SQLAlchemy will create a table called "users" in PostgreSQL from this class.
class User(Base):
    #Explicitly names the table "users" in the database.
    __tablename__ = "users"
    #Every user gets a unique integer ID. primary_key=True means this is the unique identifier for each row. index=True makes lookups by ID fast.
    id = Column(Integer, primary_key=True, index=True)
    #'unique=True': no two users can have the same email.'index=True': makes searching by email fast. 'nullable=False': email is required, can't be left empty
    email = Column(String, unique=True, index=True, nullable=False)
    #Same as email: unique, indexed, required.
    username = Column(String, unique=True, index=True, nullable=False)
    #Stores the bcrypt hashed version of the password. Never the plain text password — ever.
    hashed_password = Column(String, nullable=False)
    #Stores the user's role using the UserRole enum which was defined earlier, defaults to "user"
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    
    # Storage
        #'BigInteger', because file sizes in bytes can be very large numbers
        #storage_quota_bytes: how much storage this user is allowed. Default is 10GB (10737418240 bytes)
        #storage_used_bytes: how much they've actually used, starts at 0
    storage_quota_bytes = Column(BigInteger, default=10737418240)  # 10GB default
    storage_used_bytes = Column(BigInteger, default=0)
    
    # Account status
        #is_active: Owner or Admin can deactivate an account without deleting it
        #requires_upload_approval: the parental control flag. When True, an Admin must approve uploads before they're processed. Defaults to False for standard users, would be set to True for child accounts
    is_active = Column(Boolean, default=True)
    requires_upload_approval = Column(Boolean, default=False)
    
    # Timestamps
        #created_at: automatically set to the current time when the user is created
        #updated_at: automatically updates to the current time whenever the user record is changed
        #timezone=True — stores times in UTC, important for a platform that could have users across different timezones
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    #Relationship to files owned by this user
    files = relationship("File", back_populates="owner")
