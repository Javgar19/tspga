// JavaScript code for initializing the map 
var map = L.map('map').setView([40.4168, -3.7038], 4); // Set the initial map view

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
  maxZoom: 18,
}).addTo(map);


var markers = [];
let polyline;
map.on('click', function (e) {
    // Add marker to the list
    var marker = L.marker(e.latlng).addTo(map);
    markers.push(marker);
    marker.bindPopup('Marker ' + markers.length).openPopup();

    marker.on('click', function () {
        // Remove the existing paths
        if (polyline) {
            map.removeLayer(polyline);
        }
        // Remove the marker
        map.removeLayer(marker);
        markers = markers.filter(function (m) {
            return m !== marker;
        });
    });
});

var form = document.getElementById('mapForm');

function popMarkersLenghtAlert() {
    // Display an error message when the amount of locations is less than two
    const errorMessage = document.createElement('div');
    errorMessage.classList.add('alert', 'alert-danger');
    errorMessage.innerText = 'Error: You need at least 2 markers.';

    const container = document.getElementById('errorMessageContainer');
    container.innerHTML = '';
    container.appendChild(errorMessage);

    // Automatically remove the error message after 3 seconds
    setTimeout(() => {
        container.removeChild(errorMessage);
    }, 3000);
}

var totalDistanceElement = document.getElementById('totalDistance');
form.addEventListener('submit', function(event) {
    event.preventDefault();
    // Remove existing paths
    if (polyline) {
        map.removeLayer(polyline);
    }
    // Check the number of markers
    if (markers.length < 2) {
        popMarkersLenghtAlert()
    } else{

        var formData = new FormData(form);
        var markerData = [];

        // Iterate over the marker list and collect lat/lon data
        for (var i = 0; i < markers.length; i++){
            var marker = markers[i];
            var lat = marker.getLatLng().lat;
            var lng = marker.getLatLng().lng;
            markerData.push({ lat: lat, lng: lng });
        }

        formData.append('markerData', JSON.stringify(markerData));

        // Create the POST request
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Show solution on the map
            const latlngs = data["path"].map(coord => [coord.lat, coord.lng]);
            polyline = L.polyline(latlngs, { color: 'blue' }).addTo(map);
            map.fitBounds(polyline.getBounds());

            // Display the total distance
            const totalDistance = data["distance"]
            totalDistanceElement.textContent = `Total distance: ${totalDistance} km`;
        })
        .catch(error => console.error('Error:', error));
}});

function clearMap() {
    // Remove existing paths
    if (polyline) {
        map.removeLayer(polyline);
    }

    // Remove markers
    for (var i = 0; i < markers.length; i++){
        map.removeLayer(markers[i]);
    }
    markers = [];

    // Erase total distance
    totalDistanceElement.textContent = `Total distance:`;
};