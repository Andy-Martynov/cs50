
var map
var platform

var users_on_map = []

const coords_red_square = {lat: 55.753903, lng: 37.620062};

function setUpClickListener(map) {
  // Attach an event listener to map display
  // obtain the coordinates and display in an alert box.
  map.addEventListener('tap', function (evt) {
    var coord = map.screenToGeo(evt.currentPointer.viewportX,
            evt.currentPointer.viewportY);
    console.log('Clicked at ' + Math.abs(coord.lat.toFixed(4)) +
        ((coord.lat > 0) ? 'N' : 'S') +
        ' ' + Math.abs(coord.lng.toFixed(4)) +
         ((coord.lng > 0) ? 'E' : 'W'));
    const latitude = document.getElementById('id_latitude');
    const longitude = document.getElementById('id_longitude');
    latitude.value = coord.lat;
    longitude.value = coord.lng;
  });
}

async function show_users() {
    console.log('Show users');
    users = await fetch('/meeting/users_info')
    .then (response => response.json());
    console.log('objects :', map.getObjects());
    console.log(users_on_map, `len=${users_on_map.length}`);
    if (users_on_map.length > 0) {
        map.removeObjects(users_on_map);
    }
    console.log('objects :', map.getObjects());
    users_on_map = []
    console.log('2 ', users_on_map, `len=${users_on_map.length}`);
    for (i = 0; i < users.length; i++) {
        console.log(i, users[i])
    	var icon = new H.map.Icon('../static/meeting/big_pin.png');
        // Create a marker using the previously instantiated icon:
        var marker = new H.map.Marker({lat: users[i].latitude, lng: users[i].longitude}, { icon: icon });
        // Add the marker to the map:
        map.addObject(marker);
        users_on_map.push(marker);
    	// Create an icon, an object holding the latitude and longitude, and a marker:
    	var icon = new H.map.Icon(users[i].marker),
    		coords = {lat: users[i].latitude, lng: users[i].longitude},
    		u = new H.map.Marker(coords, {icon: icon});
    	// Add the marker to the map and center the map at the location of the marker:
    	map.addObject(u);
    	users_on_map.push(u);
    }
    console.log('3 ', users_on_map, `len=${users_on_map.length}`);
}

async function show_locations(id) {
    console.log('Show locationss');
    locations = await fetch(`/meeting/locations_info/${id}`)
    .then (response => response.json());
    console.log(locations, `len=${locations.length}`)
    for (i = 0; i < locations.length; i++) {
        console.log(i, locations[i])
    	var icon = new H.map.Icon(locations[i].marker),
    		coords = {lat: locations[i].latitude, lng: locations[i].longitude},
    		u = new H.map.Marker(coords, {icon: icon});
    	// Add the marker to the map and center the map at the location of the marker:
    	u.setZIndex(0);
    	map.addObject(u);
    	var icon = new H.map.Icon(locations[i].image);
        // Create a marker using the previously instantiated icon:
        var marker = new H.map.Marker({lat: locations[i].latitude, lng: locations[i].longitude}, { icon: icon });
        // Add the marker to the map:
        marker.setZIndex(0);
        map.addObject(marker);
    	// Create an icon, an object holding the latitude and longitude, and a marker:
    }
}

function getlocation() {
console.log('get location');
	navigator.geolocation.getCurrentPosition(showinfo);
}
function route_to_work() {
console.log('to work');
	navigator.geolocation.getCurrentPosition(to_work);
}
function to_work(position) {
	// Define a variable holding SVG mark-up that defines an icon image:
	var svgMarkup = '<svg width="24" height="24" ' +
		'xmlns="http://www.w3.org/2000/svg">' +
		'<rect stroke="white" fill="#1b468d" x="1" y="1" width="22" ' +
		'height="22" /><text x="12" y="18" font-size="12pt" ' +
		'font-family="Arial" font-weight="bold" text-anchor="middle" ' +
		'fill="yellow">A</text></svg>';

	// Create an icon, an object holding the latitude and longitude, and a marker:
	var icon = new H.map.Icon(svgMarkup),
		coords = {lat: position.coords.latitude, lng: position.coords.longitude},
		me = new H.map.Marker(coords, {icon: icon});

	// Add the marker to the map and center the map at the location of the marker:
	map.addObject(me);
	map.setCenter(coords);

	// Create the parameters for the routing request:
	var routingParameters = {
	  'routingMode': 'fast',
	  'transportMode': 'car',
	  // The start point of the route:
	  'origin': '55.394290,37.624031',
	  // The end point of the route:
	  'destination': '55.635012,37.431997',
	  // Include the route shape in the response
	  'return': 'polyline'
	};

	// Define a callback function to process the routing response:
	var onResult = function(result) {
	  // ensure that at least one route was found
	  if (result.routes.length) {
		result.routes[0].sections.forEach((section) => {
			 // Create a linestring to use as a point source for the route line
			let linestring = H.geo.LineString.fromFlexiblePolyline(section.polyline);

			// Create a polyline to display the route:
			let routeLine = new H.map.Polyline(linestring, {
			  style: { strokeColor: 'blue', lineWidth: 3 }
			});

			// Create a marker for the start point:
			let startMarker = new H.map.Marker(section.departure.place.location);

			// Create a marker for the end point:
			let endMarker = new H.map.Marker(section.arrival.place.location);

			// Add the route polyline and the two markers to the map:
			map.addObjects([routeLine, startMarker, endMarker]);

			// Set the map's viewport to make the whole route visible:
			map.getViewModel().setLookAtData({bounds: routeLine.getBoundingBox()});
		});
	  }
	};

	// Get an instance of the routing service version 8:
	var router = platform.getRoutingService(null, 8);

	// Call calculateRoute() with the routing parameters,
	// the callback and an error callback function (called if a
	// communication error occurs):
	router.calculateRoute(routingParameters, onResult,
	  function(error) {
		alert(error.message);
	  });
}

function showinfo(position) {

	// Define a variable holding SVG mark-up that defines an icon image:
	var svgMarkup = '<svg width="24" height="24" ' +
		'xmlns="http://www.w3.org/2000/svg">' +
		'<rect stroke="white" fill="red" x="1" y="1" width="22" ' +
		'height="22" /><text x="12" y="18" font-size="12pt" ' +
		'font-family="Arial" font-weight="bold" text-anchor="middle" ' +
		'fill="yellow">Me</text></svg>';

	// Create an icon, an object holding the latitude and longitude, and a marker:
	var icon = new H.map.DomIcon(svgMarkup),
		coords = {lat: position.coords.latitude, lng: position.coords.longitude},
		me = new H.map.DomMarker(coords, {icon: icon});

    console.log(map)
    console.log(me)
	me.setZIndex(1001);

	// Add the marker to the map and center the map at the location of the marker:
	map.addObject(me);
	map.setCenter(coords);
	map.setZoom(18);
}

function marker_click() {
    console.log('CLICK', this)
}

function marker_hover() {
    console.log('HOVER', this)
}

function marker_tap() {
    console.log('TAP', this)
}

document.addEventListener('DOMContentLoaded', function() {

	console.log('Location_list loaded');

	users = []

	document.getElementById('where').addEventListener('click', getlocation, false);
	document.getElementById('users').addEventListener('click', show_users, false);

	platform = new H.service.Platform({
		'apikey': 'jHq1qqUMjYonwt9OO15O-bXL9PTUCnGREfNnuYnGI04'
	});

	// Obtain the default map types from the platform object:
	var defaultLayers = platform.createDefaultLayers();

	// Instantiate (and display) a map object:
	map = new H.Map(
		document.getElementById('mapContainer'),
		defaultLayers.vector.normal.map,
		{
		  zoom: 9,
		  center: { lat: 55.394290, lng: 37.624031 }
		});

    // Enable the event system on the map instance:
    var mapEvents = new H.mapevents.MapEvents(map);

    // MapEvents enables the event system
    // Behavior implements default interactions for pan/zoom (also on mobile touch environments)
    // var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));

    // Instantiate the default behavior, providing the mapEvents object:
    new H.mapevents.Behavior(mapEvents);

    // Create the default UI:
    var ui = H.ui.UI.createDefault(map, defaultLayers);

	map.setCenter(coords_red_square);

	setUpClickListener(map);

	show_locations(0);
});
