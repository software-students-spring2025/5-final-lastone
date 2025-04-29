from flask import Blueprint, render_template, g, current_app, session, redirect, url_for
import random
import os
from bson.objectid import ObjectId
from datetime import datetime
from utils import get_current_user_id, login_required
map_bp = Blueprint('map', __name__)
gmap_api_key = os.getenv("GOOGLE_MAP_API_KEY")

@map_bp.route('/')
@login_required
def show_map():
    user_id = get_current_user_id()
    db = g.db

    if db is None:
        return "Database connection error.", 500

    places_collection = db.places
    entries_collection = db.entries

    user_entries = list(entries_collection.find({"user_id": user_id}, {"place_id": 1}))
    place_ids = [entry['place_id'] for entry in user_entries if 'place_id' in entry]

    unique_place_ids = list(set(place_ids))

    places_with_coords = list(places_collection.find({
        "_id": {"$in": unique_place_ids},
        "coordinates": {"$exists": True, "$ne": None}
    }))

    points = []
    for place in places_with_coords:
        if place.get('coordinates') and place['coordinates'].get('type') == 'Point' and len(place['coordinates'].get('coordinates', [])) == 2:
             lng, lat = place['coordinates']['coordinates']
             points.append({
                 'lat': lat,
                 'lng': lng,
                 'title': place.get('name', 'Unnamed Place'),
                 'address': place.get('address', 'No Address'),
                 'place_id': str(place['_id'])
             })

    recent_entries = list(entries_collection.aggregate([
        {"$match": {"user_id": user_id}},
        {"$sort": {"date": -1}},
        {"$limit": 10},
        {"$lookup": {
            "from": "places",
            "localField": "place_id",
            "foreignField": "_id",
            "as": "place_info"
        }},
        {"$unwind": {"path": "$place_info", "preserveNullAndEmptyArrays": True}}
    ]))

    initial_location = {'lat': 39.8283, 'lng': -98.5795}
    initial_zoom = 4

    if recent_entries:
        latest_entry = recent_entries[0]
        if latest_entry.get('place_info') and latest_entry['place_info'].get('coordinates') and \
           latest_entry['place_info']['coordinates'].get('type') == 'Point' and \
           len(latest_entry['place_info']['coordinates'].get('coordinates', [])) == 2:
            lng, lat = latest_entry['place_info']['coordinates']['coordinates']
            initial_location = {'lat': lat, 'lng': lng}
            initial_zoom = 12

    api_key = current_app.config.get('GOOGLE_MAP_API_KEY')

    for entry in recent_entries:
         entry['place_name'] = entry.get('place_info', {}).get('name', 'Unknown Place')
         entry['place_address'] = entry.get('place_info', {}).get('address', 'Unknown Address')
         if isinstance(entry.get('date'), datetime):
             entry['formatted_date'] = entry['date'].strftime('%Y-%m-%d')
         else:
             entry['formatted_date'] = 'N/A'

    return render_template(
        'map.html',
        api_key=api_key,
        initial_location=initial_location,
        initial_zoom=initial_zoom,
        points=points,
        recent_entries=recent_entries
    )