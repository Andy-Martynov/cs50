var GAME_ID
var UID

// var el_game_message

// function gameCancel(data){
//     game_id = data['game_id']
//     oid = data['oid']
//     if (game_id == GAME_ID && oid == UID) {
//         console.log('gameCancel', GAME_ID, UID, data);
//         document.location.href = 'cancel';
//     }
// }

// function gameCanceled(data){
//     game_id = data['game_id']
//     if (game_id == GAME_ID) {
//         console.log('gameCanceled', GAME_ID, data);
//         // document.location.href = 'cancel';
//     }
// }

// function sendOthelloMessage() {
//     message = document.getElementById("message_input").value;
//     console.log('sendMessage', message);
//     fetch('/game/send_message', {
//         method: 'POST',
//         body: JSON.stringify({
//             message: message,
//             game_id: GAME_ID,
//             })
//         })
//     .then((response) => response.json())
//     .then(data => {
//         console.log(data);
//     });
//     document.getElementById("message_input").value = '';
// }


// function getMessage(data){
//     const
//     console.log('getMessage', uid, data)
//     opponent_id = data['opponent_id']
//     game_id = data['game_id']
//     if (opponent_id == uid && game_id == GAME_ID) {
//         el_message.innerHTML = data['message']
//     }
// }

// function getGameCanceled(data) {
//     console.log('pusher game canceled', data);
//     if (data != null) {
//         id = data['game_id'];
//         invite_game_id = document.getElementById("invite_game_id").innerHTML;
//         if (id == invite_game_id) {
//             kind = data['kind'];
//             // location = `/game/new_game/${kind}`;
//             fetch(`/game/new_game/${kind}`, {
//                 method: 'GET',
//                 })
//         }
//     }
// }

// document.addEventListener('DOMContentLoaded', function() {

//     var pusher = new Pusher('bbe70803665a7a964619', {
//       cluster: 'eu'
//     });
//     var channel = pusher.subscribe('my-channel');
//     channel.bind('game_canceled', getGameCanceled);

//     el_game_message = document.getElementById("game_message")
//     if (el_game_message != null) {
//         // channel.bind('game_message', getMessage);
//         // console.log('Ready to get game messages');
// });


