document.addEventListener('DOMContentLoaded', function() {
    // Naga City Coordinates
    var nagaLat = 13.6192;
    var nagaLng = 123.1859;

    var map = L.map('map', {
        zoomControl: false,
        attributionControl: false 
    }).setView([nagaLat, nagaLng], 14);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd'
    }).addTo(map);

    var infoCardContainer = document.querySelector('.info-card-container');
    var eventCard = document.querySelector('.event-card');
    
    // Card Elements
    var cardTitle = document.querySelector('.event-title');
    var cardOrg = document.querySelector('.event-org');
    var cardLoc = document.querySelector('.event-loc');
    var cardLogo = document.querySelector('.event-logo-placeholder');
    var currentEventId = null;

    // Fetch Events
    fetch('/api/events')
        .then(response => response.json())
        .then(events => {
            events.forEach(event => {
                var marker = L.marker([event.lat, event.lng]).addTo(map);
                
                marker.on('click', function(e) {
                    L.DomEvent.stopPropagation(e);
                    
                    // Update content
                    cardTitle.textContent = event.title;
                    cardOrg.textContent = event.org_name;
                    cardLoc.textContent = event.location;
                    currentEventId = event.id;
                    
                    // Simple logo handling (image or placeholder)
                    if(event.image_url) {
                         cardLogo.innerHTML = `<img src="${event.image_url}" style="width:100%; height:100%; object-fit:cover; border-radius:8px;">`;
                    } else {
                         cardLogo.innerHTML = '';
                    }

                    infoCardContainer.classList.add('show');
                });
            });
        })
        .catch(err => console.error('Error loading events:', err));

    // Hide card when clicking on the map background
    map.on('click', function() {
        infoCardContainer.classList.remove('show');
    });

    // Navigate on Card Click
    eventCard.addEventListener('click', function() {
        if(currentEventId) {
            window.location.href = '/event-view/' + currentEventId;
        }
    });

    // Prevent click propogation on the card itself so it doesn't close immediately if logic changes
    eventCard.addEventListener('click', function(e) {
        // e.stopPropagation(); 
        // We actually want it to propagate or handle navigation. 
        // Keeping it simple: navigation is the priority.
    });
});

