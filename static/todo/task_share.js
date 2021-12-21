document.addEventListener('DOMContentLoaded', function() {
	console.log('LOAD Task_Share');
	document.querySelectorAll('.add').forEach(el => el.addEventListener('click', addUser));
	document.querySelectorAll('.remove').forEach(el => el.addEventListener('click', removeUser));
});

async function addUser() {
	console.log('Add!', this);
	const tid = this.getAttribute('tid');
	const uid = this.getAttribute('uid');
	const shared_to = document.querySelector('#shared_to');
	const users = document.querySelector('#users');
	let post = {
		task_id: tid,
		user_id: uid
	};
	console.log(post);
	let response = await fetch('/todo/add_share', {
		method: 'POST',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});
	let result = await response;
	console.log(result.status);
	if (result.status == 200) {
	    this.className = 'remove';
	    this.removeEventListener("click", addUser);
	    this.addEventListener('click', removeUser)
	    shared_to.appendChild(this);
	}
}

async function removeUser() {
	console.log('Remove!', this);
	const tid = this.getAttribute('tid');
	const uid = this.getAttribute('uid');
	const shared_to = document.querySelector('#shared_to');
	const users = document.querySelector('#users');
	let post = {
		task_id: tid,
		user_id: uid
	};
	console.log(post);
	let response = await fetch('/todo/remove_share', {
		method: 'POST',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});
	let result = await response;
	console.log(result.status);
	if (result.status == 200) {
	    this.className = 'add';
	    this.removeEventListener("click", removeUser);
	    this.addEventListener('click', addUser)
	    users.appendChild(this);
	}
}

