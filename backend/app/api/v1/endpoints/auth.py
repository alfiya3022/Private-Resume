from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.services.auth_service import auth_service
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new candidate user."""
    return auth_service.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate candidate and issue a JWT bearer token."""
    user = auth_service.authenticate_user(
        db=db, email=login_in.email, password=login_in.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Fetch the currently authenticated user's profile."""
    return current_user
