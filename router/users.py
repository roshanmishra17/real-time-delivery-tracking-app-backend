from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
import models.models as models
from schemas import UserCreate, UserOut
from utils import hash_pass

router = APIRouter(prefix='/users',tags=['Users'])

@router.post('/',response_model=UserOut,status_code=status.HTTP_201_CREATED)
def create_user(user : UserCreate,db : Session = Depends(get_db)):
    user_exist = db.query(models.User).filter(models.User.email == user.email).first()
    if user_exist :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = hash_pass(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=models.UserRole.customer
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get('/{id}',response_model=UserOut)
def get_user(id : int,db : Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:     
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'The User with id {id} does not exist')
    
    return user
