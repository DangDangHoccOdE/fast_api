from http.client import responses

from alembic.util import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from fastapi import status
from ..database import Base
from ..main import app
from ..routers.auth import get_current_user
from ..routers.todos import get_db
import pytest
from ..models import Todos

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread':False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit = False, autoflush= False, bind= engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username':'codingwithdang','id':1,'user_role':'admin'}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture()
def test_todo():
    todo = Todos(
        title = "Learn to code!",
        description = 'Need to learn everyday',
        priority = 5,
        complete = False,
        owner_id =1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield  todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

def test_read_all_authenticated():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title' : "Learn to code!",
                                'description' : 'Need to learn everyday',
                                'priority' : 5,
                                'complete' : False,
                                'owner_id' : 1}]

def test_read_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title' : "Learn to code!",
                                'description' : 'Need to learn everyday',
                                'priority' : 5,
                                'complete' : False,
                                'owner_id' : 1}]

def test_read_one_authenticated_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': "Todo not found"}

def test_create_todo(test_todo):
    request_data={
        'title': 'New todo',
        'description': 'New todo description',
        'priority':5,
        'complete':False,
    }

    response = client.post('/todo',json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

