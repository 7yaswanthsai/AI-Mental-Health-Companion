import os
import jwt
import datetime
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext

# -----------------------------
# JWT + Password Config
# -----------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "mysupersecretkey")
JWT_ALGORITHM = "HS256"

# Use sha256 hashing (no bcrypt issues)
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# OAuth2 token flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# -----------------------------
# Mock User Database
# -----------------------------
MOCK_USER = {
    "email": "test@pai.com",
    "hashed_password": pwd_context.hash("123456")  # <-- works always
}

# -----------------------------
# Helper Functions
# -----------------------------
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def authenticate_user(email, password):
    if email != MOCK_USER["email"]:
        return None
    if not verify_password(password, MOCK_USER["hashed_password"]):
        return None
    return {"email": email}

def create_access_token(email):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    payload = {"sub": email, "exp": expiry}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# -----------------------------
# Auth Dependency
# -----------------------------
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = decoded.get("sub")
        if email != MOCK_USER["email"]:
            raise HTTPException(status_code=401, detail="Invalid token user")
        return {"email": email}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
