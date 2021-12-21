from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from hub.views import pusher_client
from mysite import settings
import os

from .models import Player, Game, GameKind

import numpy as np
import pandas as pd

import plotly.express as px

import random
import time

# ------------------------------------------------------- main -----------------

def game_init(request):
    '''
    call when user open the site
    '''
    user = request.user
    if user.is_authenticated:
        player = Player.objects.filter(user=user).first()
        if not player:
            player = Player.objects.create(user=user)
        user.player.save()

# _________________________________________________________ NEW GAME ___________
def new_game(request, kind_id):
    '''
    Selects two players, hints mode and starts a game
    '''
    context = {}
    context['kind'] = kind

    game_kind = GameKind.objects.filter(id=kind_id).first()
    if not game_kind:
        context['error'] = f'NO GAME {kind_id}'
        return render(request, "game/new_game.html", context)
    kind = game_kind.name

    # session keys
    kind_busy = f'{kind}_busy'
    kind_game_id = f'{kind}_game_id'
    kind_username = f'{kind}_username'
    kind_first_player_name = f'{kind}_first_player_name'
    kind_second_player_name = f'{kind}_second_player_name'
    kind_hints = f'{kind}_hints'

    if request.method == 'POST' : # options changed
        data = request.POST
        if 'first_player_name' in data :
            first_player_name = data['first_player_name']
        if 'second_player_name' in data :
            second_player_name = data['second_player_name']
        request.session[kind_hints] = False
        hints = False
        if 'hints' in data :
            if data['hints'] == 'on':
                hints = True
        return start_game(request, kind_id, first_player_name, second_player_name, hints)

    # create new game form

    if kind_busy in request.session:
        if request.session[kind_busy] == 'busy':
            if kind_game_id in request.session:
                game = Game.objects.filter(id=request.session[kind_game_id]).first()
                if game:
                    context['game_running'] = game
        if kind_busy in request.session:
            context['busy'] = request.session[kind_busy]

    players = {}

    context['bot_players'] = Player.objects.filter(is_bot=True, user__is_active=True)

    if request.user.is_authenticated:
        username = request.user.username
        context['human_players'] = Player.objects.filter(is_bot=False, user__is_active=True).exclude(user__username=username)
    else:
        username = 'Guest'
    request.session[kind_username] = username
    players[username] = None

    user_player = Player.objects.filter(user__username=username).first()
    if user_player:
        context['user_player'] = user_player

    bot_players = Player.objects.filter(is_bot=True, user__is_active=True)

    context['bot_players'] = bot_players
    if kind_first_player_name in request.session:
        context['first_player_name'] = request.session[kind_first_player_name]
    else:
        context['first_player_name'] = username

    if kind_second_player_name in request.session:
        context['second_player_name'] = request.session[kind_second_player_name]
    else:
        context['second_player_name'] = bot_players.first().user.username

    return render(request, "game/new_game.html", context)

# _______________________________________________________ START GAME ___________
def start_game(request, kind_id, first_player_name, second_player_name, hints):
    '''
    Creates the game
    '''
    # session keys
    kind_first_player_name = f'{kind}_first_player_name'
    kind_second_player_name = f'{kind}_second_player_name'

    request.session[kind_first_player_name] = first_player_name
    request.session[kind_second_player_name] = second_player_name

    first_player = Player.objects.filter(user__username=first_player_name).first()
    second_player = Player.objects.filter(user__username=second_player_name).first()

    if not first_player:
        messages.info(request, f'player "{first_player_name}" not found', extra_tags='alert-danger')
        return redirect(reverse("game:new_game", args=[kind]))
    if not second_player:
        messages.info(request, f'player "{second_player_name}" not found', extra_tags='alert-danger')
        return redirect(reverse("game:new_game", args=[kind]))

    # Create a game
    game_kind = GameKind.objects.filter(id=kind_id).first()
    game = Game.objects.create(kind=game_kind, first=first_player, second=second_player, hints=hints)
    if not game:
        return redirect(reverse("game:new_game", args=[kind]))

    username = request.user.username
    if not (first_player.is_bot or second_player.is_bot): # both are human
        if not (first_player.user.username == username and second_player.user.username == username): # not play with myself
            return redirect(reverse('game:invite', args=[game.id]))
    return redirect(reverse(f"{game.kind}:game_go", args=[game.id]))

# __________________________________________________________ INVITE ____________
@csrf_exempt
def invite(request, id):
    '''
    Invites human opponent to play if he is online
    '''

    game = Game.objects.filter(id=id).first()
    kind = game.kind
    player = Player.objects.filter(user=request.user).first()
    if player == game.first:
        opponent = game.second
    else:
        opponent = game.first

    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("game_id") is not None:
            game_id = int(data["game_id"])
            if game_id == game.id:
                if data.get("opp_id") is not None:
                    opp_id = int(data["opp_id"])
                    if opp_id == opponent.user.id:
                        if data.get("confirm") is not None:
                            confirm = data["confirm"]

                            if confirm == 'OK' :
                                return redirect(reverse(f"{kind}:game_go", args={'id': game.id}))
                            return redirect(reverse("game:new_game", args=[kind]))

                        return JsonResponse({'message':'No confirm', 'status':400})
                    return JsonResponse({'message':'Bad opponent ID', 'status':400})
                return JsonResponse({'message':'No opponent ID', 'status':400})
            return JsonResponse({'message':'Bad game ID', 'status':400})
        return JsonResponse({'message':'No game ID', 'status':400})

    data = {}
    data['kind'] = kind
    data['inviter_id'] = request.user.id
    data['inviter_name'] = request.user.player.name()
    data['opponent_id'] = opponent.user.id
    data['game_id'] = game.id
    pusher_client.trigger('my-channel', 'game_invite', data)

    context = {}
    context['opponent'] = opponent
    context['game'] = game
    context['game_id'] = game.id
    context['kind'] = game.kind
    context['invite_send'] = True
    return render(request, "game/new_game.html", context)

# _______________________________________________________ CANCEL INVITE ________
@csrf_exempt
# @login_required
def cancel_invite(request, id):
    '''
    Cancel the invitation
    '''
    game = Game.objects.filter(id=id).first()
    kind = game.kind
    player = Player.objects.filter(user=request.user).first()
    if player == game.first:
        opponent = game.second
    else:
        opponent = game.first

    data = {}
    data['game_id'] = id
    data['opponent_id'] = opponent.id
    pusher_client.trigger('my-channel', 'game_invite_canceled', data)
    return redirect(reverse("game:new_game", args=[kind]))

# _____________________________________________________________ CONFIRM ________
@csrf_exempt
# @login_required
def confirm(request):
    '''
    Confirm the invitation
    '''
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("game_id") is not None:
            game_id = int(data["game_id"])
            if data.get("confirm") is not None:
                confirm = data["confirm"]
                response = {}
                response['game_id'] = game_id
                game = Game.objects.filter(id=game_id).first()
                kind = game.kind
                response['kind'] = kind
                if confirm == 'OK':
                    pusher_client.trigger('my-channel', 'game_invite_confirmed', response)
                else:
                    pusher_client.trigger('my-channel', 'game_invite_rejected', response)
                return JsonResponse({'message':confirm, 'status':200})
            return JsonResponse({'message':'No confirm', 'status':400})
        return JsonResponse({'message':'No game ID', 'status':400})
    return JsonResponse({'message':'Bad method', 'status':400})

# _______________________________________________________ GAME CANCEL ________
@csrf_exempt
# @login_required
def game_cancel(request, id, trigger='yes'):
    '''
    Cancel the game in progress
    '''
    game = Game.objects.filter(id=id).first()
    game.is_running = False
    game.save()

    if trigger == 'yes':
        data = {}
        data['game_id'] = game.id
        data['kind'] = game.kind
        data['message'] = 'game canceled'
        pusher_client.trigger('my-channel', 'game_canceled', data)

    key = f'game_{game.id}'
    kind_game_busy = f'{game.kind}_busy'
    kind_game_id = f'{game.kind}_game_id'

    if key in request.session:
        del request.session[key]
    if kind_game_id in request.session:
        del request.session[kind_game_id]
    if kind_game_busy in request.session:
        request.session[f'{game.kind}_busy'] = 'free'
        del request.session[f'{game.kind}_busy']
    request.session.modified = True
    return redirect(reverse("game:new_game", args=[game.kind]))


#_________________________________________________________ GAME GO _____________

def game_go(request, kind, id):
    return redirect(reverse(f"{kind}:game_go", args=[id]))

# ------------------------------------------------------------------------------

def new_bot_championship(request):
    '''
    Creates new bot championship
    '''
    if request.method == 'POST' : # options changed
        data = request.POST
        if 'max_games' in data :
            request.session['max_games'] = int(data['max_games'])
        if 'challenger' in data :
            request.session['challenger'] = data['challenger']
        request.session['hints'] = False
        if 'hints' in data :
            if data['hints'] == 'on':
                request.session['hints'] = True
        return redirect(reverse(":start_bot_championship"))
    context = {}
    # create agents list
    agents = Player.objects.filter(is_bot=True, user__is_active=True)
    context['agents'] = agents
    hints = request.session['hints']
    if hints:
        context['hints'] = 'checked="checked"'
    return render(request, "/new_bot_championship.html", context)


def start_bot_championship(request):
    '''
    Starts the championship
    '''
    request.session['current_game'] = 1
    request.session['championat_game_id'] = None
    return redirect(reverse(":play_bot_championship"))


def play_bot_championship(request):
    '''
    Runs the championship
    '''
    if not request.session['championat_game_id']:
        if request.session['current_game'] > request.session['max_games']:
            messages.info(request, f"championat is over, {request.session['max_games']} games played", extra_tags='alert-danger')
            return redirect(reverse(":new_game"))

        challenger_name = request.session['challenger']
        have_challenger = True
        if challenger_name == 'None':
            have_challenger = False

        agents = Player.objects.filter(is_bot=True, user__is_active=True)
        agent_list = list(agents)
        agent_numbers = [i for i in range(len(agent_list))]

        while True:
            first_player_num = random.choice(agent_numbers)
            second_player_num = random.choice(agent_numbers)
            if first_player_num != second_player_num:
                if not have_challenger:
                    break
                if agent_list[first_player_num].user.username == challenger_name:
                    break
                if agent_list[second_player_num].user.username == challenger_name:
                    break

        first_player = agent_list[first_player_num]
        second_player = agent_list[second_player_num]

        game = Game.objects.create(first=first_player, second=second_player, hints=request.session['hints'])
        if not game:
            messages.info(request, 'error creating game', extra_tags='alert-danger')
            return redirect(reverse(":new_game"))
        request.session['game_id'] = game.id
        request.session['championat_game_id'] = game.id

        context = {}
        context['game'] = game
        context['championship'] = True
        context['max_games'] = request.session['max_games']
        context['current_game'] = request.session['current_game']
        matrix = [[0 for c in range(C)] for r in range(R)]
        context['matrix'] = matrix
        return render(request, "/game.html", context)
    return redirect(reverse(":new_game"))

############################################################### LEADERBOARD ####

def leaderboard(request):
    '''
    The leaderboard
    '''
    context = {}

    # not_finished = Game.objects.filter(is_finished=False)
    # not_finished.delete()

    total_games = Game.objects.all().exclude(is_finished=False).count()

    players = Player.objects.all().order_by('-rating')
    for player in players:
        games = Game.objects.filter(first=player) | Game.objects.filter(second=player)
        games = games.exclude(first=player, second=player).exclude(is_finished=False)
        g = games.count()
        player.games = g
        win = games.filter(winner=player).count()
        player.win = win
        loss = games.filter(loser=player).count()
        player.loss = loss
        player.tie = g - win - loss
        player.save()


    results = []
    for player1 in players:
        row = [player1]
        g1, w1, l1, t1 = 0, 0, 0, 0
        for player2 in players:
            games = Game.objects.filter(first=player1, second=player2) | Game.objects.filter(second=player1, first=player2)
            games = games.exclude(first=player1, second=player1).exclude(first=player2, second=player2).exclude(is_finished=False)
            g = games.count()
            win = games.filter(winner=player1, loser=player2).count()
            loss = games.filter(winner=player2, loser=player1).count()
            tie = g - win - loss
            row.append((win, loss, tie, g))
            g1 += g
            w1 += win
            l1 += loss
            t1 += tie
        row.append((w1, l1, t1, g1))
        results.append(row)

    humans = Player.objects.filter(is_bot=False)
    human_games = Game.objects.filter(first__in=humans, second__in=humans) | Game.objects.filter(second__in=humans, first__in=humans)
    total_human_games = human_games.count()

    for human in humans:
        games = Game.objects.filter(first=human, second__in=humans) | Game.objects.filter(second=human, first__in=humans)
        games = games.exclude(first=human, second=human).exclude(is_finished=False)
        g = games.count()
        human.human_games = g
        win = games.filter(winner=human, loser__in=humans).count()
        human.human_win = win
        loss = games.filter(loser=human, winner__in=humans).count()
        human.human_loss = loss
        human.human_tie = g - win - loss
        human.save()

    humans = humans.order_by('-human_rating')
    human_matrix = []
    for human1 in humans:
        row = [human1]
        g1, w1, l1, t1 = 0, 0, 0, 0
        for human2 in humans:
            games = Game.objects.filter(first=human1, second=human2) | Game.objects.filter(second=human1, first=human2)
            games = games.exclude(first=human1, second=human1).exclude(first=human2, second=human2).exclude(is_finished=False)
            g = games.count()
            win = games.filter(winner=human1, loser=human2).count()
            loss = games.filter(winner=human2, loser=human1).count()
            tie = g - win - loss
            row.append((win, loss, tie, g))
            g1 += g
            w1 += win
            l1 += loss
            t1 += tie
        row.append((w1, l1, t1, g1))
        human_matrix.append(row)


    bots = Player.objects.filter(is_bot=True)
    bot_games = Game.objects.filter(first__in=bots, second__in=bots) | Game.objects.filter(second__in=bots, first__in=bots)
    total_bot_games = bot_games.exclude(is_finished=False).count()

    for bot in bots:
        games = Game.objects.filter(first=bot, second__in=bots) | Game.objects.filter(second=bot, first__in=bots)
        games = games.exclude(first=bot, second=bot).exclude(is_finished=False)
        g = games.count()
        bot.bot_games = g
        win = games.filter(winner=bot, loser__in=bots).count()
        bot.bot_win = win
        loss = games.filter(loser=bot, winner__in=bots).count()
        bot.bot_loss = loss
        bot.bot_tie = g - win - loss
        bot.save()

    bots = bots.order_by('-bot_rating')
    bot_matrix = []
    for bot1 in bots:
        row = [bot1]
        g1, w1, l1, t1 = 0, 0, 0, 0
        for bot2 in bots:
            games = Game.objects.filter(first=bot1, second=bot2) | Game.objects.filter(second=bot1, first=bot2)
            g = games.exclude(is_finished=False).count()
            win = Game.objects.filter(winner=bot1, loser=bot2).exclude(is_finished=False).count()
            loss = Game.objects.filter(winner=bot2, loser=bot1).exclude(is_finished=False).count()
            tie = g - win - loss
            row.append((win, loss, tie, g))
            g1 += g
            w1 += win
            l1 += loss
            t1 += tie
        row.append((w1, l1, t1, g1))
        bot_matrix.append(row)

    context['players'] = players
    context['bots'] = bots
    context['humans'] = humans

    context['bot_matrix'] = bot_matrix
    context['human_matrix'] = human_matrix
    context['results'] = results

    context['total_games'] = total_games
    context['total_bot_games'] = total_bot_games
    context['total_human_games'] = total_human_games
    return render(request, "/leaderboard.html", context)

def game_list(request):
    '''
    Game list paginated
    '''
    context = {}
    # not_finished = Game.objects.filter(is_finished=False)
    # not_finished.delete()
    games = Game.objects.all().exclude(is_finished=False).order_by('-id')

    paginator = Paginator(games, 25) # Show 25 games per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context['total'] = games.count()
    players = Player.objects.all()
    context['page_obj'] = page_obj
    context['players'] = players
    return render(request, "/game_list.html", context)

def game_list_all(request):
    '''
    Game list without pagination
    '''
    context = {}
    # not_finished = Game.objects.filter(is_finished=False)
    # not_finished.delete()
    games = Game.objects.all().exclude(is_finished=False).order_by('-id')
    context['total'] = games.count()
    players = Player.objects.all()
    context['games'] = games
    context['players'] = players
    return render(request, "/game_list_all.html", context)

def player_info(request, id, oid=None):
    '''
    id: player id
    oid: opponent id, shows all if None
    '''
    context = {}
    player = Player.objects.filter(id=id).first()
    if oid:
        opponent = Player.objects.filter(id=oid).first()
        games =  Game.objects.filter(first=player, second=opponent) | Game.objects.filter(first=opponent, second=player)
    else:
        games =  Game.objects.filter(first=player) | Game.objects.filter(second=player)
        games = games.exclude(first=player, second=player)

    games = games.exclude(is_finished=False).order_by('id')

    rating, bot_rating, human_rating = 600, 600, 600
    info, info_bot, info_human = [], [], []
    g_info, g_bot, g_human = 0, 0, 0

    for game in games:
        if player == game.first:
            rating += game.delta1
            g_info += 1
            result = 'tie'
            if game.winner == player: result = 'win'
            if game.loser  == player: result = 'loss'
            item = {'N': g_info, 'game': game.id, 'date': game.timestamp, 'delta': game.delta1, 'rating': rating, 'result': result, 'opponent': game.second.name(), 'oid': game.second.id}
            info.append(item)

            if game.second.is_bot:
                bot_rating += game.delta1
                g_bot += 1
                item_bot = {'N': g_bot, 'game': game.id, 'date': game.timestamp, 'delta': game.delta1, 'rating': bot_rating, 'result': result, 'opponent': game.second.name(), 'oid': game.second.id}
                info_bot.append(item_bot)
            else:
                human_rating += game.delta1
                g_human += 1
                item_human = {'N': g_human, 'game': game.id, 'date': game.timestamp, 'delta': game.delta1, 'rating': human_rating, 'result': result, 'opponent': game.second.name(), 'oid': game.second.id}
                info_human.append(item_human)

        if player == game.second:
            rating += game.delta2
            result = 'tie'
            g_info += 1
            if game.winner == player: result = 'win'
            if game.loser  == player: result = 'loss'
            item = {'N': g_info, 'game': game.id, 'date': game.timestamp, 'delta': game.delta2, 'rating': rating, 'result': result, 'opponent': game.first.name(), 'oid': game.first.id}
            info.append(item)
            if game.second.is_bot:
                bot_rating += game.delta2
                g_bot += 1
                item_bot = {'N': g_bot, 'game': game.id, 'date': game.timestamp, 'delta': game.delta2, 'rating': bot_rating, 'result': result, 'opponent': game.first.name(), 'oid': game.first.id}
                info_bot.append(item_bot)
            else:
                human_rating += game.delta2
                g_human += 1
                item_human = {'N': g_human, 'game': game.id, 'date': game.timestamp, 'delta': game.delta2, 'rating': human_rating, 'result': result, 'opponent': game.first.name(), 'oid': game.first.id}
                info_human.append(item_human)

    df = pd.DataFrame(info)

    if g_info > 0:
        # if oid:
        #     # title = f'{player.name()} vs {opponent.name()}, Rating progress'
        # else:
            # title = f'{player.name()}, Rating progress'
        fig = px.line(df, x="N", y="rating", hover_name="date", hover_data=["game", "opponent", "result", "delta"], labels={'rating':'', 'N':''})
        fn = os.path.join(settings.MEDIA_ROOT, '', 'plots', 'rating.html')
        fig.write_html(fn)
        context['rating_plot'] = os.path.join(settings.MEDIA_URL, '', 'plots', 'rating.html')

        if oid == None:
            if g_bot > 0:
                df_bot = pd.DataFrame(info_bot)
                # title = f'{player.name()}, Rating vs bots progress'
                fig_bot = px.line(df_bot, x="N", y="rating", hover_name="date", hover_data=["game", "opponent", "result", "delta"])
                fn = os.path.join(settings.MEDIA_ROOT, '', 'plots', 'rating_bot.html')
                fig_bot.write_html(fn)
                context['rating_plot_bot'] = os.path.join(settings.MEDIA_URL, '', 'plots', 'rating_bot.html')

            if g_human > 0:
                df_human = pd.DataFrame(info_human)
                # title = f'{player.name()}, Rating vs humans progress'
                fig_human = px.line(df_human, x="N", y="rating", hover_name="date", hover_data=["game", "opponent", "result", "delta"])
                fn = os.path.join(settings.MEDIA_ROOT, '', 'plots', 'rating_human.html')
                fig_human.write_html(fn)
                context['rating_plot_human'] = os.path.join(settings.MEDIA_URL, '', 'plots', 'rating_human.html')

    context['info'] = info
    context['info_bot'] = info_bot
    context['info_human'] = info_human
    context['player'] = player
    if oid:
        context['opponent'] = opponent
    return render(request, "/player_info.html", context)

def reset_all_scores(request):
    players = Player.objects.all()
    for player in players:
        player.rating = 600
        player.bot_rating = 600
        player.human_rating = 600
        player.save()
    return redirect(reverse(":leaderboard"))

def reset_bot_scores(request):
    players = Player.objects.filter(is_bot=True)
    for player in players:
        player.rating = 600
        player.bot_rating = 600
        player.human_rating = 600
        player.save()
    return redirect(reverse(":leaderboard"))

def delete_unfinished_games(request):
    not_finished = Game.objects.filter(is_finished=False)
    not_finished.delete()
    return redirect(reverse(":leaderboard"))

@csrf_exempt
def delete_game(request):
    if request.user.is_superuser:
        if request.method == 'POST' :
            data = json.loads(request.body)
            if data.get("game_id") is not None:
                game_id = int(data["game_id"])
                game = Game.objects.filter(id=game_id).first()
                game.delete()
                return JsonResponse({'message':f'game {game_id} deleted', 'status':200})
            return JsonResponse({'message':'No game ID', 'status':400})
        return JsonResponse({'message':'Bad method', 'status':400})
    return JsonResponse({'message':'Superuser required', 'status':400})






