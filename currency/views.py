from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import datetime
import requests
from lxml import etree
import json

import os
from mysite import settings

import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

#______________________________________________________ ABOUT __________________
from common.instruments import show_md

def about(request):
    entry_rus = os.path.join(settings.MEDIA_ROOT, 'currency', 'md', 'about_rus.md')
    entry_eng = os.path.join(settings.MEDIA_ROOT, 'currency', 'md', 'about_eng.md')
    return show_md(request, entry_rus=entry_rus, entry_eng=entry_eng, layout='currency/layout.html')


#____________________________________________________________ CBRF _____________
def get_cbrf_valuta():
    x = requests.get('https://www.cbr.ru/scripts/XML_valFull.asp')
    # remove XML prolog, i.e. something like <?xml version="1.0" encoding="UTF-8"?>
    text = x.text
    n = text.find('>') + 1
    text = text[n:]
    tree = etree.fromstring(text)
    curr = {}
    for item in tree :
        val = {}
        val['code'] = item.attrib['ID']
        for e in item:
            if e.tag == 'ISO_Char_Code':
                iso = e.text
            if e.tag == 'ISO_Num_Code':
                val['isonum'] = e.text
            if e.tag == 'ISO_Char_Code':
                val['iso'] = e.text
            if e.tag == 'Name':
                val['name'] = e.text
            if e.tag == 'EngName':
                val['eng'] = e.text
            if e.tag == 'Nominal':
                val['nominal'] = e.text
        curr[iso] = val
    return curr

def cbrfc(dt, v='R01235') :

    # dt - дата запроса курса в формат datetime
    # v - код валюты (http://www.cbr.ru/scripts/XML_daily.asp?date_req=13/04/2020)
    #       USD = R01235
    #       EUR = R01239
    #       CNY = R01375

    q = dt.strftime("%d/%m/%Y")
    x = requests.get('http://www.cbr.ru/scripts/XML_daily.asp?date_req='+q)

    yt = dt - datetime.timedelta(days = 1)
    yq = yt.strftime("%d/%m/%Y")
    y = requests.get('http://www.cbr.ru/scripts/XML_daily.asp?date_req='+yq)

    # remove XML prolog, i.e. something like <?xml version="1.0" encoding="UTF-8"?>
    text = x.text
    n = text.find('>') + 1
    text = text[n:]

    try :
        tree = etree.fromstring(text)
    except :
        return None

    d = tree.attrib['Date']

    val, code = None, None

    for e in tree :
        aid = e.attrib['ID']
        if aid==v :
            for e1 in e :
                if e1.tag=='Value' :
                    val = float(e1.text.replace(',', '.'))
                if e1.tag=='CharCode' :
                    code = e1.text
    answer = {'value':'-', 'code':'-', 'd':'-', 'change':'-'}

    if val:
        answer["value"] = val
    if code:
        answer["code"] = code
    answer["date"] = d

    text = y.text
    n = text.find('>') + 1
    text = text[n:]

    tree = etree.fromstring(text)
    d = tree.attrib['Date']

    val, code = None, None

    for e in tree :
        aid = e.attrib['ID']
        if aid==v :
            for e1 in e :
                if e1.tag=='Value' :
                    val = float(e1.text.replace(',', '.'))
                if e1.tag=='CharCode' :
                    code = e1.text
    if val:
        delta = round(answer['value']-val, 4)
        if delta>0 :
            change = '<span style="color: green">+'+str(delta)+'</span>'
        else :
            change = '<span style="color: red">'+str(delta)+'</span>'
        answer["change"] = change
        answer["delta"] = delta
    return answer

def get_all_tod_tom() :
    tod = datetime.datetime.now()
    tom = tod + datetime.timedelta(days = 1)

    if not cbrfc(tod) :
        return None

    curr = dict()

    usdtod = cbrfc(tod)
    eurtod = cbrfc(tod, v='R01239')

    utd = usdtod['value']
    etd = eurtod['value']

    utdc = usdtod['change']
    etdc = eurtod['change']
    eur_usd_tod = round(etd / utd, 4)

    curr['usd_tod'] = utd
    curr['eur_tod'] = etd
    curr['eur_usd_tod'] = eur_usd_tod
    curr['usd_todc'] = utdc
    curr['eur_todc'] = etdc

    usdtom = cbrfc(tom)
    if usdtom:
        utm = usdtom['value']
        utmc = usdtom['change']
        curr['usd_tom'] = utm
        curr['usd_tomc'] = utmc

    eurtom = cbrfc(tom, v='R01239')
    if eurtom:
        etm = eurtom['value']
        etmc = eurtom['change']
        curr['eur_tom'] = etm
        curr['eur_tomc'] = etmc

    if  eurtom and usdtom:
        eur_usd_tom = round(etm / utm, 4)
        curr['eur_usd_tom'] = eur_usd_tom
        delta_usd = cbrfc(tod)['delta']
        delta_eur = cbrfc(tod, v='R01239')['delta']
        uys = round(utd - delta_usd, 4)
        eys = round(etd - delta_eur, 4)
        eur_usd_ystd = round(eys / uys, 4)
        eur_usd_todc = round(eur_usd_tod - eur_usd_ystd, 4)
        if eur_usd_todc > 0:
            curr['eur_usd_todc'] = f'<span style="color: green">{eur_usd_todc}</span>'
        else:
            curr['eur_usd_todc'] = f'<span style="color: red">{eur_usd_todc}</span>'
        eur_usd_tomc = round(eur_usd_tom - eur_usd_tod, 4)
        if eur_usd_tomc > 0:
            curr['eur_usd_tomc'] = f'<span style="color: green">{eur_usd_tomc}</span>'
        else:
            curr['eur_usd_tomc'] = f'<span style="color: red">{eur_usd_tomc}</span>'
    return curr

def get_cbrf_todtom(v) :
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days = 1)
    curr = dict()
    tod = cbrfc(today, v)
    tom = cbrfc(tomorrow, v)
    curr['tod'] = tod['value']
    curr['tom'] = tom['value']
    curr['change_tod'] = tod['change']
    curr['change_tom'] = tom['change']
    return curr
#______________________________________________________ INDEX __________________
def index(request):
    if request.method == 'POST':
        data = request.POST
        if 'currency_list' in data:
            currency_list = data.getlist('currency_list')
            if len(currency_list) > 0:
                request.session['currencies_selected'] = currency_list
            else:
                messages.info(request, 'Select at least one currency', extra_tags='alert-danger')
                return redirect(reverse("currency:index"))
        else:
            messages.info(request, 'Select at least one currency', extra_tags='alert-danger')
            return redirect(reverse("currency:index"))

    context = {}

    if 'currencies_selected' in request.session:
        currencies_selected = request.session['currencies_selected']
    else:
        currencies_selected = ['USD', 'EUR', 'CNY']
        request.session['currencies_selected'] = currencies_selected
    context['currencies_selected'] = currencies_selected

    valuta = get_cbrf_valuta()
    context['currency_list'] = [valuta[c] for c in valuta]

    currencies = []
    for c in currencies_selected:
        data = get_cbrf_todtom(valuta[c]['code'])
        data['iso'] = c
        data['name'] = valuta[c]['name']
        data['nominal'] = valuta[c]['nominal']
        currencies.append(data)
    context['currencies'] = currencies
    return render(request, 'currency/index.html', context)

#______________________________________________________ BINANCE ________________

BINANCE = 'https://api.binance.com'

def binance_get(url):
    response= requests.get(BINANCE + url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    return None

def binance_symbols(request):
    data = binance_get('/api/v1/exchangeInfo')
    symbols = data['symbols']
    return symbols

def binance_symbol_list(symbols):
    symbol_list = [{'symbol':s['symbol'], 'baseAsset':s['baseAsset'], 'quoteAsset':s['quoteAsset']} for s in symbols if s['symbol'].count('USDT') > 0]
    return symbol_list

def binance_symbol_coins(symbols):
    symbol_list = {s['symbol']:s['baseAsset'] for s in symbols if s['symbol'].count('USDT') > 0}
    return symbol_list

def binance_symbol_avg_price(symbol):
    return binance_get(f'/api/v3/avgPrice?symbol={symbol}')

@csrf_exempt
def api_binance_symbol_avg_price(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("symbol") is not None:
            symbol = data["symbol"]
            data = binance_get(f'/api/v3/avgPrice?symbol={symbol}')
            return JsonResponse({'data':data, 'status':200})
        return JsonResponse({'error':'No symbol', 'status':400})
    return JsonResponse({'error':'Bad method', 'status':400})


def binance_symbol_ticker_price(symbol):
    return binance_get(f'/api/v3/ticker/price?symbol={symbol}')

@csrf_exempt
def api_binance_symbol_ticker_price(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("symbol") is not None:
            symbol = data["symbol"]
            data = binance_get(f'/api/v3/ticker/price?symbol={symbol}')
            return JsonResponse({'data':data, 'status':200})
        return JsonResponse({'error':'No symbol', 'status':400})
    return JsonResponse({'error':'Bad method', 'status':400})
#______________________________________________________ COINS __________________
def coins(request):
    if request.method == 'POST':
        data = request.POST
        if 'symbol_list' in data:
            symbol_list = data.getlist('symbol_list')
            if len(symbol_list) > 0:
                request.session['symbols_selected'] = symbol_list
            else:
                messages.info(request, 'Select at least one symbol', extra_tags='alert-danger')
                return redirect(reverse("currency:coins"))
        else:
            messages.info(request, 'Select at least one symbol', extra_tags='alert-danger')
            return redirect(reverse("currency:coins"))

    context = {}

    if 'symbols_selected' in request.session:
        symbols_selected = request.session['symbols_selected']
    else:
        symbols_selected = ['BTCUSDT', 'ETHUSDT']
        request.session['symbols_selected'] = symbols_selected
    context['symbols_selected'] = symbols_selected

    symbols = binance_symbols(request)
    symbol_list = binance_symbol_list(symbols)
    coins = binance_symbol_coins(symbols)
    context['symbol_list'] = symbol_list
    context['selected'] = symbols_selected

    symbols_info = []
    for symbol in symbols_selected:
        info = {'symbol':symbol, 'coin':coins[symbol]}
        info['avgPrice'] = binance_symbol_avg_price(symbol)
        info['ticker'] = binance_symbol_ticker_price(symbol)
        symbols_info.append(info)
    context['symbols_info'] = symbols_info
    return render(request, 'currency/coins.html', context)

#_______________________________________________________ DYNAMIC _______________
def dynamic(request):
    context = {}
    today = datetime.datetime.now()

    if request.method == 'POST':
        data = request.POST
        if 'currency_list' in data:
            currency_list = data.getlist('currency_list')
            if 'start' in data:
                if data['start'] != '':
                    start = datetime.datetime.strptime(data['start'], '%Y-%m-%d')
                    valuta = get_cbrf_valuta()
                    data = []
                    date = start
                    while date <= today:
                        for curr in currency_list:
                            item = {}
                            item['date'] = date
                            item['name'] = curr
                            item['value'] = cbrfc(date, valuta[curr]['code'])['value']
                            data.append(item)
                        date += datetime.timedelta(days = 1)

                    df = pd.DataFrame(data)

                    title = ''
                    for curr in currency_list:
                        title += curr
                        nominal = valuta[curr]['nominal']
                        if nominal != '1':
                            title += f'*{nominal}'
                        title += ' '

                    fig = px.line(df, x="date", y="value", color='name', labels={'date':'Date', 'value':'Value', 'name':''}, title=title)
                    fig.update_traces(mode='lines+markers') # , hover_name="date", hover_data=["date", "value", "name"])markers=True,
                    fn = os.path.join(settings.MEDIA_ROOT, 'currency', 'plots', 'dynamic.html')
                    fig.write_html(fn)
                    context['dynamic_plot'] = os.path.join(settings.MEDIA_URL, 'currency', 'plots', 'dynamic.html')
                    return render(request, 'currency/dynamic.html', context)
                messages.info(request, 'No start date', extra_tags='alert-danger')
                return redirect(reverse("currency:index"))
            messages.info(request, 'No start date', extra_tags='alert-danger')
            return redirect(reverse("currency:index"))
        messages.info(request, 'Select at least one currency', extra_tags='alert-danger')
        return redirect(reverse("currency:index"))
    messages.info(request, 'Bad request', extra_tags='alert-danger')
    return redirect(reverse("currency:index"))

















