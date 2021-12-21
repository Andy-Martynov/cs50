
var map
var platform

const coords_work = {lat: 55.635012, lng: 37.431997};
const coords_home = {lat: 55.394290, lng: 37.624031};
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
    const location = document.getElementById('location');
	location.innerHTML = 'Clicked at ' + Math.abs(coord.lat.toFixed(4)) +
        ((coord.lat > 0) ? 'N' : 'S') +
        ' ' + Math.abs(coord.lng.toFixed(4)) +
         ((coord.lng > 0) ? 'E' : 'W')

  });
}


document.addEventListener('DOMContentLoaded', function() {

	console.log('HeRe loaded');

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

	// Add the marker to the map and center the map at the location of the marker:
	map.addObject(work);




});
