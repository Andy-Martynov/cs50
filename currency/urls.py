from django.urls import path

from . import views

app_name = 'currency'
urlpatterns = [
    path("index", views.index, name="index"),
    path("coins", views.coins, name="coins"),
    path("about", views.about, name="about"),
    path("dynamic", views.dynamic, name="dynamic"),

    path("api_binance_symbol_ticker_price", views.api_binance_symbol_ticker_price, name="api_binance_symbol_ticker_price"),
    path("api_binance_symbol_avg_price", views.api_binance_symbol_avg_price, name="api_binance_symbol_avg_price"),
]

