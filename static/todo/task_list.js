document.addEventListener('DOMContentLoaded', function() {
	console.log('LOAD');
    setup();
	document.querySelectorAll('.check').forEach(el => {el.addEventListener('click', check);});
	document.querySelectorAll('.show_actions').forEach(el => {el.addEventListener('click', showActions);});
	document.querySelectorAll('.reminder').forEach(el => {el.addEventListener('click', sendReminder);});
	document.querySelector('#accept_btn').addEventListener('click', acceptShare);
	document.querySelector('#reject_btn').addEventListener('click', rejectShare);
});

async function sendReminder() {
    console.log('SEND REMINDER', this);
    share_id = this.getAttribute('share_id');
    to_whom = this.getAttribute('to_whom');
    await fetch(`/todo/reminder/${share_id}/${to_whom}`)
    .then (response => {
        console.log('reminder responce:', response);
        if (response == 200) {
            this.classList.replace('w3-text-red', 'w3-text-gray');
        }
    });
}

async function acceptShare() {
    console.log('ACCEPT', this);
    share_id = this.getAttribute('share_id');
    tid = this.getAttribute('tid');
    await fetch(`/todo/accept/${share_id}`)
    .then (response => console.log('Accept:', response));

    this.classList.replace('w3-white', 'w3-green');
    reject_btn = document.querySelector(`#reject_btn`);
    reject_btn.classList.replace('w3-red', 'w3-white');

    hand = document.querySelector(`.fa-hand-o-right[tid="${tid}"]`);
    hand.classList.replace('w3-text-red', 'w3-text-green');

    share_mode = document.querySelector(`.show_actions[tid="${tid}"] share`);
    share_mode.setAttribute('accept', 'green');
    share_mode.setAttribute('reject', 'white');

    hand.scrollIntoView();
    window.scrollBy(0,-100);
}

async function rejectShare() {
    console.log('REJECT', this);
    share_id = this.getAttribute('share_id');
    tid = this.getAttribute('tid');
    await fetch(`/todo/reject/${share_id}`)
    .then (response => console.log('Reject:', response));

    this.classList.replace('w3-white', 'w3-red');
    accept_btn = document.querySelector(`#accept_btn`);
    accept_btn.classList.replace('w3-green', 'w3-white');

    hand = document.querySelector(`.fa-hand-o-right[tid="${tid}"]`);
    hand.classList.replace('w3-text-green', 'w3-text-red');

    share_mode = document.querySelector(`.show_actions[tid="${tid}"] share`);
    share_mode.setAttribute('accept', 'white');
    share_mode.setAttribute('reject', 'red');

    hand.scrollIntoView();
    window.scrollBy(0,-100);
}


function setup() {
    console.log('SETUP');
    const tasks = document.querySelectorAll('.task');
    console.log('TASKS =', tasks);
    for (i = 0; i < tasks.length; i++)  {
        console.log('task = ', tasks[i]);
        const state = tasks[i].getAttribute('state');
        const tid = tasks[i].getAttribute('tid');
        const icon = document.querySelector(`[cid="${tid}"]`);
        const name = document.querySelector(`.name[tid="${tid}"]`);
        console.log('icon = ', icon);
        if (state == 'False') {
            icon.className = 'check fa fa-square-o';
            tasks[i].style.color = "blue";
            name.style.color = "blue"
            name.style.textDecoration = "none";
        } else {
            icon.className = 'check fa fa-check-square-o';
            tasks[i].style.color = "green";
            name.style.color = "green"
            name.style.textDecoration = "line-through";
        }
    }
}

function showActions() {
    tid = this.getAttribute('tid');
    modal = document.querySelector('#actions');
    modal.style.display = 'block';
    actions = document.querySelectorAll('.action');
    for (i = 0; i < actions.length; i++) {
        href = actions[i].getAttribute('href');
        console.log('href:', href, tid);
        href = href.replace('123456', tid);
        console.log('href=', href, tid);
        actions[i].setAttribute('href', href);
    }
    accept_btn = document.querySelector('#accept_btn');
    reject_btn = document.querySelector('#reject_btn');
    share_mode = document.querySelector(`.show_actions[tid="${tid}"] share`);
    console.log('Actions!', this, tid, "Share:", share_mode);
    if (share_mode == null) {
        accept_btn.style.display = 'none';
        reject_btn.style.display = 'none';
        console.log('share-mode null', share_mode);
    } else {
        share_id = share_mode.getAttribute('share_id');
        accept_btn.setAttribute('share_id', share_id);
        reject_btn.setAttribute('share_id', share_id);
        accept_btn.setAttribute('tid', tid);
        reject_btn.setAttribute('tid', tid);
        a_color = 'w3-' + share_mode.getAttribute('accept');
        r_color = 'w3-' + share_mode.getAttribute('reject');
        accept_btn.classList.replace('w3-white', a_color);
        reject_btn.classList.replace('w3-white', r_color);
        accept_btn.style.display = 'inline-block';
        reject_btn.style.display = 'inline-block';
    }
}


async function check() {
    console.log('this =', this)
	const task = this.parentNode;
	const icon = this;
	const task_id = task.getAttribute('tid');
	const state = task.getAttribute('state');
	const name = document.querySelector(`.name[tid="${task_id}"]`);
	console.log(task_id, state, name);
    if (state == 'False') {
        task.setAttribute('state', 'True');
        icon.className = 'check fa fa-check-square-o';
        task.style.color = "green";
        name.style.color = "green"
        name.style.textDecoration = "line-through";
    } else {
        task.setAttribute('state', 'False');
        icon.className = 'check fa fa-square-o';
        task.style.color = "blue";
        name.style.color = "blue"
        name.style.textDecoration = "none";
    }

	let post = {
		task_id: task_id
	};
	console.log(post);
	let response = await fetch('/todo/check', {
		method: 'POST',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});
	let result = await response;
	console.log(result.status);
}

var pusher = new Pusher('bbe70803665a7a964619', {
  cluster: 'eu'
});

var channel = pusher.subscribe('my-channel');

channel.bind('todo_task_toggle_checked', toggleChecked);

function toggleChecked(data) {
    const params = data; // JSON.stringify(data);
    console.log('PUSHER TOGGLE CHECKED:', params);
    const task_id = params['task_id'];
    const state = params['checked'];

	const icon = document.querySelector(`.check[cid="${task_id}"]`);
	const name = document.querySelector(`.name[tid="${task_id}"]`);
	const task = document.querySelector(`.task[tid="${task_id}"]`);
	console.log(task_id, state, name);
    if (state) {
        task.setAttribute('state', 'True');
        icon.className = 'check fa fa-check-square-o';
        task.style.color = "green";
        name.style.color = "green"
        name.style.textDecoration = "line-through";
    } else {
        task.setAttribute('state', 'False');
        icon.className = 'check fa fa-square-o';
        task.style.color = "blue";
        name.style.color = "blue"
        name.style.textDecoration = "none";
    }
}




