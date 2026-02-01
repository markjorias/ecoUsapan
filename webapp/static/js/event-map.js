document.addEventListener('DOMContentLoaded', function() {
    // Naga City Coordinates
    var nagaLat = 13.6192;
    var nagaLng = 123.1859;

    var map = L.map('map', {
        zoomControl: false, // We can hide zoom control for a cleaner mobile look or move it
        attributionControl: false 
    }).setView([nagaLat, nagaLng], 14);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd'
    }).addTo(map);

    // Add a marker for the event
    var eventMarker = L.marker([nagaLat, nagaLng]).addTo(map);
    
    var infoCardContainer = document.querySelector('.info-card-container');

    eventMarker.on('click', function(e) {
        L.DomEvent.stopPropagation(e); // Prevent map click
        infoCardContainer.classList.add('show');
    });

    // Hide card when clicking on the map background
    map.on('click', function() {
        infoCardContainer.classList.remove('show');
    });
});
