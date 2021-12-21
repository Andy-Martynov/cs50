function trigger(event) {
    console.log('trigger', event);
    fetch('/rtc/test', {
        method: 'POST',
        body: JSON.stringify({
            event: event,
            })
        })
    .then((response) => response.json())
    .then(error => {
        console.log(error);
    });
}

function event(data) {
    console.log('got event', data);
}

// ['test', 'four_game_canceled', 'four_game_started', 'four_game_started']

document.addEventListener('DOMContentLoaded', function() {

    var pusher = new Pusher('bbe70803665a7a964619', {
      cluster: 'eu'
    });
    var channel = pusher.subscribe('my-channel');
    channel.bind('test', event);
    channel.bind('four_game_canceled', event);
    channel.bind('four_game_started', event);
    channel.bind('four_game_started', event);
});