from datetime import datetime, timedelta

import pytest
from fastapi import status
from jose import jwt
from fastapi import HTTPException

from ..routers.auth import authenticate_user, create_access_token, get_db, SECRET_KEY, ALGORITHM, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    
    authenticated_user = authenticate_user(test_user.username, "admin",db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username
    
    non_existent_user = authenticate_user('WrongUserName','admin',db)
    assert non_existent_user is None
    
    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is None
    
def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                               options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub':'testuser','id':1, 'role':'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await  get_current_user(token= token)
    assert  user == {'username':'testuser','id':1,"role":'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role':'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token = token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate user."
