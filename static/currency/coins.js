var TICKERS
var PLOTS
var COINS
var PRICES = []

function updateTickers____() {
    // console.log('updateTickers', TICKERS);
    i = 0;
    TICKERS.forEach((ticker) => {
       symbol = ticker.getAttribute('sym');
       value = ticker.innerHTML;
    //   console.log(symbol, value);
        result = fetch('/currency/api_binance_symbol_ticker_price', {
            method: 'POST',
            body: JSON.stringify({
                symbol: symbol,
                })
            })
        .then((response) => response.json())
        .then(result => {
            // console.log(result);
            new_value = result['data']['price'];
            if (new_value != value) {
                ticker.innerHTML = new_value;
                if (new_value > value) {
                    ticker.style.color = 'green';
                } else {
                    ticker.style.color = 'red';
                }
            }

            PRICES[i].push(new_value);
            id = PLOTS[i].id;
            Plotly.newPlot(`${id}`, /* JSON object */ {
                "data": [{ "y": PRICES[i] }],
                "layout": { "width": '80%', "height": '40vh'}
            });
            console.log(i, ticker, PRICES[i])
            i++;
        })
    });
}

async function updateTickers() {
    // console.log('updateTickers', TICKERS);
    i = 0;
    for (i=0; i < TICKERS.length; i++) {
        symbol = TICKERS[i].getAttribute('sym');
        coin = TICKERS[i].getAttribute('coin');
        value = TICKERS[i].innerHTML;
        // console.log(symbol, value);
        result = await fetch('/currency/api_binance_symbol_ticker_price', {
            method: 'POST',
            body: JSON.stringify({
                symbol: symbol,
                })
            })
        .then((response) => response.json())
        // .then(result => {
            // console.log('result', result, result.data);
            new_value = result.data['price'];
            if (new_value != value) {
                TICKERS[i].innerHTML = new_value;
                if (new_value > value) {
                    TICKERS[i].style.color = 'green';
                } else {
                    TICKERS[i].style.color = 'red';
                }
            }

            PRICES[i].push(new_value);
            id = PLOTS[i].id;
            Plotly.newPlot(`${id}`, /* JSON object */ {
                "data": [{ "y": PRICES[i] }],
                "layout": {title:coin} // , "width": '80%', "height": '40vh'}
            });
            // console.log(i, TICKERS[i], PRICES[i])
        // })
    }
}


document.addEventListener('DOMContentLoaded', function() {
	console.log('COINS LOADED');
	TICKERS = document.querySelectorAll('.ticker');

	setInterval(() => updateTickers(), 10000);

	PLOTS = document.querySelectorAll('.tickerplot');
	avgs = document.querySelectorAll('.avg-price');
	boxes = document.querySelectorAll('.tickerplotbox');
	console.log(PLOTS);
    for (i=0;  i < PLOTS.length; i++) {
        if (boxes.length < 4) {
            let n = 12 / boxes.length;
            let m = n;
            if (n == 4) {
                let m = 6;
            }
            boxes[i].className = `w3-border p-1 tickerplotbox col-12 col-md-${m} col-lg-${n}`
        }
        coin = TICKERS[i].getAttribute('coin');
        id = PLOTS[i].id;
        avg = avgs[i].innerHTML;
        list = [avg];
        PRICES.push(list);
        Plotly.newPlot(`${id}`, /* JSON object */ {
            "data": [{ "y": PRICES[i] }],
            "layout": {title:coin} // "width": '80%', "height": '40vh'}
        })
    }
});
