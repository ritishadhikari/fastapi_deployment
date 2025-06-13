from fastapi import FastAPI,Request, status
from .models import Todos, Base
from .database import engine 
from .routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


app=FastAPI()

@app.get(path="/healthy")
def health_check():
    return {"status":"healthy"}

Base.metadata.create_all(bind=engine)

# # Providing location to the templates (.html)
# templates=Jinja2Templates(directory="ToDoApp/templates")

# Providing location to the static files (ex. .css)
app.mount(path="/static",
          app=StaticFiles(directory="ToDoApp/static"), 
          name="static")

# The home page will show the screen from home.html
@app.get(path="/")
def test(request:Request):
    # return templates.TemplateResponse("home.html",{'request':request})
    return RedirectResponse(url="/todos/todo-page",
                            status_code=status.HTTP_302_FOUND)

app.include_router(router=admin.router)
app.include_router(router=auth.router)
app.include_router(router=users.router)
app.include_router(router=todos.router)


