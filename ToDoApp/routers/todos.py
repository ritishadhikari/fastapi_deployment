from fastapi import APIRouter, Depends,HTTPException,Path,Request
from ..models import Todos, Base
from sqlalchemy.orm import Session
from ..database import SessionLocal
from typing import Annotated
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user
from typing import Annotated
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates=Jinja2Templates(directory="TodoApp/templates")

router=APIRouter(
    prefix="/todos",
    tags=['todos']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TodoRequest(BaseModel):
    title: str=Field(min_length=3)
    description: str=Field(min_length=3, max_length=100)
    priority: int=Field(gt=0,lt=6)
    complete: bool 

def redirect_to_login():
    redirect_response=RedirectResponse(
        url="/auth/login-page",
        status_code=status.HTTP_302_FOUND
    )
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages
@router.get("/todo-page")
async def render_todo_page(request:Request, 
                           db:Annotated[Session,Depends(dependency=get_db)]):
    try:
        user=await get_current_user(token=request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        else:
            todos=db.query(Todos).filter(Todos.owner_id==user.get('id')).all()
            return templates.TemplateResponse("todo.html",
                                              {
                                                  "request":request,
                                                  "todos":todos,
                                                  "user":user
                                              }
            )
    except:
        return redirect_to_login()
    

@router.get("/add-todo-page")
async def render_todo_page(request:Request):
    try:
        user=await get_current_user(token=request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        else:
            return templates.TemplateResponse("add_todo.html",
                                              {
                                                  "request":request,
                                                  "user":user
                                              }
            )
    except:
        return redirect_to_login()

# does not work
@router.get(path="edit-todo-page/{todo_id}")
async def render_edit_todo_page(request:Request, 
                                todo_id:int,
                                db:Annotated[Session,Depends(dependency=get_db)]
                                ):
    try:
        user=await get_current_user(token=request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        else:
            todo=db.query(Todos).filter(Todos.id==todo_id).first()
            return templates.TemplateResponse("edit-todo.html",
                                              {
                                                  "request":request,
                                                  "todos":todo,
                                                  "user":user
                                              }
            )
    except:
        return redirect_to_login()



### Endoints
@router.get(path="/",status_code=status.HTTP_200_OK)
# async def read_all(db: Annotated[ Session, Depends(dependency=get_db) ]):
async def read_all(
    user:dict=Depends(dependency=get_current_user),
    db: Session = Depends(dependency=get_db) ):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id==user.get('id')).all()

@router.get(path="/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(
    user:dict=Depends(dependency=get_current_user) ,
    todo_id: int=Path(gt=0),
    db: Session = Depends(dependency=get_db),
    ):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication Failed")
    todo_model=db.query(Todos).filter(Todos.id==todo_id)\
        .filter(Todos.owner_id==user.get('id'))\
        .first()
    
    if todo_model is not None:
        return todo_model
    else: 
        raise HTTPException(status_code=404, detail="Record does not exists")

@router.post(path="/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request:TodoRequest,
                      user:Annotated[dict,Depends(dependency=get_current_user)],
                      db:Annotated[Session,Depends(dependency=get_db)]
                      ):
    print("coming here")
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication Failed")
    todo_model=Todos(**todo_request.model_dump(),owner_id=user.get('id'))
    db.add(instance=todo_model)
    db.commit()

@router.put("/todo_update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    todo_request:TodoRequest,
    todo_id:int=Path(gt=0),
    user:dict=Depends(dependency=get_current_user),
    db: Session = Depends(dependency=get_db)
    ):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication Failed")
    todo_model=db.query(Todos).filter(Todos.id==todo_id)\
            .filter(Todos.owner_id==user.get('id'))\
            .first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Record not found for update")
    else:
        todo_model.title=todo_request.title
        todo_model.complete=todo_request.complete
        todo_model.priority=todo_request.priority
        todo_model.description=todo_request.description
        db.add(todo_model)  # has the old id, and id being a pk, update the record
        db.commit()

@router.delete(path="/todo/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    todo_id:int=Path(gt=0),
    user:dict=Depends(dependency=get_current_user),
    db: Session = Depends(dependency=get_db)
    ):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication Failed")
    todo_model=db.query(Todos).filter(Todos.id==todo_id)\
        .filter(Todos.owner_id==user.get('id'))\
        .first()

    
    if todo_model is None:
        # "Entering the None block"
        raise HTTPException(status_code=404,detail="Record not found for delete")
    else:
        # "Entering the else block"
        db.query(Todos).filter(Todos.id==todo_id)\
            .filter(Todos.owner_id==user.get('id'))\
            .delete()
        db.commit()