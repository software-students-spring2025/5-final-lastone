from flask import Flask, render_template, request, redirect, url_for, g, session
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import bcrypt

from map import map_bp
from utils import get_current_user_id, login_required

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
app.config['GOOGLE_MAP_API_KEY'] = os.getenv('GOOGLE_MAP_API_KEY')
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = None
db = None

def get_db():
    global client, db
    if db is None:
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ismaster')
            print("MongoDB connection successful!")
            mongodb_name = os.getenv('MONGO_DBNAME', 'geometric_journal_db')
            db = client.get_database(mongodb_name)
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            db = None
    return db

@app.before_request
def before_request():
    g.db = get_db()
    
@app.teardown_appcontext
def teardown_db(exception):
    global client, db
    if client is not None:
        client.close()
        client = None
        db = None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db = g.db
        if db is None:
            return "Database connection error.", 500

        users_collection = db.users
        user = users_collection.find_one({"username": username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('map.show_map'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        db = g.db
        if db is None:
            return "Database connection error.", 500

        users_collection = db.users

        if not username or not password or not confirm_password:
            return render_template('create_account.html', error="All fields are required.")
        if password != confirm_password:
            return render_template('create_account.html', error="Passwords do not match.")
        if users_collection.find_one({"username": username}):
            return render_template('create_account.html', error="Username already exists.")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_data = {
            "username": username,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow()
        }

        try:
            users_collection.insert_one(user_data)
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error creating user: {e}")
            return render_template('create_account.html', error="Error creating account.")

    return render_template('create_account.html')
    
@app.route('/entries')
@login_required
def my_entries():
    user_id = get_current_user_id()
    db = g.db

    if db is None:
        return "Database connection error.", 500

    entries_with_place = list(db.entries.aggregate([
        {"$match": {"user_id": user_id}},
        {"$sort": {"date": -1}},
        {"$lookup": {
            "from": "places",
            "localField": "place_id",
            "foreignField": "_id",
            "as": "place_info"
        }},
        {"$unwind": {"path": "$place_info", "preserveNullAndEmptyArrays": True}}
    ]))

    for entry in entries_with_place:
         entry['place_name'] = entry.get('place_info', {}).get('name', 'Unknown Place')
         entry['place_address'] = entry.get('place_info', {}).get('address', 'Unknown Address')
         if isinstance(entry.get('date'), datetime):
             entry['formatted_date'] = entry['date'].strftime('%Y-%m-%d')
         else:
             entry['formatted_date'] = 'N/A'
         if not isinstance(entry.get('companions'), list):
             entry['companions'] = []


    return render_template('my_entries.html', entries=entries_with_place)

@app.route('/entries/add', methods=['GET', 'POST'])
@login_required
def add_entry():
    user_id = get_current_user_id()
    db = g.db
    if db is None:
        return "Database connection error.", 500

    entries_collection = db.entries
    places_collection = db.places

    if request.method == 'POST':
        place_name = request.form.get('place_name')
        place_address = request.form.get('place_address')
        entry_date_str = request.form.get('date')
        companions_str = request.form.get('companions', '')
        rating = request.form.get('rating')
        category = request.form.get('category')
        review = request.form.get('review')

        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if not place_name or not place_address or not entry_date_str or not review:
             return render_template('add_entry.html', error="Missing required fields.")


        if latitude is not None and longitude is not None and latitude != "" and longitude != "":
             try:
                 latitude = float(latitude)
                 longitude = float(longitude)
                 coordinates = {"type": "Point", "coordinates": [longitude, latitude]}
             except ValueError:
                 return render_template('add_entry.html', error="Invalid coordinate format.")
        else:
             coordinates = None
        print("coordinates: " , coordinates)

        try:
            entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d')
        except ValueError:
             return render_template('add_entry.html', error="Invalid date format. UseYYYY-MM-DD")

        try:
            rating = float(rating) if rating else None
        except ValueError:
             return render_template('add_entry.html', error="Invalid rating format.")

        companions = [c.strip() for c in companions_str.split(',') if c.strip()]

        place_id = None
        if coordinates:
             print(f"Coordinates provided. Creating new place with coordinates.")
             new_place_data = {
                 "name": place_name,
                 "address": place_address,
                 "coordinates": coordinates,
                 "created_at": datetime.utcnow()
             }
             try:
                 insert_place_result = places_collection.insert_one(new_place_data)
                 place_id = insert_place_result.inserted_id
                 print(f"Created new place: {place_name} ({place_id})")
             except Exception as e:
                  print(f"Error creating new place with coordinates: {e}")
                  return render_template('add_entry.html', error="Error saving place information.")
        else:
             existing_place = places_collection.find_one({"address": place_address})

             if existing_place:
                 place_id = existing_place['_id']
                 print(f"Found existing place by address: {place_name} ({place_id})")
             else:
                 print(f"Place not found by address. Creating new place without geocoding.")
                 new_place_data = {
                     "name": place_name,
                     "address": place_address,
                     "coordinates": None,
                     "created_at": datetime.utcnow()
                 }
                 try:
                     insert_place_result = places_collection.insert_one(new_place_data)
                     place_id = insert_place_result.inserted_id
                     print(f"Created new place: {place_name} ({place_id})")
                 except Exception as e:
                      print(f"Error creating new place without coordinates: {e}")
                      return render_template('add_entry.html', error="Error saving place information.")


        entry_data = {
            "user_id": user_id,
            "place_id": place_id,
            "date": entry_date,
            "companions": companions,
            "rating": rating,
            "category": category,
            "review": review,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        try:
            entries_collection.insert_one(entry_data)
            print("Entry added successfully!")
            return redirect(url_for('my_entries'))
        except Exception as e:
             print(f"Error inserting entry: {e}")
             return render_template('add_entry.html', error="Error saving entry to database.")


    else:
        api_key = app.config.get('GOOGLE_MAP_API_KEY')
        return render_template('add_entry.html', api_key=api_key)


@app.route('/entries/edit/<entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    user_id = get_current_user_id()
    db = g.db
    if db is None:
        return "Database connection error.", 500

    entries_collection = db.entries
    places_collection = db.places

    try:
        entry_object_id = ObjectId(entry_id)
    except:
        return "Invalid entry ID.", 400

    entry = entries_collection.find_one({"_id": entry_object_id, "user_id": user_id})

    if not entry:
        return "Entry not found or you don't have permission to edit.", 404

    place = places_collection.find_one({"_id": entry.get('place_id')})
    if place:
        entry['place_name'] = place.get('name')
        entry['place_address'] = place.get('address')
        if place.get('coordinates') and place['coordinates'].get('type') == 'Point' and len(place['coordinates'].get('coordinates', [])) == 2:
             lng, lat = place['coordinates']['coordinates']
             entry['latitude'] = lat
             entry['longitude'] = lng
        else:
             entry['latitude'] = None
             entry['longitude'] = None

    else:
        entry['place_name'] = 'Unknown Place'
        entry['place_address'] = 'Unknown Address'
        entry['latitude'] = None
        entry['longitude'] = None
        print(f"Warning: Place not found for entry ID {entry_id}")


    if request.method == 'POST':
        place_name = request.form.get('place_name')
        place_address = request.form.get('place_address')
        entry_date_str = request.form.get('date')
        companions_str = request.form.get('companions', '')
        rating = request.form.get('rating')
        category = request.form.get('category')
        review = request.form.get('review')

        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if not place_name or not place_address or not entry_date_str or not review:
             return render_template('edit_entry.html', entry=entry, error="Missing required fields.")

        if latitude is not None and longitude is not None:
             try:
                 latitude = float(latitude)
                 longitude = float(longitude)
                 coordinates = {"type": "Point", "coordinates": [longitude, latitude]}
             except ValueError:
                 return render_template('edit_entry.html', entry=entry, error="Invalid coordinate format.")
        else:
             coordinates = None

        try:
            entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d')
        except ValueError:
             return render_template('edit_entry.html', entry=entry, error="Invalid date format. UseYYYY-MM-DD")

        try:
            rating = float(rating) if rating else None
        except ValueError:
             return render_template('edit_entry.html', entry=entry, error="Invalid rating format.")

        companions = [c.strip() for c in companions_str.split(',') if c.strip()]

        current_place_id = entry.get('place_id')
        new_place_id = current_place_id

        update_entry_place_id = False

        original_place_address = place.get('address') if place else None

        if coordinates is not None:
             if place:
                  print(f"Updating coordinates for existing place {current_place_id}")
                  places_collection.update_one(
                      {"_id": current_place_id},
                      {"$set": {"coordinates": coordinates, "updated_at": datetime.utcnow()}}
                  )
                  update_entry_place_id = False
             else:
                  print(f"No existing place linked. Creating new place with coordinates during edit.")
                  new_place_data = {
                      "name": place_name,
                      "address": place_address,
                      "coordinates": coordinates,
                      "created_at": datetime.utcnow()
                  }
                  try:
                      insert_place_result = places_collection.insert_one(new_place_data)
                      new_place_id = insert_place_result.inserted_id
                      update_entry_place_id = True
                      print(f"Created new place and will link entry: {new_place_id}")
                  except Exception as e:
                       print(f"Error creating new place during edit with coordinates: {e}")
                       return render_template('edit_entry.html', entry=entry, error="Error saving new place information.")

        elif original_place_address != place_address:
             print(f"Address changed for entry {entry_id}, no new coordinates. Handling place by address...")
             existing_place = places_collection.find_one({"address": place_address})

             if existing_place:
                 new_place_id = existing_place['_id']
                 update_entry_place_id = (new_place_id != current_place_id)
                 print(f"Linked to existing place by new address: {new_place_id}")
             else:
                 print(f"New address not found. Creating new place without geocoding during edit.")
                 new_place_data = {
                     "name": place_name,
                     "address": place_address,
                     "coordinates": None,
                     "created_at": datetime.utcnow()
                 }
                 try:
                     insert_place_result = places_collection.insert_one(new_place_data)
                     new_place_id = insert_place_result.inserted_id
                     update_entry_place_id = True
                     print(f"Created new place and will link entry: {new_place_id}")
                 except Exception as e:
                      print(f"Error creating new place during edit without coordinates: {e}")
                      return render_template('edit_entry.html', entry=entry, error="Error saving place information.")
        else:
             update_entry_place_id = False


        update_data = {
            "date": entry_date,
            "companions": companions,
            "rating": rating,
            "category": category,
            "review": review,
            "updated_at": datetime.utcnow()
        }

        if update_entry_place_id:
             update_data["place_id"] = new_place_id


        try:
            update_result = entries_collection.update_one(
                {"_id": entry_object_id, "user_id": user_id},
                {"$set": update_data}
            )
            if update_result.matched_count == 0:
                 print(f"Warning: Update matched 0 documents for entry ID {entry_id}")
                 return "Error updating entry: Document not found or not owned.", 500
            print("Entry updated successfully!")
            return redirect(url_for('my_entries'))
        except Exception as e:
             print(f"Error updating entry: {e}")
             return render_template('edit_entry.html', entry=entry, error="Error saving updates to database.")


    else:
        api_key = app.config.get('GOOGLE_MAP_API_KEY')
        if isinstance(entry.get('date'), datetime):
            entry['date_str'] = entry['date'].strftime('%Y-%m-%d')
        else:
             entry['date_str'] = ''

        if isinstance(entry.get('companions'), list):
             entry['companions_str'] = ', '.join(entry['companions'])
        else:
             entry['companions_str'] = ''

        entry['rating_str'] = str(entry['rating']) if entry.get('rating') is not None else ''

        return render_template('edit_entry.html', entry=entry, api_key=api_key)

@app.route('/entries/delete/<entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    user_id = get_current_user_id()
    db = g.db
    if db is None:
        return "Database connection error.", 500

    entries_collection = db.entries

    try:
        entry_object_id = ObjectId(entry_id)
    except:
        return "Invalid entry ID.", 400

    try:
        delete_result = entries_collection.delete_one(
            {"_id": entry_object_id, "user_id": user_id}
        )

        if delete_result.deleted_count == 1:
            print(f"Entry {entry_id} deleted successfully!")
        else:
             print(f"Entry {entry_id} not found or not owned by user {user_id}. Deleted count: {delete_result.deleted_count}")
             return "Entry not found or you don't have permission to delete.", 404

        return redirect(url_for('my_entries'))

    except Exception as e:
        print(f"Error deleting entry {entry_id}: {e}")
        return "Error deleting entry from database.", 500

app.register_blueprint(map_bp)
if __name__ == '__main__':
    db_connection = get_db()
    if db_connection is not None:
       app.run(debug=True, port=5000)
    else:
       print("Failed to connect to database. Exiting.")

