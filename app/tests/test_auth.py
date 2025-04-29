def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_successful_login(client, db):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert '/' in response.headers['Location']

    with client.session_transaction() as session:
        assert 'user_id' in session

def test_failed_login(client):
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_create_account_page(client):
    response = client.get('/create_account')
    assert response.status_code == 200
    assert b'Create Account' in response.data

def test_create_account_success(client, db):
    response = client.post('/create_account', data={
        'username': 'newuser',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Should redirect to login page

def test_create_account_password_mismatch(client):
    response = client.post('/create_account', data={
        'username': 'newuser',
        'password': 'newpassword',
        'confirm_password': 'differentpassword'
    })
    assert response.status_code == 200
    assert b'Passwords do not match' in response.data

def test_create_account_existing_username(client, db):
    response = client.post('/create_account', data={
        'username': 'testuser',  # Already exists
        'password': 'password',
        'confirm_password': 'password'
    })
    assert response.status_code == 200
    assert b'Username already exists' in response.data