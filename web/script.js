// Initialize the map
const map = L.map('map').setView([51.505, -0.09], 3);

// Add the tile layer
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Create a marker cluster group
const markers = L.markerClusterGroup();

// Load your JSON file
fetch('../db/markers.json')
    .then(response => response.json())
    .then(data => {
        // Loop through each marker in the JSON
        data.forEach(marker => {
            const lat = marker.lat;
            const lng = marker.lng;
            const popupText = marker.popup || 'Marker';
            // Add the marker to the cluster group
            markers.addLayer(L.marker([lat, lng]).bindPopup(popupText));
        });
        // Add the cluster group to the map
        map.addLayer(markers);
    })
    .catch(error => console.error('Error loading the JSON file:', error));

// Alternative Approach: Server-Side Rendering
// If clustering is still too slow, consider server-side rendering (e.g., using GeoJSON and a backend service to only send markers for the current view). This is more advanced and requires a backend (Node.js, Python, etc.).
