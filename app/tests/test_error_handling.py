# test_error_handling.py
import pytest
from bson.objectid import ObjectId

def test_invalid_entry_id_view(auth_client):
    """Test viewing an entry with invalid ID format"""
    invalid_id = "invalid_id_123"
    response = auth_client.get(f'/entries/edit/{invalid_id}')
    assert response.status_code == 400
    assert b"Invalid entry ID" in response.data

def test_nonexistent_entry_view(auth_client, db):
    """Test viewing a non-existent entry"""
    fake_id = ObjectId()  # Generates a new ID that doesn't exist
    response = auth_client.get(f'/entries/edit/{fake_id}')
    assert response.status_code == 404
    assert b"Entry not found" in response.data

def test_edit_entry_unauthorized(auth_client, db):
    """Test editing an entry that belongs to another user"""
    # Create a second test user
    other_user_id = db.users.insert_one({
        'username': 'otheruser',
        'password_hash': 'dummyhash',
        'created_at': '2023-01-01'
    }).inserted_id
    
    # Create an entry belonging to the other user
    place_id = db.places.insert_one({
        'name': 'Unauthorized Place',
        'address': '789 Unauthorized St',
        'created_at': '2023-01-01'
    }).inserted_id
    
    other_entry_id = db.entries.insert_one({
        'user_id': other_user_id,
        'place_id': place_id,
        'date': '2023-01-03',
        'review': 'Private review',
        'created_at': '2023-01-03'
    }).inserted_id
    
    # Try to edit this entry with our auth_client (logged in as testuser)
    response = auth_client.post(f'/entries/edit/{other_entry_id}', 
                              data={'review': 'Hacked review'},
                              follow_redirects=True)
    assert response.status_code == 404
    assert b"don't have permission" in response.data

def test_invalid_login(client, db):
    """Test login with invalid credentials"""
    # Test with wrong password
    response = client.post('/login', 
                         data={'username': 'testuser', 'password': 'wrongpassword'},
                         follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    
    # Test with non-existent username
    response = client.post('/login',
                         data={'username': 'nonexistent', 'password': 'testpassword'},
                         follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

def test_create_account_errors(client, db):
    """Test error cases for account creation"""
    # Test missing fields
    response = client.post('/create_account',
                         data={'username': '', 'password': 'test', 'confirm_password': 'test'},
                         follow_redirects=True)
    assert b"All fields are required" in response.data
    
    # Test password mismatch
    response = client.post('/create_account',
                         data={'username': 'newuser', 'password': 'test', 'confirm_password': 'mismatch'},
                         follow_redirects=True)
    assert b"Passwords do not match" in response.data
    
    # Test existing username
    response = client.post('/create_account',
                         data={'username': 'testuser', 'password': 'test', 'confirm_password': 'test'},
                         follow_redirects=True)
    assert b"Username already exists" in response.data

def test_add_entry_missing_fields(auth_client):
    """Test adding an entry with missing required fields"""
    response = auth_client.post('/entries/add',
                             data={'place_name': '', 'place_address': '', 'review': ''},
                             follow_redirects=True)
    assert response.status_code == 200
    assert b"Missing required fields" in response.data

def test_invalid_date_format(auth_client):
    """Test adding an entry with invalid date format"""
    response = auth_client.post('/entries/add',
                             data={
                                 'place_name': 'Test',
                                 'place_address': '123 St',
                                 'date': 'invalid-date',
                                 'review': 'Test review'
                             },
                             follow_redirects=True)
    assert b"Invalid date format" in response.data