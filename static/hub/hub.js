document.addEventListener('DOMContentLoaded', function() {
	console.log('LOAD');
	helpSetup();
    document.querySelectorAll('.like').forEach(el => el.addEventListener('click', like));
	document.querySelectorAll('.edit').forEach(el => el.addEventListener('click', edit));
	document.querySelectorAll('.save').forEach(el => el.addEventListener('click', save));
	document.querySelectorAll('.flag').forEach(el => el.addEventListener('click', language));
    document.querySelectorAll('[rus]').forEach(el => el.setAttribute('eng', el.innerHTML));
});

function language() {
    console.log('Lang', this.id);
    if (this.id == 'rus') {
        document.querySelectorAll('[rus]').forEach(el => el.innerHTML = el.getAttribute('rus'));
    } else {
        document.querySelectorAll('[eng]').forEach(el => el.innerHTML = el.getAttribute('eng'));
    }
}

function helpSetup() {
    const btn = document.querySelector('#help-button');
    const content = document.querySelector('#help-content').innerHTML;
    console.log("Content <", content, ">");
    if (content == "") {
        btn.style.display = "none";
    }
}


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
		console.log('label:', label);
		if (label == '👍' ) {
			this.innerHTML = '&#128078;';
			counter.innerHTML = num + 1;
		} else {
			this.innerHTML = '&#128077;';
			counter.innerHTML = num - 1;
		}
		console.log('counter:', counter.innerHTML, this.innerHTML);
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