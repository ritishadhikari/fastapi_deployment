from fastapi import APIRouter,Depends,HTTPException, Request
from pydantic import BaseModel
from ..models import Users
from ..database import SessionLocal
from passlib.context import CryptContext
from starlette import status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta,datetime,timezone
from fastapi.templating import Jinja2Templates

router=APIRouter(
    prefix="/auth",
    tags=['auth']
)

SECRET_KEY="3f51b4aec2fb2fd2c1767b39be406319de964be63efdade05913500812f275fe"
ALGORITHM="HS256"


bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

oauth2_bearer=OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()



class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str

templates=Jinja2Templates(directory="ToDoApp/templates") 

##### Pages ####################
@router.get(path="/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse(
                                    "login.html", 
                                    {'request':request}
                                      )

@router.get(path="/register-page")
def render_login_page(request:Request):
    return templates.TemplateResponse(
                                    "register.html", 
                                    {'request':request}
                                      )


##### Endpoints ################

async def authenticate_user(username:str, password: str, db):
    user=db.query(Users).filter(Users.username==username).first()
    if user and bcrypt_context.verify(secret=password,hash=user.hashed_password):
        return user
    else: 
        return False

async def create_access_token(username:str, user_id: int, 
                              role:str, expires_delta: timedelta):
    # print(f"UserName:{username}, UserId:{user_id}")
    "Encoding a JWT"
    encode={"sub":username,"id":user_id,"role":role}
    expires=datetime.now(tz=timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(claims=encode,
                      key=SECRET_KEY,
                      algorithm=ALGORITHM)


async def get_current_user(
                    token: str=Depends(dependency=oauth2_bearer)
                    ):
    "Decoding a JWT"
    try:
        payload=jwt.decode(token=token,key=SECRET_KEY,algorithms=[ALGORITHM])
        username: str=payload.get('sub')  # fetches the username
        user_role:str=payload.get("role")
        user_id: int=payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
                )
        return {"username":username,"id":user_id,"user_role":user_role}
    except JWTError:
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                    )
##########################################################################################################

@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def create_user(
    create_user_request:CreateUserRequest,
    db:Session=Depends(dependency=get_db),
    ):
    
    create_user_model=Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password= bcrypt_context.hash(
            secret=create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number
    )

    db.add(instance=create_user_model)
    db.commit()

@router.post(path="/token", response_model=Token)
async def login_for_access_token(
    form_data:OAuth2PasswordRequestForm=Depends(),
    db: Session=Depends(dependency=get_db)
):
    user=await authenticate_user(username=form_data.username,
                           password=form_data.password,
                           db=db)
    
    # return "Failed Authentication" if not user else "Successful Authentication"
    if not user:
         raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                    )
    else:
        token=await create_access_token(
                                username=user.username,
                                user_id=user.id,
                                role=user.role,
                                expires_delta=timedelta(minutes=20)
                                )
        return {"access_token":token,"token_type":'bearer'}