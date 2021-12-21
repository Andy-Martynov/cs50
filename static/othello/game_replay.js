var STEP = 1
var MARK = 1
var THINKING = false

var PRED_MOVE
var AUTO = false
var IS_BOT = [true, false, false]
var NAMES = ["", "", ""]

var MOVES = [[0,0,0]]

var PAUSE = false

var GAME_ID
var UID

var HUMAN_NUM

var el_moved_circle
var el_moved_name
var el_move_made
var el_current_circle

var el_qty1
var el_qty2

var el_current_step
var el_step
var el_step_num

var el_human_num

var el_show_gameover
var el_show_winner
var el_show_your_turn

const stones =   ["<img src='/media/othello/images/white_50.png' class='empty no'>",
                  "<img src='/media/othello/images/black_50.png' class=''>",
                  "<img src='/media/othello/images/white_50.png' class=''>",
                  "<img src='/media/othello/images/white_50.png' class='empty no'>",
                  "<img src='/media/othello/images/white_50.png' class='empty yes'>",
                  "<img src='/media/othello/images/white_50.png' class='empty yes'>",
                  "<img src='/media/othello/images/white_50.png' class='empty no'>",
                  "<img src='/media/othello/images/yes_50.png' class=''>",
                  "<img src='/media/othello/images/yes_50.png' class=''>",
                  "<img src='/media/othello/images/white_50.png' class='empty'>",
                 ]

const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

var GRID = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,2,1,0,0,0],
    [0,0,0,1,2,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    ]

var GRIDS = [GRID]

function changeCell(row, col, mark) {
    const cell = document.querySelector(`[r="${row}"][c="${col}"]`);
    if (cell == null) {
        console.log('changeCell, cell', row, col, 'not found');
    } else {
        cell.innerHTML = stones[mark];
    }
}

function settings(){
    GAME_ID = document.getElementById("game_id").innerHTML;
    UID = document.getElementById("uid").innerHTML;

    const first_name = document.getElementById("first_player_name").innerHTML;
    NAMES[1] = first_name;
    const second_name = document.getElementById("second_player_name").innerHTML;
    NAMES[2] = second_name;

    el_current_step = document.getElementById("current_step");

    HUMAN_NUM = document.getElementById("human_num").innerHTML;

    el_moved_circle = document.getElementById("moved_circle");
    el_current_circle = document.getElementById("current_circle");

    el_moved_name = document.getElementById("moved_name");
    el_current_name = document.getElementById("current_name");

    el_move_made = document.getElementById("move_made");
    el_current_step = document.getElementById("current_step");

    el_show_thinking = document.getElementById("show_thinking");
    el_show_gameover = document.getElementById("show_gameover");
    el_show_winner = document.getElementById("show_winner");
    el_show_your_turn = document.getElementById("show_your_turn");

    el_qty1 = document.getElementById("qty1");
    el_qty2 = document.getElementById("qty2");

    moves = document.getElementById("moves").innerHTML;
    for (let i = 0; i < moves.length; i=i+3) {
        MOVES.push([Number(moves.charAt(i)), Number(moves.charAt(i+1)), Number(moves.charAt(i+2))]);
    }
    console.log('moves', MOVES)

    el_step = document.getElementById("step");
    el_step.value = STEP;
    // el_step_num = document.getElementById("step_num");
    // el_step.innerHTML = STEP;
}


function update(data) {
    console.log('I am update', STEP, GRIDS);
    mark = MOVES[STEP-1][0]
    row = MOVES[STEP-1][1]
    column = MOVES[STEP-1][2]
    showGrid(GRIDS[STEP-1]);

    last_move = MOVES.length-1;

    if (STEP == last_move) {
        GAMEOVER = true;
    } else {
        GAMEOVER = false;
    }
    el_show_gameover.style.visibility = 'hidden';
    el_show_winner.style.visibility = 'hidden';

    if (STEP == 1) {
        el_moved_circle.innerHTML = stones[0];
        el_moved_name.style.visibility = 'hidden';
        el_move_made.style.visibility = 'hidden';
    } else {
        el_moved_circle.innerHTML = stones[mark];
        el_moved_name.innerHTML = NAMES[mark] + ' ';
        el_moved_name.style.visibility = 'visible';
        el_move_made.innerHTML = letters[column] + `${8-row}`;
        el_move_made.style.visibility = 'visible';
    }

    one = 0;
    two = 0;
    for (r = 0; r < GRIDS[STEP-1].length; r++)  {
        for (c = 0; c < GRIDS[STEP-1][r].length; c++)  {
            if (GRIDS[STEP-1][r][c] == 1) {
                one++;
            }
            if (GRIDS[STEP-1][r][c] == 2) {
                two++;
            }
        }
    }

    el_qty1.innerHTML = one
    el_qty2.innerHTML = two
    win = 0;
    if (one > two) {
        win = 1;
    }
    if (one < two) {
        win = 2;
    }

    if (GAMEOVER) {
        el_show_gameover.style.visibility = 'visible';
        el_show_winner.style.visibility = 'visible';
        if (win > 0) {
            el_show_winner.innerHTML = NAMES[win] + " wins";
        } else {
            el_show_winner.innerHTML = "TIE";
        }
    }
}

function showGrid(grid) {
    for (r=0; r < grid.length; r++){
        for (c=0; c < grid[r].length; c++) {
            changeCell(r, c, grid[r][c]);
        }
    }
}

function forward() {
    if (STEP < MOVES.length) {
        STEP++;
        update();
        el_step.value = STEP;
    }
}

async function getGrids() {
    for (let move = 1; move < MOVES.length; move++) {
        mark = MOVES[move][0]
        row = MOVES[move][1]
        column = MOVES[move][2]
        // console.log('I am getGrids, asc the server to show the move', move, mark, row, column, GRIDS[move-1], 'waiting response ...')
        await fetch('/othello/make_move', {
            method: 'POST',
            body: JSON.stringify({
                row: row,
                column: column,
                mark: mark,
                grid: GRIDS[move-1],
                })
            })
        .then((response) => response.json())
        .then(data => {
                GRIDS.push(data['grid']);
                // console.log(data);
        });
    }
    document.querySelector('#replay-loading').style.display = 'none';
    document.querySelectorAll('.replay-control').forEach((el) => {el.style.visibility = 'visible'});
}

function backward() {
    if (STEP > 1) {
        STEP--;
        el_step.value = STEP;
        update();
    }
}

function reset() {
    STEP = 1
    el_step.value = 1;
    update();
}

function changeStep() {
    v = this.value;
    console.log('step ->', v);
    STEP = v;
    update();
}


document.addEventListener('DOMContentLoaded', function() {
    showGrid(GRID);
    changeCell(2,3,4);
    changeCell(3,2,4);
    changeCell(4,5,4);
    changeCell(5,4,4);

    settings();
    getGrids();

	document.querySelector("#forward").addEventListener('click', forward, false);
	document.querySelector("#backward").addEventListener('click', backward, false);
	document.querySelector("#reset").addEventListener('click', reset, false);
	document.querySelector("#step").addEventListener('change', changeStep, false);

    console.log('GAME replay');
});


