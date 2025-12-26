from fastapi import APIRouter, Depends, HTTPException,status
from database import get_db
import models.models as models
from oauth import get_current_user
from schemas import UserCreate, UserOut
from sqlalchemy.orm import Session

from utils import hash_pass


router = APIRouter(prefix = '/create_agent',tags=['Agent'])

def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.post('/',response_model=UserOut)
def create_agent(user: UserCreate,db : Session = Depends(get_db),current_user = Depends(require_admin)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_pass = hash_pass(user.password)

    new_agent = models.User(
        name=user.name,
        email=user.email,
        password=hashed_pass,
        role=models.UserRole.agent
    )

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    return new_agent