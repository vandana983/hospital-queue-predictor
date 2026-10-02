from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str = ""
    role: str = "receptionist"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileResponse(BaseModel):
    username: str
    full_name: str
    role: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if not auth_service.authenticate(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return LoginResponse(access_token=auth_service.create_token(payload.username.strip().lower()))


@router.post("/register", response_model=LoginResponse)
def register(payload: RegisterRequest):
    error = auth_service.register_staff(payload.username, payload.password, payload.full_name, payload.role)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return LoginResponse(access_token=auth_service.create_token(payload.username.strip().lower()))


def require_staff(authorization: str = Header(default="")) -> str:
    """FastAPI dependency: protects a route behind a valid staff JWT.
    Usage: def route(..., staff: str = Depends(require_staff))"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    username = auth_service.decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired session, please sign in again")
    return username


@router.get("/me", response_model=ProfileResponse)
def me(staff: str = Depends(require_staff)):
    profile = auth_service.get_profile(staff)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
