import pytest
from app import app as flask_app
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.exceptions import NotFound, InternalServerError

if os.getenv('GITHUB_ACTIONS') == 'true':
    # Use environment variables directly in CI
    pass
else:
    # Local development - load from .env.test
    load_dotenv('env/.env.test')

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['MONGO_URI'] = os.getenv('TEST_MONGO_URI', 'mongodb://localhost:27017/test_geometric_journal_db')
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client(use_cookies = True)

@pytest.fixture
def db(app):
    with app.app_context():
        # Setup test database
        client = MongoClient(app.config['MONGO_URI'])
        db = client.get_database("test")
        
        # Clean up before tests
        db.users.delete_many({})
        db.entries.delete_many({})
        db.places.delete_many({})
        
        # Create a test user
        hashed_pw = bcrypt.hashpw(b'testpassword', bcrypt.gensalt())
        user_id = db.users.insert_one({
            'username': 'testuser',
            'password_hash': hashed_pw,
            'created_at': '2023-01-01'
        }).inserted_id
        
        # Create test places
        place1_id = db.places.insert_one({
            'name': 'Test Place 1',
            'address': '123 Test St',
            'coordinates': {'type': 'Point', 'coordinates': [-73.9857, 40.7484]},
            'created_at': '2023-01-01'
        }).inserted_id
        
        place2_id = db.places.insert_one({
            'name': 'Test Place 2',
            'address': '456 Test Ave',
            'coordinates': None,
            'created_at': '2023-01-01'
        }).inserted_id
        
        # Create test entries
        db.entries.insert_many([
            {
                'user_id': user_id,
                'place_id': place1_id,
                'date': '2023-01-01',
                'companions': ['Friend1', 'Friend2'],
                'rating': 4.5,
                'category': 'Restaurant',
                'review': 'Great place!',
                'created_at': '2023-01-01',
                'updated_at': '2023-01-01'
            },
            {
                'user_id': user_id,
                'place_id': place2_id,
                'date': '2023-01-02',
                'companions': [],
                'rating': 3.0,
                'category': 'Park',
                'review': 'Nice park',
                'created_at': '2023-01-02',
                'updated_at': '2023-01-02'
            }
        ])
        
        yield db
        
        # Clean up after tests
        client.drop_database('test_geometric_journal_db')
        client.close()

@pytest.fixture
def auth_client(client, db):
    db.users.insert_one({
        'username': 'testuser',
        'password_hash': bcrypt.hashpw(b'testpassword', bcrypt.gensalt()),
        'created_at': datetime.utcnow()
    })
    
    response = client.post('/login',
        data={'username': 'testuser', 'password': 'testpassword'},
        follow_redirects=True  # Critical for auth flow
    )
    
    # 3. Verify login succeeded
    assert response.status_code == 200

    # 3. Explicitly check session
    with client.session_transaction() as sess:
        sess['user_id'] = str(db.users.find_one()['_id'])
        sess.permanent = True 
    return client

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    # Override database name for tests
    monkeypatch.setenv('MONGO_DBNAME', 'test')