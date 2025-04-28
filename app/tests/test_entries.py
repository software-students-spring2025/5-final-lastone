def test_my_entries_unauthorized(client):
    response = client.get('/entries', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Should redirect to login page

def test_my_entries_authorized(auth_client):
    # First verify session exists
    response = auth_client.get('/entries')
    print(response.data)
    assert response.status_code == 200

def test_add_entry_page(auth_client):
    response = auth_client.get('/entries/add')
    assert response.status_code == 200

def test_add_entry_success(auth_client, db):
    print(f"Using MongoDB: {db.client.address}")  # Should show localhost:27017
    print(f"Database name: {db.name}")  # Should be 'test_db' or similar    
    response = auth_client.post('/entries/add', data={
        'place_name': 'New Place',
        'place_address': '789 New St',
        'date': '2023-03-01',
        'companions': 'Friend1, Friend2',
        'rating': '5',
        'category': 'Museum',
        'review': 'Excellent museum',
        'latitude': '40.7128',
        'longitude': '-74.0060'
    })

    print("All entries:", list(db.entries.find({})))
    new_entry = db.entries.find_one({
        'review': 'Excellent museum'
    })
    
    assert new_entry is not None, "Entry not found in database"
    assert new_entry['rating'] == 5.0  # Check type conversion
    assert 'Friend1' in new_entry['companions']  # Check array conversion
    
    print("Places:", list(db.places.find({})))
    place = db.places.find_one({
        'name': 'New Place',
        'address': '789 New St'
    })
    assert place is not None, "Place not created in database"
    assert place['coordinates'] == {
        'type': 'Point',
        'coordinates': [-74.0060, 40.7128]  # Note: MongoDB uses [lng, lat]
    }

def test_add_entry_missing_fields(auth_client):
    response = auth_client.post('/entries/add', data={
        'place_name': '',  # Missing required field
        'place_address': '789 New St',
        'date': '2023-03-01',
        'review': 'Excellent museum'
    })
    assert response.status_code == 200
    assert b'Missing required fields' in response.data

def test_edit_entry_page(auth_client, db):
    # Get an entry ID from the database
    entry = db.entries.find_one({'review': 'Great place!'})
    response = auth_client.get(f'/entries/edit/{entry["_id"]}')
    assert response.status_code == 200

def test_edit_entry_success(auth_client, db):
    entry = db.entries.find_one({'review': 'Great place!'})
    response = auth_client.post(f'/entries/edit/{entry["_id"]}', data={
        'place_name': 'Updated Place',
        'place_address': 'Updated Address',
        'date': '2023-01-01',
        'companions': 'Friend1, Friend3',
        'rating': '5',
        'category': 'Restaurant',
        'review': 'Updated review',
        'latitude': '40.7128',
        'longitude': '-74.0060'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_delete_entry(auth_client, db):
    entry = db.entries.find_one({'review': 'Nice park'})
    response = auth_client.post(f'/entries/delete/{entry["_id"]}', follow_redirects=True)
    assert response.status_code == 200
    new_entry = db.entries.find_one({
        'review': 'Nice park'
    })
    assert new_entry is None