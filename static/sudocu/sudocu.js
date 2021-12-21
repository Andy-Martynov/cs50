// function show_hint() {
// 	const hint = this.getAttribute('hint');
// 	console.log(hint);
// 	const hint_place =document.getElementById('hint');
// 	hint_place.innerHTML = `(${this.id})=${hint}`;
// }

var gr
var gc

function move() {
    console.log('MOVE');
    const num_pad = document.getElementById('num_pad');
    num_pad.style.visibility = 'visible';
	const r = this.getAttribute('r');
	const c = this.getAttribute('c');
    console.log(r, c);
    gr = r;
    gc = c;
//     document.location.href = `/sudocu/move/${r}/${c}/${v}`;
}
function send_move() {
	const v = this.innerHTML;
	console.log('move', gr, gc, v, `/sudocu/move/${gr}/${gc}/${v}`);
    document.location.href = `/sudocu/move/${gr}/${gc}/${v}`;

    const num_pad = document.getElementById('num_pad');
    num_pad.style.visibility = 'hidden';
}
function make_move() {
	const hint = this.getAttribute('hint');
	const v = this.value;
	const r = this.getAttribute('r');
	const c = this.getAttribute('c');
	console.log(hint, r, c, v, `/sudocu/move/${r}/${c}/${v}`);
    document.location.href = `/sudocu/move/${r}/${c}/${v}`;
}
function random_sudocu() {
	const n = this.value;
    document.location.href = `/sudocu/random/${n}`;
}
function save_sudocu() {
    const name = document.getElementById('game_name').value;
	console.log('SAVE', name)
    document.location.href = `/sudocu/save/${name}`;
}
function load_sudocu() {
	console.log('LOAD')
    document.location.href = `/sudocu/load`;
}
function toggle_h() {
	console.log('TOGGLE')
	if (this.style.color == 'green') {
	    this.style.color = 'red'
    	document.querySelectorAll('.hint').forEach(el => el.style.visibility = 'visible');
	} else {
	    this.style.color = 'green'
    	document.querySelectorAll('.hint').forEach(el => el.style.visibility = 'hidden');
	}
}

document.addEventListener('DOMContentLoaded', function() {

//     cells = document.querySelectorAll('.cell');
//     hints = document.querySelectorAll('.hint');
// 	cells.forEach(el => el.addEventListener('change', make_move));
// 	cells.forEach(el => el.addEventListener('click', move));
// 	hints.forEach(el => el.addEventListener('click', move));

	document.querySelectorAll('.tde').forEach(el => el.addEventListener('click', move));
	document.querySelectorAll('.np').forEach(el => el.addEventListener('click', send_move));

    console.log('SUDOKU');

	const toggle_hints = document.getElementById('toggle_hints');
	toggle_hints.addEventListener('click', toggle_h);
// 	if (toggle_hints.style.color == 'red') {
//     	document.querySelectorAll('.hint').forEach(el => el.style.visibility = 'visible');
// 	}

	const level = document.getElementById('level');
	level.addEventListener('change', random_sudocu);

	document.getElementById('btn_save').addEventListener('click', save_sudocu);
	document.getElementById('btn_load').addEventListener('click', load_sudocu);

	const mode = document.getElementById('mode').innerHTML;
	console.log('Mode?', mode);
	if (mode == 'AI-cycle') {
	    console.log('AI-CYCLE!');
        document.location.href = `/sudocu/ai_move/AI-cycle`;
	}
});
