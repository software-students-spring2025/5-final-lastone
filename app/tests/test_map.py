def test_map_page_unauthorized(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200

def test_map_page_authorized(auth_client):
    response = auth_client.get('/')
    assert response.status_code == 200
    assert b'Map' in response.data
    assert b'Test Place 1' in response.data
    assert b'Test Place 2' in response.data

def test_map_points_data(auth_client, db):
    response = auth_client.get('/')
    print(response.data.decode('utf-8'))

    assert b'points = [' in response.data
    assert b'Test Place 1' in response.data 
    assert b'123 Test St' in response.data 

def test_recent_entries_display(auth_client):
    auth_client.post('/entries/add', data={
        'place_name': 'Test_Recent_Entries',
        'place_address': '123 Test',
        'date': '2025-04-28',
        'companions': 'test1',
        'rating': '5',
        'category': 'Museum',
        'review': 'Excellent Test_Recent_Entries',
        'latitude': '32.2345',
        'longitude': '-78.9876'
    })
    response = auth_client.get('/')
    assert b'Test_Recent_Entries' in response.data
    assert b'2025-04-28' in response.data