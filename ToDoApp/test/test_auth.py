from .utils import (override_get_db,override_get_current_user,
                    client,TestingSessionLocal,test_todo,test_user)
from ..routers.auth import (get_db, 
                            authenticate_user, 
                            create_access_token,
                            SECRET_KEY, ALGORITHM,
                            get_current_user
                            )
from jose import jwt
from datetime import timedelta
from ..main import app
import pytest
from starlette import status
from fastapi import HTTPException

app.dependency_overrides[get_db]=override_get_db

async def test_authenticate_user(test_user):
    db=TestingSessionLocal()
    authenticated_user=await authenticate_user(
        username=test_user.username,
        password="ritishadhikaritest",
        db=db)
    assert authenticated_user is not None
    assert authenticated_user.username==test_user.username

    non_authenticated_user=await authenticate_user(
        username="wrong_user",
        password="ritishadhikaritest",
        db=db
    )
    assert non_authenticated_user is False

    wrong_password_user= await authenticate_user(
        username=test_user.username,
        password="wrong_password",
        db=db
    )
    assert wrong_password_user is False

async def test_create_access_token():
    username='testuser'
    user_id=1
    role="user"
    expires_delta=timedelta(days=1)

    token=await create_access_token(
        username=username,
        user_id=user_id,
        role=role,
        expires_delta=expires_delta
    )

    decoded_token=jwt.decode(token=token,key=SECRET_KEY,
                             algorithms=[ALGORITHM],
                             options={'verify_signature':False})
    
    assert decoded_token['sub']==username
    assert decoded_token['id']==user_id
    assert decoded_token['role']==role

@pytest.mark.asyncio  # non mandatory
async def test_get_current_user_valid_token():
    encode={'sub':'testuser','id':1,'role':'admin'}
    token=jwt.encode(claims=encode,
                     key=SECRET_KEY,
                     algorithm=ALGORITHM)
    user=await get_current_user(token=token)
    assert user=={"username":'testuser',"id":1,"user_role":'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode={'role':'user'}
    token=jwt.encode(claims=encode,
                     key=SECRET_KEY,
                     algorithm=ALGORITHM)
    
    # writting with a context manager since get_current_user is not written 
    # with fastapi (@app) whose errors could be directly handled through FastAPI
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)


    assert excinfo.value.status_code==status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail=='Could not validate user.'