from django.urls import path

from . import views

app_name = 'game'
urlpatterns = [
    path("new_game", views.index, name="new_game"),
    path("new_game/<int:id>", views.index, name="new_game"),
    path("index", views.index, name="index"),
    path("index/<int:id>", views.index, name="index"),

    path("invite/<int:id>", views.invite, name="invite"),
    path("cancel_invite/<int:id>", views.cancel_invite, name="cancel_invite"),
    path("confirm", views.confirm, name="confirm"),

    path("game_cancel/<int:id>", views.game_cancel, name="game_cancel"),
    path("game_cancel/<int:id>/<str:trigger>", views.game_cancel, name="game_cancel"),
    path("game_go/<int:kind_id>/<int:id>", views.game_go, name="game_go"),
    path("game_replay/<int:kind_id>/<int:id>", views.game_replay, name="game_replay"),

    # path("game_go/<int:id>", views.game_go, name="game_go"),
    # path("game_go", views.game_go, name="game_go"),

    # path("cancel", views.game_cancel, name="cancel"),
    # path("game_go/cancel", views.game_cancel, name="cancel"),
    # path("play_bot_championship/cancel", views.game_cancel, name="game_end"),

    # path("new_bot_championship", views.new_bot_championship, name="new_bot_championship"),
    # path("start_bot_championship", views.start_bot_championship, name="start_bot_championship"),
    # path("play_bot_championship", views.play_bot_championship, name="play_bot_championship"),

    path("leaderboard", views.leaderboard, name="leaderboard"),
    path("reset_all_scores", views.reset_all_scores, name="reset_all_scores"),
    path("reset_bot_scores", views.reset_bot_scores, name="reset_bot_scores"),

    path("kinds_info", views.kinds_info, name="kinds_info"),
    path("game_list", views.game_list, name="game_list"),
    path("game_list_all", views.game_list_all, name="game_list_all"),
    path("delete_unfinished_games", views.delete_unfinished_games, name="delete_unfinished_games"),
    path("delete_game", views.delete_game, name="delete_game"),

    path("player_info/<int:id>", views.player_info, name="player_info"),
    path("player_info/<int:id>/<int:oid>", views.player_info, name="player_info"),

    path("about", views.about, name="about"),
]