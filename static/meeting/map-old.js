
var map
var platform

const coords_work = {lat: 55.635012, lng: 37.431997};
const coords_home = {lat: 55.394290, lng: 37.624031};
const coords_red_square = {lat: 55.753903, lng: 37.620062};


async function show_users() {
    console.log('Show users');

    users = await fetch('/meeting/users_info')
    .then (response => response.json());

    console.log(users, `len=${users.length}`)

    for (i = 0; i < users.length; i++) {
        console.log(i, users[i])
    	var icon = new H.map.Icon('../static/meeting/big_pin.png');

        // Create a marker using the previously instantiated icon:
        var marker = new H.map.Marker({lat: users[i].latitude, lng: users[i].longitude}, { icon: icon });

        // Add the marker to the map:
        map.addObject(marker);

    	// Create an icon, an object holding the latitude and longitude, and a marker:
    	var icon = new H.map.Icon(users[i].marker),
    		coords = {lat: users[i].latitude, lng: users[i].longitude},
    		u = new H.map.Marker(coords, {icon: icon});

    	// Add the marker to the map and center the map at the location of the marker:
    	map.addObject(u);

    }
}

function where_s () {
    console.log('where S?');

    // Get an instance of the geocoding service:
    var service = platform.getSearchService();

    // Call the geocode method with the geocoding parameters,
    // the callback and an error callback function (called if a
    // communication error occurs):
    service.geocode({
      q: 'Москва, ул. Бирюлевская, 1'
    }, (result) => {
      // Add a marker for each location found
      result.items.forEach((item) => {
        map.addObject(new H.map.Marker(item.position));
        map.setCenter(item.position);
      });
    }, alert);
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
	const location = document.getElementById('location');
	location.innerHTML = `lat: ${position.coords.latitude}, lng: ${position.coords.longitude}, acc: ${position.coords.accuracy}`

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

    console.log(map)
    console.log(me)

	// Add the marker to the map and center the map at the location of the marker:
	map.addObject(me);
	map.setCenter(coords);
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

	console.log('HeRe loaded');

	document.getElementById('where').addEventListener('click', getlocation, false);
	document.getElementById('users').addEventListener('click', show_users, false);
	document.getElementById('work').addEventListener('click', route_to_work, false);
	document.getElementById('s').addEventListener('click', where_s, false);

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

    // Instantiate the default behavior, providing the mapEvents object:
    new H.mapevents.Behavior(mapEvents);

    // Create the default UI:
    var ui = H.ui.UI.createDefault(map, defaultLayers);


    	var icon = new H.map.Icon('../static/meeting/big_pin.png');

        // Create a marker using the previously instantiated icon:
        var marker = new H.map.Marker({lat: 55.431618, lng: 37.544698}, { icon: icon });

        // Add the marker to the map:
        map.addObject(marker);


    	var icon = new H.map.Icon('../static/meeting/home.png');

        // Create a marker using the previously instantiated icon:
        var marker = new H.map.Marker(coords_home, { icon: icon });

        // Add the marker to the map:
        map.addObject(marker);


	// Define a variable holding SVG mark-up that defines an icon image:
	var svgMarkup = '<svg width="24" height="24" ' +
		'xmlns="http://www.w3.org/2000/svg">' +
		'<rect stroke="white" fill="#1b468d" x="1" y="1" width="22" ' +
		'height="22" /><text x="12" y="18" font-size="12pt" ' +
		'font-family="Arial" font-weight="bold" text-anchor="middle" ' +
		'fill="red">W</text></svg>';

	// Create an icon, an object holding the latitude and longitude, and a marker:
	var icon = new H.map.Icon(svgMarkup),
		coords = coords_work,
		work = new H.map.Marker(coords, {icon: icon});

		work.addEventListener('click', marker_click);
		work.addEventListener('hover', marker_hover);
		work.addEventListener('tap', marker_tap);
// 		work.addEventListener('tap', function (evt) {
// 		    console.log('this')
//             var coord = map.screenToGeo(evt.currentPointer.viewportX,
//                     evt.currentPointer.viewportY);
//             console.log('Clicked at ' + Math.abs(coord.lat.toFixed(4)) +
//                 ((coord.lat > 0) ? 'N' : 'S') +
//                 ' ' + Math.abs(coord.lng.toFixed(4)) +
//                  ((coord.lng > 0) ? 'E' : 'W'));
//             const location = document.getElementById('location');
//         	location.innerHTML = 'Clicked at ' + Math.abs(coord.lat.toFixed(4)) +
//                 ((coord.lat > 0) ? 'N' : 'S') +
//                 ' ' + Math.abs(coord.lng.toFixed(4)) +
//                  ((coord.lng > 0) ? 'E' : 'W')

//         });
		console.log('WORK:', work)


	// Add the marker to the map and center the map at the location of the marker:
	map.addObject(work);

	map.setCenter(coords_red_square);
});
