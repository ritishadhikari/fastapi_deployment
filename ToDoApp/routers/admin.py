from fastapi import APIRouter, Depends,HTTPException,Path
from ..models import Todos, Base
from sqlalchemy.orm import Session
from ..database import SessionLocal
from typing import Annotated
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user
from typing import Annotated

router=APIRouter(
    prefix="/admin",
    tags=['admin']
    )

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(path="/todo",status_code=status.HTTP_200_OK)
async def read_all(
    db: Session=Depends(dependency=get_db),
    user: dict=Depends(dependency=get_current_user)
    ):
    if user is None or user.get('user_role',"not an admin").casefold()!="admin":
        raise HTTPException(status_code=401, detail="Authentication Failed !")
    else:
        return db.query(Todos).all()

@router.delete(path="/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    db: Session=Depends(dependency=get_db),
    user: dict=Depends(dependency=get_current_user),
    todo_id:int=Path(gt=0)
):
    if user is None or user.get('user_role',"not an admin").casefold()!="admin":
        raise HTTPException(status_code=401, detail="Authentication Failed !")
    else:
        todo_model=db.query(Todos).filter(Todos.id==todo_id).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        db.query(Todos).filter(Todos.id==todo_id).delete()
        db.commit()