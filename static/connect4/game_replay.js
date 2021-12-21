var GAMEOVER = false
var STEP = 0
var MARK = 1
var THINKING = false

var PRED_MOVE
var AUTO = false
var IS_BOT = [true, false, false]
var NAMES = ["", "", ""]

var MOVES = []

var el_moved_circle
var el_current_circle
var el_moved_name
var el_current_name
var el_move_made
var el_delay
var el_current_step
var el_step
var el_step_num

var el_show_thinking
var el_show_gameover
var el_show_winner

var CHAMPIONSHIP = false

var PLAY = 1
const play_pause = ["<i class='fas fa-pause'>", "<i class='fas fa-play'>"]

DELAY = 1

const circles = ["<i class='fas fa-circle empty'></i>", "<i class='fas fa-circle first'></i>", "<i class='fas fa-circle second'></i>"]
const dot_circles = ["<i class='fas fa-skull-crossbones empty'></i>", "<i class='fas fa-skull-crossbones first'></i>", "<i class='fas fa-skull-crossbones second'></i>"]
const rings = ["<i class='far fa-circle first'></i>", "<i class='far fa-circle second'></i>", "<i class='far fa-circle both'></i>"]

const circle_classes = ['fas fa-circle empty', 'fas fa-circle first', 'fas fa-circle second']
const dot_circle_classes = ['fas fa-skull-crossbones empty', 'fas fa-skull-crossbones first', 'fas fa-skull-crossbones second']
const ring_classes = ['far fa-circle first', 'far fa-circle second', 'far fa-circle both']

var GRID = [
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    ]

function settings(){
    const first_name = document.getElementById("first_player_name").innerHTML;
    NAMES[1] = first_name;
    const second_name = document.getElementById("second_player_name").innerHTML;
    NAMES[2] = second_name;

    el_moved_circle = document.getElementById("moved_circle");
    el_current_circle = document.getElementById("current_circle");
    el_moved_name = document.getElementById("moved_name");
    el_current_name = document.getElementById("current_name");
    el_move_made = document.getElementById("move_made");
    el_delay = document.getElementById("delay");
    el_current_step = document.getElementById("current_step");

    el_show_thinking = document.getElementById("show_thinking");
    el_show_gameover = document.getElementById("show_gameover");
    el_show_winner = document.getElementById("show_winner");

    moves = document.getElementById("moves").innerHTML;
    for (let i = 0; i < moves.length; i++) {
        MOVES.push(Number(moves.charAt(i)));
    }

    console.log('moves', MOVES)

    el_step = document.getElementById("step");
    el_step.value = STEP;
    console.log('el_step', el_step)
    el_step_num = document.getElementById("step_num");
    el_step.innerHTML = STEP;


}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function changeCell(row, col, mark) {
    const cell = document.querySelector(`[r="${row}"][c="${col}"]`);
    console.log('change', row, col, mark);
    if (cell == null) {
        console.log('changeCell, cell', row, col, 'not found');
    } else {
        if (mark < 3) {
            cell.innerHTML = circles[mark];
        } else {
            if (mark < 6) {
                cell.innerHTML = rings[mark-3];
            } else {
                cell.innerHTML = dot_circles[mark-6];
            }
        }
    }
}

function place(row, col, mark) {
    GRID[row][col] = mark;
    changeCell(row, col, mark);
}

function showMove(col) {
    if (GRID[0][col] == 0) {
        row = 0;
        while ((row < 6) && (GRID[row][col] == 0)) {
            row++;
        }
        row--;
        changeCell(row, col, MARK);
        GRID[row][col] = MARK;
    } else {
        console.log('column full')
    }
}

function hideMove(col) {
    row = 0;
    while ((row < 5) && (GRID[row][col] == 0)) {
        row++;
    }
    changeCell(row, col, 0);
    GRID[row][col] = 0;
}

function update(result) {
    console.log(result);
    GAMEOVER = result['gameover']
    console.log(GAMEOVER);
    if (GAMEOVER != true) {
        signal = result['signal'];
        for (let r = 0; r < 6; r++) {
            for (let c = 0; c < 7; c++) {
                v = signal[r][c];
                if (v > 0) {
                    changeCell(r, c, v+2);
                }
            }
        }
        MARK = 3 - MARK;
        STEP++;
        el_moved_circle.innerHTML = circles[3-MARK];
        el_current_circle.innerHTML = circles[MARK];
        el_moved_name.innerHTML = NAMES[3-MARK];
        el_current_name.innerHTML = NAMES[MARK];
        el_move_made.innerHTML = result['move'];
        el_delay.innerHTML = result['delay'];
        el_current_step.innerHTML = STEP;

        if (IS_BOT[MARK]) {
            play_bot();
        } else {
            THINKING = false;
            el_show_thinking.innerHTML = "";
        }
    } else {
        el_show_gameover.innerHTML = "GAME OVER";
        win = result['winner'];
        if (win > 0) {
            el_show_winner.innerHTML = NAMES[win] + " wins";
            four = result['four'];
            for (let i = 0; i < 4; i++) {
                changeCell(four[i][0], four[i][1], win+6);
                console.log(four[i], win+6);
            }
        } else {
            el_show_winner.innerHTML = "TIE";
        }
        if (CHAMPIONSHIP) {
            url = `/four/play_bot_championship`;
            console.log('Championship new game ');
            document.location.href = url;
        }
    }
}

function changeDelay() {
    DELAY = this.value;
}

function forward() {
    if (STEP <= MOVES.length) {
        showMove(MOVES[STEP]);
        if (STEP >= MOVES.length-1) {
            console.log('GAEOVER');
            winning(MARK);
        }
        console.log(STEP, MOVES[STEP], MARK);
        STEP++;
        MARK = 3 - MARK;
        el_step.value = STEP;
        el_step_num.innerHTML = STEP;
    }
}

function backward() {
    if (STEP > 0) {
        if (STEP >= MOVES.length-1) {
            console.log('GAMEOVER----');
            showGrid();
        }
        STEP--;
        hideMove(MOVES[STEP]);
        console.log(STEP, MOVES[STEP], MARK);
        MARK = 3 - MARK;
        el_step.value = STEP;
        el_step_num.innerHTML = STEP;
    }
}

function reset() {
    STEP = 0
    MARK = 1
    for (let r = 0; r < 6; r++){
        for (let c = 0; c < 7; c++) {
            GRID[r][c] = 0;
            changeCell(r, c, 0);
        }
    }
    el_step.value = 0;
    el_step_num.innerHTML = 0;
}

function showGrid() {
    for (let r = 0; r < 6; r++){
        for (let c = 0; c < 7; c++) {
            changeCell(r, c, GRID[r][c]);
        }
    }
}

function changeStep() {
    v = this.value;
    console.log('step ->', v);
    if (v > STEP) {
        for (let i = STEP; i < v; i++) {
            forward();
        }
    }
    if (v < STEP) {
        for (let i = STEP+1; i >= v; i--) {
            backward();
        }
    }
}

function playPause() {
    PLAY = 1 - PLAY;
    this.innerHTML = play_pause[PLAY];
}

function winning(piece) {
    console.log('winning', piece);
    // horizontal
    for (let r = 0; r < 6; r++) {
        for (let c = 0; c < 7; c++) {
            let count = 0;
            for (let i = c; i < c+4; i++) {
                if (GRID[r][i] == piece) {
                    count++;
                }
            }
            if (count == 4) {
                for (let i = c; i < c+4; i++) {
                    changeCell(r, i, piece+6);
                }
            }
        }
    }
    // vertical
    for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 7; c++) {
            let count = 0;
            for (let i = r; i < r+4; i++) {
                if (GRID[i][c] == piece) {
                    count++;
                }
            }
            if (count == 4) {
                for (let i = r; i < c+4; i++) {
                    changeCell(i, c, piece+6);
                }
            }
        }
    }
    // positive diagonal
    for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 4; c++) {
            let count = 0;
            for (let i = 0; i < 4; i++) {
                if (GRID[r+i][c+i] == piece) {
                    count++;
                }
            }
            if (count == 4) {
                for (let i = 0; i < 4; i++) {
                    changeCell(r+i, c+i, piece+6);
                }
            }
        }
    }
    // negative diagonal
    for (let r = 3; r < 6; r++) {
        for (let c = 0; c < 4; c++) {
            let count = 0;
            for (let i = 0; i < 4; i++) {
                if (GRID[r-i][c+i] == piece) {
                    count++;
                }
            }
            if (count == 4) {
                for (let i = 0; i < 4; i++) {
                    changeCell(r-i, c+i, piece+6);
                }
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
	document.querySelector("#forward").addEventListener('click', forward, false);
	document.querySelector("#backward").addEventListener('click', backward, false);
	document.querySelector("#reset").addEventListener('click', reset, false);
	document.querySelector("#step").addEventListener('change', changeStep, false);

    console.log('GAME replay');
    settings();
});

















