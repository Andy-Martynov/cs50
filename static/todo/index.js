document.addEventListener('DOMContentLoaded', function() {
	console.log('LOAD Todo');
    setup();
	document.querySelectorAll('.check').forEach(el => el.addEventListener('click', check));
	document.querySelectorAll('.name').forEach(el => el.addEventListener('click', showActions));
});

function setup() {
    console.log('SETUP');
    const tasks = document.querySelectorAll('.task');
    for (i=0; i < tasks.length; i++) {
        console.log(tasks[i]);
        const state = tasks[i].getAttribute('state');
        const tid = tasks[i].getAttribute('tid');
        const check = document.querySelector(`.check[cid="${tid}"]`);
        const name = document.querySelector(`.name[tid="${tid}"]`);
        console.log(tid, state, check, name);
        if (state == 'True') {
            name.style.color = "green";
            name.style.textDecoration = "line-through";
            check.className = "check fa fa-check-square-o";
        } else {
            name.style.color = "blue";
            check.className = "check fa fa-square-o";
        }
    }
}

function showActions() {
    console.log('showActions!')
    const actions = document.querySelector('#actions');
    actions.style.display = "block";
    const tid = this.getAttribute('tid');
    text = actions.innerHTML;
    actions.innerHTML = text.replace(/123456/g, tid);
}

async function check() {
	console.log('Check!', this);
	const check = this;
	const tid = this.getAttribute('cid');
	const name = document.querySelector(`.name[tid="${tid}"]`);
	const task = document.querySelector(`.task[tid="${tid}"]`);
    const state = task.getAttribute('state');
    if (state == 'False') {
        task.setAttribute('state', 'True');
        name.style.color = "green";
        name.style.textDecoration = "line-through";
        check.className = "check fa fa-check-square-o";
    } else {
        task.setAttribute('state', 'False');
        name.style.color = "blue";
        name.style.textDecoration = "none";
        check.className = "check fa fa-square-o";
    }
}

