from fastapi import APIRouter, Depends,HTTPException,Path
from ..models import Todos, Base,Users
from sqlalchemy.orm import Session
from ..database import SessionLocal
from typing import Annotated
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user
from typing import Annotated
from passlib.context import CryptContext

router=APIRouter(prefix="/user",tags=['user'])
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserVerification(BaseModel):
    password: str
    new_password: str=Field(min_length=6)

###############################################################################################
@router.get(path="/",status_code=status.HTTP_200_OK)
async def get_user(
    user:dict=Depends(dependency=get_current_user),
    db:Session=Depends(dependency=get_db)
    ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).filter(Users.id==user.get('id')).first()

@router.put(path="/password",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_verification: UserVerification,
    user:dict=Depends(dependency=get_current_user),
    db:Session=Depends(dependency=get_db),
    ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    else:
        user_model=db.query(Users).filter(Users.id==user.get('id')).first()
    
        if not bcrypt_context.verify(
            secret=user_verification.password,
            hash=user_model.hashed_password
            ):
            raise HTTPException(status_code=401, detail="Original Password is incorrect")
        else:
            user_model.hashed_password=bcrypt_context.hash(
                secret=user_verification.new_password
                )
            db.add(user_model)
            db.commit()

@router.put(path="/phonenumber/{phone_number}",status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    phone_number:str,
    user:dict=Depends(dependency=get_current_user),
    db:Session=Depends(dependency=get_db),
    ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model=db.query(Users).filter(Users.id==user.get('id')).first()
    user_model.phone_number=phone_number
    db.add(instance=user_model)
    db.commit()