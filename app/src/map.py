from flask import Blueprint, render_template
import random
import os
map_bp = Blueprint('map', __name__)
gmap_api_key = os.getenv("GOOGLE_MAP_API_KEY")

@map_bp.route('/map')
def show_map():
    # Generate sample points (replace with your MongoDB data)
    points = []
    for i in range(10):
        points.append({
            'lat': 40.72 + random.uniform(-0.01, 0.01),
            'lng': -73.99 + random.uniform(-0.01, 0.01),
            'title': f'Point {i+1}',
            'description': f'Sample description {i+1}'
        })
    
    return render_template(
        'map.html',
        api_key=gmap_api_key,  # Better to use app.config
        initial_location={'lat': 37.7749, 'lng': -122.4194},
        points=points
    )