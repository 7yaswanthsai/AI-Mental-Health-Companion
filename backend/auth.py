"""
Authentication module with JWT tokens and user management.
Supports login and registration with MongoDB user storage.
"""
import os
import jwt
import datetime
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from database.db_connection import get_database
from backend.utils.password_hasher import hash_password, verify_password
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# JWT + Password Config
# -----------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "mysupersecretkey")
JWT_ALGORITHM = "HS256"

# OAuth2 token flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# MongoDB collections
db = get_database()
users_collection = db["users"]


# -----------------------------
# Models
# -----------------------------
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    subject_id: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# -----------------------------
# Helper Functions
# -----------------------------
def generate_subject_id() -> str:
    """
    Generate a new subject_id in format S####.
    Finds the highest existing number and increments.
    """
    try:
        # Find the highest subject_id number
        users = list(users_collection.find({}, {"subject_id": 1}).sort("subject_id", -1).limit(1))
        if users and users[0].get("subject_id"):
            # Extract number from "S####" format
            last_id = users[0]["subject_id"]
            if last_id.startswith("S"):
                try:
                    num = int(last_id[1:])
                    return f"S{num + 1}"
                except ValueError:
                    pass
        # Default starting point
        return "S1001"
    except Exception as e:
        logger.error(f"Error generating subject_id: {e}")
        return "S1001"


def register_user(name: str, email: str, password: str, subject_id: str | None = None) -> dict:
    """
    Register a new user in MongoDB.
    
    Args:
        name: User's full name
        email: User's email address
        password: Plain text password (will be hashed)
        subject_id: Optional subject_id (auto-generated if not provided)
        
    Returns:
        dict: User document with subject_id
        
    Raises:
        HTTPException: If email already exists
    """
    try:
        # Check if email already exists
        existing = users_collection.find_one({"email": email.lower()})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate subject_id if not provided
        if not subject_id:
            subject_id = generate_subject_id()
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create user document
        user_doc = {
            "name": name,
            "email": email.lower(),
            "hashed_password": hashed_password,
            "subject_id": subject_id,
            "created_at": datetime.datetime.utcnow(),
        }
        
        # Insert into MongoDB
        users_collection.insert_one(user_doc)
        
        logger.info(f"User registered: {email} with subject_id {subject_id}")
        
        return {
            "name": user_doc["name"],
            "email": user_doc["email"],
            "subject_id": user_doc["subject_id"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


def authenticate_user(email: str, password: str) -> dict | None:
    """
    Authenticate a user by email and password.
    
    Args:
        email: User's email
        password: Plain text password
        
    Returns:
        dict: User document if authenticated, None otherwise
    """
    try:
        user = users_collection.find_one({"email": email.lower()})
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        return {
            "email": user["email"],
            "name": user.get("name", ""),
            "subject_id": user.get("subject_id", "S10"),
        }
    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        return None


def create_access_token(email: str) -> str:
    """
    Create a JWT access token.
    
    Args:
        email: User's email
        
    Returns:
        str: JWT token
    """
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    payload = {"sub": email, "exp": expiry}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        dict: User document
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = decoded.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Fetch user from database
        user = users_collection.find_one({"email": email.lower()})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "email": user["email"],
            "name": user.get("name", ""),
            "subject_id": user.get("subject_id", "S10"),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        logger.error(f"Token validation error: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
