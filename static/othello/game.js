var GAMEOVER = false
var STEP = 1
var MARK = 1
var THINKING = false

var IS_BOT = [true, false, false]
var NAMES = ["", "", ""]
var BOTH_ARE_BOTS = false

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

var el_replay

var el_pause
var el_forward

var el_human_num

var el_show_gameover
var el_show_winner
var el_show_your_turn

var CHAMPIONSHIP = false

const circles = ["<i class='fas fa-circle empty no'></i>",
                 "<i class='fas fa-circle first no'></i>",
                 "<i class='fas fa-circle second no'></i>",
                 "<i class='fas fa-circle empty no'></i>",
                 "<i class='fas fa-circle empty yes'></i>",
                 "<i class='fas fa-circle empty yes'></i>",
                 "<i class='fas fa-circle empty no'></i>",
                 "<i class='far fa-circle first game-opacity yes'></i>",
                 "<i class='far fa-circle second game-opacity yes'></i>",
                 "<i class='far fa-circle both game-opacity yes'></i>"
                 ]
const stones =   ["<img src='/media/othello/images/white_50.png' class='empty no'>",
                  "<img src='/media/othello/images/black_50.png' class=''>",
                  "<img src='/media/othello/images/white_50.png' class=''>",
                  "<img src='/media/othello/images/white_50.png' class='empty no'>",
                  "<img src='/media/othello/images/white_50.png' class='empty yes'>",
                  "<img src='/media/othello/images/white_50.png' class='empty yes'>",
                  "<img src='/media/othello/images/white_50.png' class='empty no'>",
                  "<img src='/media/othello/images/yes_40.png'>",
                  "<img src='/media/othello/images/yes_40.png'>",
                  "<img src='/media/othello/images/white_50.png' class='empty'>",
                 ]

const rolling_stones =   ["<img src='/media/othello/images/white_50.png' class='empty no'>",
                  "<img src='/media/othello/images/black_50.png' class='rolling'>",
                  "<img src='/media/othello/images/white_50.png' class='rolling'>",
                 ]

const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

const cursors = ["<i class='fas fa-skull-crossbones empty no'></i>", "<i class='fas fa-skull-crossbones empty yes'></i>", "<i class='fas fa-skull-crossbones empty yes'></i>"]
const rings = []

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

var forwardpressed = false;

function changeCell(row, col, mark) {
    const cell = document.querySelector(`[r="${row}"][c="${col}"]`);
    if (cell == null) {
        console.log('changeCell, cell', row, col, 'not found');
    } else {
        cell.innerHTML = stones[mark];
    }
}

function waitForForward() {
    PAUSE = confirm('PAUSE?');
}

function pause() {
    if (PAUSE) {
        PAUSE = false;
        forwardpressed = true;
        el_pause.innerHTML = "<i class='fas fa-pause'></i>";
    } else {
        el_pause.innerHTML = "<i class='fas fa-play'></i>";
        PAUSE = true;
        fowardpressed = false;
    }
}

function forward() {
    forwardpressed = true;
}


function settings(){
    GAME_ID = document.getElementById("game_id").innerHTML;
    UID = document.getElementById("uid").innerHTML;

    const first_name = document.getElementById("first_player_name").innerHTML;
    NAMES[1] = first_name;
    const second_name = document.getElementById("second_player_name").innerHTML;
    NAMES[2] = second_name;
    const first_mode = document.getElementById("first_mode");
    if (first_mode.innerHTML == "bot") {
        IS_BOT[1] = true;
    }
    const second_mode = document.getElementById("second_mode");
    if (second_mode.innerHTML == "bot") {
        IS_BOT[2] = true;
    }
    const championship = document.getElementById("championship");
    if (championship.innerHTML == "True") {
        CHAMPIONSHIP = true;
    }

    if (IS_BOT[1] && IS_BOT[2]) {
        BOTH_ARE_BOTS = true
    }

    HUMAN_NUM = document.getElementById("human_num").innerHTML;

    el_moved_circle = document.getElementById("moved_circle");
    el_moved_circle.innerHTML = rolling_stones[3-HUMAN_NUM]

    el_current_circle = document.getElementById("current_circle");
    el_current_circle.innerHTML = rolling_stones[HUMAN_NUM]

    el_moved_name = document.getElementById("moved_name");
    el_moved_name.innerHTML = NAMES[3-HUMAN_NUM]

    el_move_made = document.getElementById("move_made");

    el_show_gameover = document.getElementById("show_gameover");
    el_show_winner = document.getElementById("show_winner");
    el_show_your_turn = document.getElementById("show_your_turn");

    el_qty1 = document.getElementById("qty1");
    el_qty2 = document.getElementById("qty2");

    el_depth = document.getElementById("depth");
    el_replay = document.getElementById("replay");

    el_pause = document.getElementById("pause");
    el_forward = document.getElementById("forward");
}

function move() {
    col = this.getAttribute('c');
    row = this.getAttribute('r');

    console.log('human move hn mark GAMEOVER', row, col, HUMAN_NUM, MARK, GAMEOVER);
    if (!GAMEOVER) {
        if (THINKING) {
            console.log('I am thinking!!!')
        } else {
            if (MARK != HUMAN_NUM) {
                console.log('It is not your turn!');
            } else {
                if (GRID[row][col] == 0) {
                    console.log('YOUR MOVE:', row, col, 'call play human')
                    play_human(row, col);
                } else {
                    console.log('cell full')
                }
            }
        }
    } else {
        console.log('GAMEOVER!!!')
    }
}

function play_human(row, col) {
    console.log('I am play_human, asc the server to use the move', row, col, 'waiting response ...')
    fetch('/othello/play', {
        method: 'POST',
        body: JSON.stringify({
            row: row,
            column: col,
            game_id: GAME_ID,
            })
        })
    .then((response) => response.json())
    .then(data => {
        console.log('Call update')
        update(data);
    })
    .then(message => {
        console.log(message);
    });
}

function update(data) {
    console.log('I am update, the data:', data);

    valid_move = data['valid_move'] // update only if the move was valid

    if (valid_move == 'yes') {
        console.log('OK, the move was valid, processing ...')

        grid = data['grid'];
        copyGrid(grid);

        gameover = data['gameover'];
        if (gameover != undefined) {
            GAMEOVER = GAMEOVER || gameover;
        }

        PREV = data['prev']
        MARK = data['mark'];

        if (BOTH_ARE_BOTS){
            el_moved_circle.innerHTML = stones[3-MARK];
            el_moved_name.innerHTML = NAMES[3-MARK] + ' ';
            el_move_made.innerHTML = letters[data['move']['column']] + `${8-data['move']['row']}`;
        }

        el_moved_name.style.visibility = 'visible';
        el_moved_circle.style.visibility = 'visible';
        el_move_made.style.visibility = 'visible';

        move_made = data['move']
        if (move_made != null) {
            el_move_made.innerHTML = letters[data['move']['column']] + `${8-data['move']['row']}`;
            el_move_made.style.visibility = 'visible';
        }

        el_qty1.innerHTML = data['qty1']
        el_qty2.innerHTML = data['qty2']

        signal = data['signal'];
        if (signal != null) {
            for (let r = 0; r < 8; r++) {
                for (let c = 0; c < 8; c++) {
                    v = signal[r][c];
                    if (v > 0) {
                        changeCell(r, c, v+3);
                    }
                }
            }
        }

        if (!GAMEOVER) { // GAME IS NOT OVER
            console.log('GAME IS NOT OVER');

            console.log('The next is #', MARK, 'IS_BOT:', IS_BOT[MARK]);
            if (!BOTH_ARE_BOTS) {
                if (MARK == HUMAN_NUM) {
                    THINKING = false;
                    el_show_your_turn.style.visibility = 'visible';
                    el_moved_circle.innerHTML = stones[3-HUMAN_NUM];
                } else {
                    THINKING = true;
                    el_show_your_turn.style.visibility = 'hidden';
                    el_moved_name.innerHTML = NAMES[MARK];
                    el_move_made.innerHTML = "....";
                    el_moved_circle.innerHTML = rolling_stones[3-HUMAN_NUM];
                }
            }
            if (IS_BOT[MARK]) {
                console.log('Update calls play_bot');
                // el_moved_name.innerHTML = NAMES[MARK];
                play_bot();
            }
        } else { // GAME OVER
            console.log('T H E  G A M E  I S  O V E R ! ! !');
            el_replay.style.visibility = 'visible';
            el_show_your_turn.style.display = 'none';
            el_pause_tr = document.getElementById("pause-tr");
            if (el_pause_tr != null) {
                el_pause_tr.style.display = 'none';
            }
            el_show_gameover.innerHTML = "GAME OVER";
            win = data['winner'];
            if (win > 0) {
                el_show_winner.innerHTML = NAMES[win] + " wins";
            } else {
                el_show_winner.innerHTML = "TIE";
            }
            if (CHAMPIONSHIP) {
                url = `/game/play_bot_championship/othello`;
                console.log('Championship new game ');
                document.location.href = url;
            }
        }
    } else {
        console.log('invalid move!!!!!!!!!!!!!!!!!!!!!!!!')
    }
}

function opponentMove(data) {
    console.log('OPPONENT MOVE', data)
    game_id = data['game_id']
    if ((HUMAN_NUM != MARK) && (game_id == GAME_ID) && !GAMEOVER) {
        console.log('----- opponent move calls update ------', !gameover)
        if (!IS_BOT[data['mark']]) {
            update(data);
        }

    }
}

function play_bot() {
    console.log('I am play_bot, bot name:', GAME_ID, NAMES[MARK], 'PAUSE:', PAUSE);
    console.log('I called the server and the data is:');
    if (!GAMEOVER) {
        if (PAUSE) {
            console.log('PAUSE')
            forwarspressed = false;
            waitForForward();
        }
        THINKING = true;
        fetch('/othello/play', {
            method: 'PUT',
            body: JSON.stringify({
                game_id: GAME_ID,
                })
            })
        .then((response) => response.json())
        .then(data => {
            console.log('Call update')
            update(data);
        });
        // .then(message => {
        //     console.log(message);
        // })
    }
}

function showGrid() {
    for (r=0; r < GRID.length; r++){
        for (c=0; c < GRID[r].length; c++) {
            changeCell(r, c, GRID[r][c]);
        }
    }
}

function copyGrid(grid) {
    for (r=0; r < GRID.length; r++){
        for (c=0; c < GRID[r].length; c++) {
            GRID[r][c] = grid[r][c];
            changeCell(r, c, GRID[r][c]);
        }
    }
}


document.addEventListener('DOMContentLoaded', function() {

    var pusher = new Pusher('bbe70803665a7a964619', {
      cluster: 'eu'
    });
    var channel = pusher.subscribe('my-channel');
    channel.bind('othello_move', opponentMove);

    showGrid();
    changeCell(2,3,4);
    changeCell(3,2,4);
    changeCell(4,5,4);
    changeCell(5,4,4);

	document.querySelectorAll('.cell').forEach(el => el.addEventListener('click', move));

    settings();
    console.log('GAME OTHELLO, MARK:', MARK, 'IS_BOT:', IS_BOT);
    console.log('GAME_ID:', GAME_ID, "UID:", UID)

    if (IS_BOT[MARK] && IS_BOT[3-MARK]) {
        console.log('Both players are bots, switch PAUSE on')
        let PAUSE = true;
    }

    // if (IS_BOT[1] && IS_BOT[2]) {
    //     PAUSE = true;
    // }

    if (IS_BOT[MARK]) {
        console.log('The first is bot, call play_bot')
        play_bot();
    }
});


