from django.urls import path

from . import views

app_name = 'othello'
urlpatterns = [

    path("index", views.index, name="index"),
    path("game_go/<int:id>", views.game_go, name="game_go"),

    path("play", views.play, name="play"),
    path("game_replay/<int:id>", views.game_replay, name="game_replay"),
    path("make_move", views.make_move, name="make_move"),

    # path("about", views.about, name="about"),
]