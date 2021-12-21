document.addEventListener('DOMContentLoaded', function() {
	console.log('LOAD filter.js');
	document.querySelectorAll('.input').forEach(el => {el.addEventListener('change', setParam);});
});

async function setParam() {
    console.log('this =', this, this.name, this.value)

	let post = {
		param: this.name,
		value: this.value
	};
	console.log(post);
	let response = await fetch('/explorer/set_param', {
		method: 'POST',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});
	let result = await response;
	console.log(result.status);
}