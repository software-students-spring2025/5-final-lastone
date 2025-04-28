def test_add_entry_with_new_place(auth_client, db):
    """Test adding an entry with a completely new place (with coordinates)"""
    # Test data
    test_data = {
        'place_name': 'New Test Place',
        'place_address': '789 New Test St, Test City',
        'date': '2023-01-03',
        'companions': 'Friend3, Friend4',
        'rating': '5.0',
        'category': 'Museum',
        'review': 'Amazing experience!',
        'latitude': '40.7128',
        'longitude': '-74.0060'
    }
    
    response = auth_client.post('/entries/add', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify database state
    # Check place was created
    place = db.places.find_one({"name": "New Test Place"})
    assert place is not None
    assert place['address'] == '789 New Test St, Test City'
    assert place['coordinates'] == {'type': 'Point', 'coordinates': [-74.0060, 40.7128]}
    
    # Check entry was created and linked to the place
    entry = db.entries.find_one({"review": "Amazing experience!"})
    assert entry is not None
    assert entry['place_id'] == place['_id']
    assert entry['rating'] == 5.0
    assert entry['category'] == 'Museum'
    assert sorted(entry['companions']) == sorted(['Friend3', 'Friend4'])

def test_add_entry_with_existing_place_by_address(auth_client, db):
    """Test adding an entry with an existing place (matched by address)"""
    # Test data using address of existing place from fixture
    test_data = {
        'place_name': 'Updated Place Name',  # This should get ignored since we match by address
        'place_address': '123 Test St',  # Matches place1 from fixture
        'date': '2023-01-04',
        'companions': '',
        'rating': '4.0',
        'category': 'Updated Category',
        'review': 'Still great!',
        'latitude': '',  # No new coordinates provided
        'longitude': ''
    }
    
    response = auth_client.post('/entries/add', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify database state
    # Should not create a new place
    assert db.places.count_documents({}) == 2
    
    # Should use existing place1
    place1 = db.places.find_one({"address": "123 Test St"})
    entry = db.entries.find_one({"review": "Still great!"})
    assert entry['place_id'] == place1['_id']
    
    # Original place name should remain unchanged
    assert place1['name'] == 'Test Place 1'

def test_add_entry_with_new_place_no_coordinates(auth_client, db):
    """Test adding an entry with a new place but no coordinates"""
    test_data = {
        'place_name': 'Place Without Coordinates',
        'place_address': '999 No Coordinates St',
        'date': '2023-01-05',
        'companions': '',
        'rating': '3.5',
        'category': 'Cafe',
        'review': 'Nice atmosphere',
        'latitude': '',
        'longitude': ''
    }
    
    response = auth_client.post('/entries/add', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify database state
    # Should create a new place without coordinates
    place = db.places.find_one({"address": "999 No Coordinates St"})
    assert place is not None
    assert place['coordinates'] is None
    
    # Entry should be linked to this place
    entry = db.entries.find_one({"review": "Nice atmosphere"})
    assert entry['place_id'] == place['_id']

def test_edit_entry_update_place_coordinates(auth_client, db):
    """Test editing an entry to add coordinates to an existing place"""
    # Get an existing entry with a place that has no coordinates (place2 from fixture)
    place2 = db.places.find_one({"name": "Test Place 2"})
    entry = db.entries.find_one({"place_id": place2['_id']})
    
    # Edit data - adding coordinates
    edit_data = {
        'place_name': 'Test Place 2',
        'place_address': '456 Test Ave',  # Same address
        'date': '2023-01-02',
        'companions': 'Friend5',  # Updated companions
        'rating': '4.0',  # Updated rating
        'category': 'Updated Park',
        'review': 'Even better now!',
        'latitude': '40.7128',  # New coordinates
        'longitude': '-74.0060'
    }
    
    response = auth_client.post(f'/entries/edit/{entry["_id"]}', data=edit_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify database state
    # Place should now have coordinates
    updated_place = db.places.find_one({"_id": place2['_id']})
    assert updated_place['coordinates'] == {'type': 'Point', 'coordinates': [-74.0060, 40.7128]}
    
    # Entry should be updated but still linked to same place
    updated_entry = db.entries.find_one({"_id": entry['_id']})
    assert updated_entry['place_id'] == place2['_id']
    assert updated_entry['rating'] == 4.0
    assert updated_entry['companions'] == ['Friend5']

def test_edit_entry_change_place_address(auth_client, db):
    """Test editing an entry with a changed place address (should create new place)"""
    # Get an existing entry (place1 from fixture)
    place1 = db.places.find_one({"name": "Test Place 1"})
    entry = db.entries.find_one({"place_id": place1['_id']})
    
    # Edit data - changing address
    edit_data = {
        'place_name': 'Test Place 1',
        'place_address': '123 Updated Test St',  # Changed address
        'date': '2023-01-01',
        'companions': 'Friend1, Friend2',
        'rating': '4.5',
        'category': 'Restaurant',
        'review': 'Still great!'
    }
    
    response = auth_client.post(f'/entries/edit/{entry["_id"]}', data=edit_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify database state
    # Should create a new place with the new address
    print(list(db.places.find({})))
    assert db.places.count_documents({}) == 3
    new_place = db.places.find_one({"address": "123 Updated Test St"})
    assert new_place is not None
    assert new_place['coordinates'] is None  # No coordinates provided
    
    # Entry should now be linked to the new place
    updated_entry = db.entries.find_one({"_id": entry['_id']})
    assert updated_entry['place_id'] == new_place['_id']
    
    # Original place should still exist
    assert db.places.find_one({"_id": place1['_id']}) is not None