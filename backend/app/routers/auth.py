from fastapi import APIRouter, Depends, HTTPException, status
#OAuth2PasswordRequestForm, a built-in FastAPI form which expects a username & password
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
#EmailStr, a Pydantic type that automatically validates that the email is in valid format
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.user import User, UserRole
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


# Request / Response models
#(Defines what the frontend must send to register)
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

#What the login endpoint returns the JWT token and type 
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

#What the register endpoint returns the newly created user's details
#(The user's password isn't, from_attributes = true allows Pydantic to read from a SQLAlchemy object)
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

#A POST endpoint at /auth/register, taking the registration data and a database session
@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email already exists, if it does, returns a 400 Bad error request
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # same process but with the username instead
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Check if this is the first user, (if the current no. of users is 0),  makes them Owner
    user_count = db.query(User).count()
    role = UserRole.owner if user_count == 0 else UserRole.user

    #Create the user object, hashes password and stores it into the database,
    #commits the transaction, and returns the new user
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

#A POST endpoint at /auth/login, uses OAuth2PasswordRequestForm which expects a standard username/password form submission 
@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()

    #Verify user exists and password is correct, if user doesn't exit or password is wrong, error 401 returned (kept vague to prevent an attacker from knowing if a username exists) 
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account is active, if the account had been disabled by Admin or Owner, error 403 returned (instead of error 401, the credentials are correct but access had been denied)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Create and return the access token and user's ID as the payload to frontend
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer")
