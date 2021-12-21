var location_ok

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
    const geoconfig = {
        enableHighAccuracy: true,
        maximumAge: 60000
    };
	navigator.geolocation.getCurrentPosition(showinfo, showerror, geoconfig);
}

function showinfo(position) {
	coords = {lat: position.coords.latitude, lng: position.coords.longitude};
	console.log('showinfo, coords: ', coords);
	const info = document.getElementById('location');
	info.innerHTML = `Your coodinates: ${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`;
	location_ok = true;
    set_coords(position);
}

function showerror(error) {
    console.log(`error code: ${error.code}, ${error.message}`)
	const info = document.getElementById('location');
	if (error.code == 1) {
	    info.innerHTML = `Please allow to know your location.<br> To change permisions in your browser, e.g. in Chrome :<br>Settings/Privace and security/Site settings/Permissions/Location`;
	} else {
    	info.innerHTML = `Something went wrong, error code: ${error.code}, ${error.message}`;
	}
}

function setCurrent(name) {
    console.log('Set current')
    pages = document.querySelectorAll('.nav-link');
	for(var  n=0; n<pages.length; n++) {
	    nav_index = pages[n].getAttribute('nav_index');
	    if (nav_index == name) {
	        pages[n].setAttribute('current', 'yes');
	    } else {
	        pages[n].setAttribute('current', 'no');
	    }
        console.log(nav_index, pages[n].getAttribute('current'));
    }
}

document.addEventListener('DOMContentLoaded', function() {

    location_ok = false
	getlocation();
    watchlocation();
});