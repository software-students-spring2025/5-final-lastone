let map;
let userMarker;
let infoWindow;
let markers = [];

function initMap() {
    const center = window.initialLocation;
    // Create the map centered at initial location
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: center,
        mapTypeId: "roadmap",
    });

    if (isNaN(center.lat) || isNaN(center.lng)) {
        console.error("Invalid coordinates:", center);
        return;
    }

    infoWindow = new google.maps.InfoWindow();

    // Add points from backend
    const points = window.points;
    addPointsToMap(points);

    // Try to get user's location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userPos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };

                // Add user marker
                userMarker = new google.maps.Marker({
                    position: userPos,
                    map: map,
                    title: "Your Location",
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 10,
                        fillColor: "#4285F4",
                        fillOpacity: 1,
                        strokeWeight: 2,
                        strokeColor: "#ffffff"
                    }
                });

                // Center map on user
                map.setCenter(userPos);

                // Calculate distances to all points
                calculateDistances(userPos);
            },
            () => {
                handleLocationError(true, map.getCenter());
            }
        );
    } else {
        handleLocationError(false, map.getCenter());
    }
}

function addPointsToMap(points) {
    points.forEach(point => {
        const marker = new google.maps.Marker({
            position: { lat: point.lat, lng: point.lng },
            map: map,
            title: point.title
        });

        // Add click listener for each marker
        marker.addListener("click", () => {
            infoWindow.setContent(
                `<h3>${point.title}</h3><p>${point.description}</p>`
            );
            infoWindow.open(map, marker);
        });

        markers.push(marker);
    });
}

function calculateDistances(userPos) {
    const service = new google.maps.DistanceMatrixService();
    const destinations = markers.map(marker => marker.getPosition());
    
    service.getDistanceMatrix({
        origins: [userPos],
        destinations: destinations,
        travelMode: 'WALKING',
        unitSystem: google.maps.UnitSystem.METRIC,
    }, (response, status) => {
        if (status !== 'OK') return;
        
        const results = response.rows[0].elements;
        let infoHtml = "<h3>Distances from your location:</h3><ul>";
        
        results.forEach((result, i) => {
            infoHtml += `<li>${markers[i].title}: ${result.distance.text} away</li>`;
        });
        
        infoHtml += "</ul>";
        document.getElementById("info-panel").innerHTML = infoHtml;
    });
}

function handleLocationError(browserHasGeolocation, pos) {
    const content = browserHasGeolocation
        ? "Error: The Geolocation service failed."
        : "Error: Your browser doesn't support geolocation.";
    
    infoWindow.setContent(content);
    infoWindow.setPosition(pos);
    infoWindow.open(map);
}