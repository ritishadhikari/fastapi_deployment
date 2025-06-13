from .utils import (override_get_db,override_get_current_user,
                    client,TestingSessionLocal,test_todo,test_user)
from ..routers.users import get_db,get_current_user,bcrypt_context
from starlette import status
from ..main import app
from ..models import Todos,Users

app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=override_get_current_user

def test_return_user(test_user):
    response=client.get(url="/user")
    assert response.status_code==status.HTTP_200_OK
    assert response.json()['email'] == 'ritishadhikaritest@email.com'
    assert response.json()['username'] == 'ritishadhikaritest'
    assert response.json()['first_name'] == 'ritish'
    assert response.json()['last_name'] == 'adhikaritest'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '8665537373'
 

def test_change_password_success(test_user):
    response=client.put(url="/user/password",json={"password":"ritishadhikaritest",
                                                  "new_password":"ritishadhikaritest1"})
    assert response.status_code==status.HTTP_204_NO_CONTENT

    
def test_change_password_invalid_current_password(test_user):
    response=client.put(url="/user/password",json={"password":"ritishadhikaritest1",  # 1 at the last should not be there
                                                  "new_password":"ritishadhikaritest2"})
    assert response.status_code==status.HTTP_401_UNAUTHORIZED
    assert response.json()==dict(detail="Original Password is incorrect")

def test_change_phone_number_success(test_user):
    response=client.put(url='/user/phonenumber/9803765342')
    assert response.status_code==status.HTTP_204_NO_CONTENT