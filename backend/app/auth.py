from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole

# Configuration
#the secret used to sign the JWT tokens, so that anyone with said key could forge tokens,
#so in production, this will be a long random string stored in the .env file, and not hardcoded.
SECRET_KEY = "changethisbeforeproduction"
#HS256 is the signing algorithm
ALGORITHM = "HS256"
#Tokens expire after half an hour, after that, the user needs to login again, limits damage if token is stolen
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
#A hashing context using bcrypt, the tool used for hashing and verifying passwords throughout the app
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
#Indicates to FastAPI where users will obtain their tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#This functions takes a plain text password and returns a bcrypt hash, called when as user registers
#It's very IMPORTANT that the plain text password is never stored.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#This function verifies what the user typed at login and the stored hash and returns true if match
#(bcyrpt handles the comparison securely, no hashs are unhashed)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#This function creates a JWT token, taking a dictionary of data (user's ID & role),
#adds an expiry time, & signs it with the SECRET_KEY, a token string is returned to the user post-login
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#This function, (which is most important in the class), is used by every protected route
#When a request with a token is made, the token is decoded using SECRET_KEY,
#Extracts the user_ID from the payload, user looked up in the database and user object returned if all is good
#In the case of something going wrong, an unauthorised error 401 is raised
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

#This the authorization layer on top of authentication, taking 1 or more roles,
#returns a function that checks if the current user has one of those roles and error 401 if not
def require_role(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return current_user
    return role_checker
