from ..main import app
from ..routers.todos import get_db
from ..routers.auth import get_current_user
from fastapi import status 
from ..models import Todos
from .utils import (override_get_db,override_get_current_user,
                    client,TestingSessionLocal,test_todo)



app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=override_get_current_user

# Forcing application to run as a test

def test_read_all_authenticated(test_todo):
    response=client.get(url="/todos/")
    assert response.status_code==status.HTTP_200_OK
    assert response.json()==[{
        "title":"Learn to code!",
        "description":"Need to learn everyday!",
        "priority":5,
        "complete":False,
        "owner_id":1,
        "id":1
    }]
    
def test_read_one_authenticated(test_todo):
    response=client.get(url="/todos/todo/1")
    assert response.status_code==status.HTTP_200_OK
    assert response.json()=={
        "title":"Learn to code!",
        "description":"Need to learn everyday!",
        "priority":5,
        "complete":False,
        "owner_id":1,
        "id":1
    }
    
def test_read_one_authenticated_not_found(test_todo):
    response=client.get(url="/todos/todo/999")
    assert response.status_code==status.HTTP_404_NOT_FOUND
    assert response.json()=={
        "detail" : "Record does not exists"
    }

def test_create_todo(test_todo):
    request_data={
        "title": "New Todo",
        "description": "New Todo description",
        "priority": 5,
        "complete": False
    }
    
    # after posting in the test_todo, the id will be 2 because 
    # 1 was created and then deleted

    response=client.post(url="/todos/todo",json=request_data)
    assert response.status_code==status.HTTP_201_CREATED

    # Now check if the title is same for the same post id
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==2).first()
    assert model.title==request_data['title']
    assert model.description==request_data['description']
    assert model.priority==request_data['priority']
    assert model.complete==request_data['complete']



def test_update_todo(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description':"Need to learn everyday",
        'priority':5,
        'complete':False
    }

    # /todo_update/{todo_id}
    response=client.put(url="/todos/todo_update/1",json=request_data)
    assert response.status_code==status.HTTP_204_NO_CONTENT
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==1).first()
    assert model.title==request_data['title']

def test_update_todo_not_found(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description':"Need to learn everyday",
        'priority':5,
        'complete':False
    }

    # /todo_update/{todo_id}
    response=client.put(url="/todos/todo_update/999",json=request_data)
    print(response.json())
    assert response.status_code==status.HTTP_404_NOT_FOUND
    
def test_delete_todo(test_todo):
    response=client.delete(url="/todos/todo/delete/1")
    assert response.status_code==status.HTTP_204_NO_CONTENT
    
    # Check the content is deleted for the user
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==1).first()
    assert model is None

def test_delete_todo_not_found(test_todo):
    response=client.delete(url="/todos/todo/delete/999")
    assert response.status_code==status.HTTP_404_NOT_FOUND
    assert response.json()==dict(detail="Record not found for delete")
    