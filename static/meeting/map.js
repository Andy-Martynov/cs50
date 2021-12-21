
var map
var platform
var ui
var destination

var users_on_map = []
var on_map = []
var routes = []
var me_on_map = []

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
    destination = {lat: coord.lat, lng: coord.lng};
    route_to_destination();
  });
}

async function show_user() {
    getlocation();

    user = await fetch(`/meeting/user_info/${this.value}`)
    .then (response => response.json());

    if (on_map.length > 0) {
        map.removeObjects(on_map);
    }
    on_map = []

	var icon = new H.map.Icon('../static/meeting/big_pin.png');
    // Create a marker using the previously instantiated icon:
    var marker = new H.map.Marker({lat: user.latitude, lng: user.longitude}, { icon: icon });
    // Add the marker to the map:
    map.addObject(marker);
    on_map.push(marker);
	// Create an icon, an object holding the latitude and longitude, and a marker:
	var icon = new H.map.Icon(user.marker),
		coords = {lat: user.latitude, lng: user.longitude},
		u = new H.map.Marker(coords, {icon: icon});
	// Add the marker to the map and center the map at the location of the marker:
	map.addObject(u);
	on_map.push(u);

    destination = {lat: user.latitude, lng: user.longitude};
    route_to_destination();
}

async function show_location() {
    getlocation();

    id = this.value;
    s = `/meeting/loc/${id}`
    loc = await fetch(s)
    .then (response => response.json());

    if (on_map.length > 0) {
        map.removeObjects(on_map);
    }
    on_map = []

    	var icon = new H.map.Icon(loc.marker),
    		coords = {lat: loc.latitude, lng: loc.longitude},
    		u = new H.map.Marker(coords, {icon: icon});
    	// Add the marker to the map and center the map at the location of the marker:
    	u.setZIndex(0);
    	map.addObject(u);
    	on_map.push(u);
    	var icon = new H.map.Icon(loc.image);
        // Create a marker using the previously instantiated icon:
        var marker = new H.map.Marker({lat: loc.latitude, lng: loc.longitude}, { icon: icon });
        // Add the marker to the map:
        marker.setZIndex(0);
        map.addObject(marker);
        on_map.push(marker);
    destination = {lat: loc.latitude, lng: loc.longitude};
    route_to_destination();
}

async function show_meeting() {
    console.log('Show meeting', this.value);

    meeting = await fetch(`/meeting/meeting_info/${this.value}`)
    .then (response => response.json());

    if (on_map.length > 0) {
        map.removeObjects(on_map);
    }
    on_map = []
    if (routes.length > 0) {
        map.removeObjects(routes);
    }
    routes = []

    users = meeting.users;
    loc = meeting.loc;
    bubble = meeting.bubble

	var icon = new H.map.Icon(loc.marker),
		coords = {lat: loc.latitude, lng: loc.longitude},
		u = new H.map.Marker(coords, {icon: icon});
	// Add the marker to the map and center the map at the location of the marker:
	u.setZIndex(0);
	map.addObject(u);
	on_map.push(u);
	var icon = new H.map.Icon(loc.image);
    // Create a marker using the previously instantiated icon:
    var marker = new H.map.Marker({lat: loc.latitude, lng: loc.longitude}, { icon: icon });
    // Add the marker to the map:
    marker.setZIndex(0);
    map.addObject(marker);
    on_map.push(marker);
    destination = {lat: loc.latitude, lng: loc.longitude};
    map.setCenter(destination);

    var bubble =  new H.ui.InfoBubble(destination, {
      // read custom data
      content: bubble
    });
    // show info bubble
    ui.addBubble(bubble);

    for (i = 0; i < users.length; i++) {
        console.log(i, users[i])
    	var icon = new H.map.Icon('../static/meeting/big_pin.png');
        // Create a marker using the previously instantiated icon:
        var marker = new H.map.Marker({lat: users[i].latitude, lng: users[i].longitude}, { icon: icon });
        // Add the marker to the map:
        map.addObject(marker);
        on_map.push(marker);
        users_on_map.push(marker);
    	// Create an icon, an object holding the latitude and longitude, and a marker:
    	var icon = new H.map.Icon(users[i].marker),
    		coords = {lat: users[i].latitude, lng: users[i].longitude},
    		u = new H.map.Marker(coords, {icon: icon});
    	// Add the marker to the map and center the map at the location of the marker:
    	map.addObject(u);
    	on_map.push(u);
    	origin = {lat: users[i].latitude, lng: users[i].longitude};
    	route(origin, destination, false);
    }
    coords = {lat: loc.latitude, lng: loc.longitude};
    map.setCenter(coords);
}

async function show_group() {
    console.log('Show group', this.value);

    users = await fetch(`/meeting/group_info/${this.value}`)
    .then (response => response.json());

    if (on_map.length > 0) {
        map.removeObjects(on_map);
    }
    on_map = []
    if (routes.length > 0) {
        map.removeObjects(routes);
    }
    routes = []

    for (i = 0; i < users.length; i++) {
        console.log(i, users[i])
    	var icon = new H.map.Icon('../static/meeting/big_pin.png');
        // Create a marker using the previously instantiated icon:
        var marker = new H.map.Marker({lat: users[i].latitude, lng: users[i].longitude}, { icon: icon });
        // Add the marker to the map:
        map.addObject(marker);
        on_map.push(marker);
        users_on_map.push(marker);
    	// Create an icon, an object holding the latitude and longitude, and a marker:
    	var icon = new H.map.Icon(users[i].marker),
    		coords = {lat: users[i].latitude, lng: users[i].longitude},
    		u = new H.map.Marker(coords, {icon: icon});
    	// Add the marker to the map and center the map at the location of the marker:
    	map.addObject(u);
    	on_map.push(u);
    }
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

function watchlocation() {
    console.log('watch location');
    const geoconfig = {
        enableHighAccuracy: true,
        maximumAge: 60000
    };
	navigator.geolocation.getCurrentPosition(showinfo, showerror, geoconfig);
}

function getlocation() {
console.log('get location');
	navigator.geolocation.getCurrentPosition(showinfo);
}

function route_to_destination() {
console.log('to destination');
	navigator.geolocation.getCurrentPosition(to_destination);
}

function to_destination(position) {
    if (routes.length > 0) {
        map.removeObjects(routes);
    }
    routes = []
	map.setCenter(destination);
	// Create the parameters for the routing request:
	var routingParameters = {
	  'routingMode': 'fast',
	  'transportMode': 'car',
	  // The start point of the route:
	  'origin': `${position.coords.latitude},${position.coords.longitude}`,
	  // The end point of the route:
	  'destination': `${destination.lat},${destination.lng}`,
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

			// Add the route polyline and the two markers to the map:
			map.addObjects([routeLine]);
            routes.push(routeLine);
            console.log(routes);
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

function route(origin, destination, view) {
	map.setCenter(destination);
	// Create the parameters for the routing request:
	var routingParameters = {
	  'routingMode': 'fast',
	  'transportMode': 'car',
	  // The start point of the route:
	  'origin': `${origin.lat},${origin.lng}`,
	  // The end point of the route:
	  'destination': `${destination.lat},${destination.lng}`,
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

			// Add the route polyline and the two markers to the map:
			map.addObjects([routeLine]);
            routes.push(routeLine);
            console.log(routes);
			// Set the map's viewport to make the whole route visible:
 			if (view) {
 			    map.getViewModel().setLookAtData({bounds: routeLine.getBoundingBox()});
 			};
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

async function set_coords(position) {
	console.log('Set coords ...', position.coords);
	let post = {
		latitude: position.coords.latitude,
		longitude: position.coords.longitude
	};
	console.log(JSON.stringify(post));
	let response = await fetch('/meeting/set_coords', {
		method: 'POST',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});
	let result = await response;
	console.log('result :', result.status);
}

function showinfo(position) {
    if (me_on_map.length > 0) {
        map.removeObjects(me_on_map);
    }
    me_on_map = []
	// Create an icon, an object holding the latitude and longitude, and a marker:
	var icon = new H.map.Icon('../static/meeting/me_60.png'),
		coords = {lat: position.coords.latitude, lng: position.coords.longitude},
		me = new H.map.Marker(coords, {icon: icon});
	me.setZIndex(1001);
	// Add the marker to the map and center the map at the location of the marker:
	map.addObject(me);
	map.setCenter(coords);
    me_on_map.push(me);
	set_coords(position);
}

function marker_click() {
    console.log('CLICK', this)
}

function marker_hover() {
    console.log('HOVER', this)
}

function marker_tap() {
    console.log('TAP', this.position)
    destination = this.position;
    route_to_destination();
}

document.addEventListener('DOMContentLoaded', function() {

	console.log('Location_list loaded');

	users = []

	document.getElementById('where').addEventListener('click', getlocation, false);

	document.getElementById('select_user').addEventListener('change', show_user, false);
	document.getElementById('select_group').addEventListener('change', show_group, false);
	document.getElementById('select_location').addEventListener('change', show_location, false);
	document.getElementById('select_meeting').addEventListener('change', show_meeting, false);

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
    ui = H.ui.UI.createDefault(map, defaultLayers);

	map.setCenter(coords_red_square);

	setUpClickListener(map);

	getlocation();
	watchlocation();
});
