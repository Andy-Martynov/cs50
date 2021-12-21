var GAMEOVER = false
var STEP = 1
var MARK = 1
var THINKING = false

var IS_BOT = [true, false, false]
var BOTH_ARE_BOTS = false
var NAMES = ["", "", ""]

var PAUSE = false

var GAME_ID
var UID

var HUMAN_NUM

var el_moved_circle
var el_moved_name
var el_move_made
var el_current_circle

var el_replay

var el_pause
var el_forward

var el_human_num

var el_show_gameover
var el_show_winner
var el_show_your_turn

var CHAMPIONSHIP = false

const circles = ["<img src='/media/connect4/images/white.png'>", "<img src='/media/connect4/images/red.png'>", "<img src='/media/connect4/images/yellow.png'>"]
const dot_circles = ["<img src='/media/connect4/images/white.png'>", "<img src='/media/connect4/images/red.png' class='win4'>", "<img src='/media/connect4/images/yellow.png' class='win4'>"]
const falling_circles = ["<img src='/media/connect4/images/white.png'>", "<img src='/media/connect4/images/red.png' class='drop'>", "<img src='/media/connect4/images/yellow.png' class='drop'>"]
const rings = ["<i class='far fa-circle first'></i>", "<i class='far fa-circle second'></i>", "<i class='far fa-circle both'></i>"]

var GRID = [
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    ]

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

    if (IS_BOT[1] && IS_BOT[2]) {
        BOTH_ARE_BOTS = true
    }

    const championship = document.getElementById("championship");
    if (championship.innerHTML == "True") {
        CHAMPIONSHIP = true;
    }

    HUMAN_NUM = document.getElementById("human_num").innerHTML;

    el_moved_circle = document.getElementById("moved_circle");
    el_moved_circle.innerHTML = circles[3-HUMAN_NUM]

    el_current_circle = document.getElementById("current_circle");
    el_current_circle.innerHTML = circles[HUMAN_NUM]

    el_moved_name = document.getElementById("moved_name");
    el_moved_name.innerHTML = NAMES[3-HUMAN_NUM]

    el_move_made = document.getElementById("move_made");

    el_show_gameover = document.getElementById("show_gameover");
    el_show_winner = document.getElementById("show_winner");
    el_show_your_turn = document.getElementById("show_your_turn");

    el_replay = document.getElementById("replay");

    el_pause = document.getElementById("pause");
    el_forward = document.getElementById("forward");
}

function pause() {
    if (PAUSE) {
        PAUSE = false;
        el_pause.innerHTML = "<i class='fas fa-pause'></i>";
    } else {
        el_pause.innerHTML = "<i class='fas fa-play'></i>";
        PAUSE = true;
    }
}
function forward() {
    console.log('>> forward');
}

function changeCell(row, col, mark) {
    const cell = document.querySelector(`[r="${row}"][c="${col}"]`);
    if (cell == null) {
        console.log('changeCell, cell', row, col, 'not found');
    } else {
        if (mark < 3) {
            cell.innerHTML = circles[mark];
        } else {
            if (mark < 6) {
                cell.innerHTML = rings[mark-3];
            } else {
                if (mark < 9) {
                    cell.innerHTML = dot_circles[mark-6];
                } else {
                    cell.innerHTML = falling_circles[mark-9];
                }
            }
        }
    }
}

function place(row, col, mark) {
    GRID[row][col] = mark;
    changeCell(row, col, mark);
}

function move() {
    col = this.getAttribute('c');
    console.log('human move hn mark GAMEOVER', col, HUMAN_NUM, MARK, GAMEOVER);
    if (!GAMEOVER) {
        if (THINKING) {
            console.log('I am thinking!!!')
        } else {
            if (MARK != HUMAN_NUM) {
                console.log('It is not your turn!');
            } else {
                if (GRID[0][col] == 0) {
                    THINKING = true;
                    row = 0;
                    while ((row < 6) && (GRID[row][col] == 0)) {
                        row++;
                    }
                    row--;
                    // changeCell(row, col, MARK, 0);
                    changeCell(row, col, MARK+9, 0);
                    GRID[row][col] = MARK;
                    play_human(col);
                } else {
                    console.log('column full')
                }
            }
        }
    } else {
        console.log('GAMEOVER!!!')
    }
}

function showMove(col) {
    if (GRID[0][col] == 0) {
        row = 0;
        while ((row < 6) && (GRID[row][col] == 0)) {
            row++;
        }
        row--;
        // changeCell(row, col, MARK, 0);
        changeCell(row, col, MARK+9, 0);
        GRID[row][col] = MARK;
    } else {
        console.log('column full')
    }
}

function play_human(col) {
    fetch('/connect4/play', {
        method: 'POST',
        body: JSON.stringify({
            column: col,
            game_id: GAME_ID,
            })
        })
    .then((response) => response.json())
    .then(result => {
        update(result);
    })
    .then(error => {
        console.log(error);
    });
}

function update(result) {
    console.log('UPDATE result:', result);

    document.getElementById('response').innerHTML = result;

    scores = result['scores'];
    for (let i = 0; i < 7; i++) {
        el_score = document.getElementById(`score${i}`);
        el_score.innerHTML = scores[i];
    }

    GAMEOVER = result['gameover']
    console.log('GAMEOVER:', GAMEOVER);

    signal = result['signal'];
    if (signal != null) {
        for (let r = 0; r < 6; r++) {
            for (let c = 0; c < 7; c++) {
                v = signal[r][c];
                if (v > 0) {
                    changeCell(r, c, v+2);
                }
            }
        }
    }


    if (!GAMEOVER) {
        MARK = 3 - MARK;
        STEP++;

        el_move_made.innerHTML = result['move'];
        el_moved_name.style.visibility = 'visible';
        el_move_made.style.visibility = 'visible';
        el_moved_circle.style.visibility = 'visible';

        if (BOTH_ARE_BOTS){
            el_moved_circle.innerHTML = circles[3-MARK];
            el_moved_name.innerHTML = NAMES[3-MARK] + ' ';
        } else {
            if (MARK == HUMAN_NUM) {
                THINKING = false;
                el_show_your_turn.style.visibility = 'visible';
                el_moved_circle.innerHTML = circles[3-HUMAN_NUM];
            } else {
                THINKING = true;
                el_show_your_turn.style.visibility = 'hidden';
                el_move_made.innerHTML = "";
                el_moved_circle.innerHTML = dot_circles[3-HUMAN_NUM];
            }
        }
        if (IS_BOT[MARK]) {
            // el_moved_name.innerHTML = NAMES[MARK];
            play_bot();
        }

    } else {
        el_show_your_turn.style.display = 'none';

        el_moved_circle.innerHTML = circles[MARK];
        el_moved_name.innerHTML = NAMES[MARK] + ' ';
        el_move_made.innerHTML = result['move'];
        el_replay.style.visibility = 'visible';
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
            url = `/connect4/play_bot_championship`;
            console.log('Championship new game ');
            document.location.href = url;
        }
    }
}

function opponentMove(data) {
    col = data['move'];
    game_id = data['game_id']
    console.log('opponent move hn mark', col, HUMAN_NUM, MARK, data)
    if ((HUMAN_NUM != MARK) && (game_id == GAME_ID) && !GAMEOVER) {
        if (!IS_BOT[data['mark']]) {
            showMove(col);
            update(data);
        }
    }
}

function play_bot() {
    console.log('play_bot', PAUSE);
    if (PAUSE == true) {
        alert('-- pause --');
    }
    if (GAMEOVER != true) {
        THINKING = true;
        fetch('/connect4/play', {
            method: 'PUT',
            body: JSON.stringify({
                game_id: GAME_ID,
                })
            })
        .then((response) => response.json())
        .then(data => {
            col = data['move'];
            showMove(col);
            update(data);
        });

    }
}

document.addEventListener('DOMContentLoaded', function() {

    var pusher = new Pusher('bbe70803665a7a964619', {
      cluster: 'eu'
    });
    var channel = pusher.subscribe('my-channel');
    channel.bind('connect4_move', opponentMove);

	document.querySelectorAll('.cell').forEach(el => el.addEventListener('click', move));

    console.log('GAME FOUR IN A ROW');
    settings();
    console.log(MARK, IS_BOT)
    if (IS_BOT[MARK]) {
        console.log('call play bot')
        play_bot();
    }
});


