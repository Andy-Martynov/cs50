document.addEventListener('DOMContentLoaded', function() {
	console.log('LOAD');
    document.querySelectorAll('.like').forEach(el => el.addEventListener('click', like));
	document.querySelectorAll('.edit').forEach(el => el.addEventListener('click', edit));
	document.querySelectorAll('.save').forEach(el => el.addEventListener('click', save));
});

async function like() {
	console.log('Like!');
	post_id = this.getAttribute('pid');
	label = this.innerHTML;
	console.log(label);
	console.log(post_id);
	let post = {
		post_id: post_id
	};
	console.log(post);
	let response = await fetch('/network/like', {
		method: 'POST',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});

	let result = await response;
	console.log(result.status);
	if (result.status == 204) {
		counter = document.querySelector(`[cid="${post_id}"]`);
		console.log(counter.innerHTML);
		num = parseInt(counter.innerHTML);
		if (label == 'Like' ) {
			this.innerHTML = 'Unlike';
			counter.innerHTML = num + 1;
		} else {
			this.innerHTML = 'Like';
			counter.innerHTML = num - 1;
		}
	}
}

async function save() {
	console.log('Save!');
	post_id = this.getAttribute('pid');
	console.log(post_id);
	textarea = document.querySelector(`[aid="${post_id}"]`);
	let post = {
		post_id: post_id,
		text: textarea.value
	};
	console.log(post);
	let response = await fetch('/network/edit', {
		method: 'PUT',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});

	form = document.querySelector(`[fid="${post_id}"]`);
	p = document.querySelector(`[tid="${post_id}"]`);

	let result = await response;
	console.log(result.status);
	if (result.status == 204) {
	// if (true) {
		p.innerHTML = textarea.value;
	}
	form.style.display = 'none';
	p.style.display = 'block';
}

function edit() {
	console.log('Edit!');
	post_id = this.getAttribute('pid');
	form = document.querySelector(`[fid="${post_id}"]`);
	p = document.querySelector(`[tid="${post_id}"]`);
	console.log(post_id);
	form.style.display = 'block';
	p.style.display = 'none';
}