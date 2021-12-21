from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rtc.views import pusher_client
from mysite import settings
import os

from .models import Player, Game, GameKind
from account.models import User

import numpy as np
import pandas as pd

import plotly.express as px

import random
import time

#______________________________________________________ ABOUT __________________
from common.instruments import show_md

def about(request):
    entry_rus = os.path.join(settings.MEDIA_ROOT, 'game', 'md', 'about_rus.md')
    entry_eng = os.path.join(settings.MEDIA_ROOT, 'game', 'md', 'about_eng.md')
    return show_md(request, entry_rus=entry_rus, entry_eng=entry_eng, layout='game/layout.html')

# _________________________________________________________ INDEX ______________

@login_required
def index(request, id=None):
    if request.method == 'POST' : # options changed
        data = request.POST
        if 'kind_id' in data:
            kind = GameKind.objects.filter(id=data['kind_id']).first()
            if kind:
                if 'opponent_id' in data:
                    opponent = Player.objects.filter(id=data['opponent_id']).first()
                    if opponent:
                        player = Player.objects.filter(user=request.user).first()
                        hints = False
                        if 'hints' in data :
                            if data['hints'] == 'on':
                                hints = True
                        turn = random.choice([1, 2])
                        if turn == 1:
                            game = Game.objects.create(kind=kind, first=player, second=opponent, hints=hints)
                        else:
                            game = Game.objects.create(kind=kind, first=opponent, second=player, hints=hints)
                        if not opponent.is_bot: # both are human
                            if not player == opponent: # not play with myself
                                return redirect(reverse('game:invite', args=[game.id]))
                        return redirect(reverse(f"{game.kind.name}:game_go", args=[game.id]))
        messages.info(request, f'Bad request data: {data}', extra_tags='alert-danger')

    user = request.user
    if user.is_authenticated:
        player = Player.objects.filter(user=user).first()
        if not player:
            player = Player.objects.create(user=user)
            data = {}
            data['id'] = player.id
            data['uid'] = player.user.id
            data['name'] = player.name()
            data['image'] = player.user.filename()
            pusher_client.trigger('my-channel', 'game_new_player', data)
            messages.info(request, f'Player {player.name()} created', extra_tags='alert-warning')
        user.player.save()

    context = {}

    kinds = GameKind.objects.all()
    if id:
        kind_selected = kinds.filter(id=id).first()
    else:
        nums = [k.id for k in kinds]
        num = random.choice(nums)
        kind_selected = kinds.filter(id=num).first()

    humans = None

    bots = Player.objects.filter(is_bot=True, user__is_active=True)
    humans = Player.objects.filter(is_bot=False).exclude(user=request.user)
    players = bots | humans
    players = players.order_by('-is_bot')
    opponent = players.filter(kind=kind_selected).first()

    context['kinds'] = kinds
    context['bots'] = bots
    context['humans'] = humans
    context['players'] = players
    context['kind_selected'] = kind_selected
    context['opponent'] = opponent
    return render(request, "game/index.html", context)


# _________________________________________________________ NEW GAME ___________
def new_game(request, id):
    '''
    Selects two players, hints mode and starts a game
    '''
    context = {}
    kind = GameKind.objects.filter(id=id).first()
    if not kind:
        context['error'] = f'NO GAME {id}'
        return render(request, "game/new_game.html", context)
    context['kind'] = kind

    if request.method == 'POST' : # options changed
        data = request.POST
        if 'first_player_name' in data :
            first_player_name = data['first_player_name']
        if 'second_player_name' in data :
            second_player_name = data['second_player_name']
        hints = False
        if 'hints' in data :
            if data['hints'] == 'on':
                hints = True
        first_player = Player.objects.filter(user__username=first_player_name).first()
        second_player = Player.objects.filter(user__username=second_player_name).first()
        game = Game.objects.create(kind=kind, first=first_player, second=second_player, hints=hints)
        username = request.user.username
        if not (first_player.is_bot or second_player.is_bot): # both are human
            if not (first_player.user.username == username and second_player.user.username == username): # not play with myself
                return redirect(reverse('game:invite', args=[game.id]))
        return redirect(reverse(f"{game.kind.name}:game_go", args=[game.id]))

    if request.user.is_authenticated:
        username = request.user.username
        context['human_players'] = Player.objects.filter(is_bot=False, user__is_active=True).exclude(user__username=username)
    else:
        username = 'Guest'

    user_player = Player.objects.filter(user__username=username).first()
    bot_players = Player.objects.filter(is_bot=True, kind=kind, user__is_active=True)

    context['bot_players'] = bot_players
    context['user_player'] = user_player

    turn = random.choice([1, 2])
    if turn == 1:
        context['first_player_name'] = username
        context['second_player_name'] = bot_players.first().user.username
    else:
        context['first_player_name'] = bot_players.first().user.username
        context['second_player_name'] = username
    return render(request, "game/new_game.html", context)

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
                                return redirect(reverse(f"{kind.name}:game_go", args={'id': game.id}))
                            return redirect(reverse("game:index", args=[kind.id]))

                        return JsonResponse({'message':'No confirm', 'status':400})
                    return JsonResponse({'message':'Bad opponent ID', 'status':400})
                return JsonResponse({'message':'No opponent ID', 'status':400})
            return JsonResponse({'message':'Bad game ID', 'status':400})
        return JsonResponse({'message':'No game ID', 'status':400})

    data = {}
    data['kind'] = kind.name
    data['inviter_id'] = request.user.id
    data['inviter_name'] = request.user.player.name()
    data['opponent_id'] = opponent.user.id
    data['game_id'] = game.id
    pusher_client.trigger('my-channel', 'game_invite', data)

    context = {}
    context['opponent'] = opponent
    context['game'] = game
    context['game_id'] = game.id
    context['kind'] = game.kind.name
    context['invite_send'] = True
    return render(request, "game/index.html", context)

# _______________________________________________________ CANCEL INVITE ________
@csrf_exempt
# @login_required
def cancel_invite(request, id):
    '''
    Cancel the invitation
    '''
    game = Game.objects.filter(id=id).first()
    player = Player.objects.filter(user=request.user).first()
    if player == game.first:
        opponent = game.second
    else:
        opponent = game.first

    data = {}
    data['game_id'] = id
    data['opponent_id'] = opponent.id
    pusher_client.trigger('my-channel', 'game_invite_canceled', data)
    return redirect(reverse("game:index", args=[game.kind.id]))

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
                response['kind'] = game.kind.name
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
        data['kind'] = game.kind.name
        data['message'] = 'game canceled'
        pusher_client.trigger('my-channel', 'game_canceled', data)
    if request.user == game.first.user:
        messages.info(request, f"The game with {game.second.user.username} canceled.", extra_tags='alert-danger')
    else:
        messages.info(request, f"The game with {game.first.user.username} canceled.", extra_tags='alert-danger')
    return redirect(reverse("game:index", args=[game.kind.id]))


#_________________________________________________________ GAME GO _____________

def game_go(request, kind_id, id):
    kind = GameKind.objects.filter(id=kind_id).first()
    return redirect(reverse(f"{kind.name}:game_go", args=[id]))

def game_replay(request, kind_id, id):
    kind = GameKind.objects.filter(id=kind_id).first()
    return redirect(reverse(f"{kind.name}:game_replay", args=[id]))
















# ___________________________________________________ BOT CHAMPIONSHIP _________

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

# ________________________________________________________ LEADERBOARD _________

def leaderboard(request):
    '''
    The leaderboard
    '''
    context = {}

    kinds = GameKind.objects.all()
    total_games = Game.objects.all().exclude(is_finished=False).count()

    tmp_table = {}

    players = Player.objects.all().order_by('-rating')
    for player in players:
        games = Game.objects.filter(first=player) | Game.objects.filter(second=player)
        games = games.exclude(first=player, second=player).exclude(is_finished=False)
        player_item ={}
        player_games_info = []
        player_item['player'] = player

        total_info = {}
        total_info['kind'] = 'total'
        total_info['total'] = 0
        total_info['win'] = 0
        total_info['loss'] = 0
        total_info['tie'] = 0
        total_info['rating'] = 0

        for kind in kinds:
            games_of_kind = games.filter(kind=kind)
            g = games_of_kind.count()
            win = games_of_kind.filter(winner=player).count()
            loss = games_of_kind.filter(loser=player).count()

            kind_info = {}
            kind_info['kind'] = kind.name
            kind_info['total'] = g
            kind_info['win'] = win
            kind_info['loss'] = loss
            kind_info['tie'] = g - win - loss
            if g> 0:
                kind_info['rating'] = 100 * (win - loss) / g
            player_games_info.append(kind_info)

            total_info['total'] += g
            total_info['win'] += win
            total_info['loss'] += loss
            total_info['tie'] += g - win - loss

        if total_info['total'] > 0:
            total_info['rating'] = 100 * (total_info['win'] - total_info['loss']) / total_info['total']
        player_games_info.append(total_info)

        player.rating = total_info['rating']
        player.win = total_info['win']
        player.loss = total_info['loss']
        player.tie = total_info['tie']
        player.games = total_info['total']
        player.save()
        player_item['info'] = player_games_info
        tmp_table[player.id] = player_item

    matrix = []
    players = players.order_by('-rating')
    for player in players:
        matrix.append(tmp_table[player.id])

    context['players'] = players
    context['kinds'] = kinds
    context['matrix'] = matrix
    context['total_games'] = total_games
    return render(request, "game/leaderboard.html", context)

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
    return render(request, "game/game_list.html", context)

def game_list_all(request):
    '''
    Game list without pagination
    '''
    context = {}
    games = Game.objects.all().exclude(is_finished=False).order_by('-id')
    context['total'] = games.count()
    players = Player.objects.all()
    context['games'] = games
    context['players'] = players
    return render(request, "game/game_list_all.html", context)

def kinds_info(request):
    context = {}
    kinds = GameKind.objects.all()
    info = []
    for kind in kinds:
        item = {}
        item['kind'] = kind
        item['games'] = kind.games.all()
        item['bots'] = kind.bots.all()
        info.append(item)

    context['kinds'] = kinds
    context['info'] = info
    return render(request, "game/kinds.html", context)



def player_info(request, id, oid=None):
    '''
    id: player id
    oid: opponent id, shows all if None
    '''
    context = {}
    kinds = GameKind.objects.all()
    player = Player.objects.filter(id=id).first()
    if oid:
        opponent = Player.objects.filter(id=oid).first()
        games =  Game.objects.filter(first=player, second=opponent) | Game.objects.filter(first=opponent, second=player)
    else:
        games =  Game.objects.filter(first=player) | Game.objects.filter(second=player)
        games = games.exclude(first=player, second=player)
        opponent = None

    n_kind = games.exclude(is_finished=False).values('kind').distinct().count()

    player_kinds = games.exclude(is_finished=False).values('kind').distinct()
    context['player_kinds'] = player_kinds

    games = games.exclude(is_finished=False).order_by('id')

    data = []
    scores = {k.id :0 for k in kinds}
    wins = {k.id :0 for k in kinds}
    losses = {k.id :0 for k in kinds}
    ties = {k.id :0 for k in kinds}


    for game in games:
        item = {}
        item['game'] = game.kind.name
        item['date'] = game.timestamp
        if game.first == player:
            versus = game.second
        else:
            versus = game.first
        item['versus'] = versus.user.username
        if game.winner == player:
            item['result'] = 'win'
            scores[game.kind.id] += 1
            wins[game.kind.id] += 1
        elif game.loser == player:
            item['result'] = 'loss'
            scores[game.kind.id] -= 1
            losses[game.kind.id] += 1
        else:
            item['result'] = 'tie'
            ties[game.kind.id] += 1
        item['score'] = scores[game.kind.id]

        total = wins[game.kind.id] + losses[game.kind.id] + ties[game.kind.id]
        if total > 0:
            item['rating'] = round(100*(wins[game.kind.id] - losses[game.kind.id]) / total, 0)
        else:
            item['rating'] = 0
        data.append(item)

        df = pd.DataFrame(data)

        if n_kind > 1:
            fig = px.line(df, x="date", y="score", color='game', labels={'date':'Date', 'score':'win/loss', 'versus':'versus'}, hover_data=['game', 'date', 'versus', 'result'], width=800, height=400) #, title=title)
        else:
            fig = px.line(df, x="date", y="score", hover_data=['game', 'versus', 'result'], width=800, height=400) #, title=title)

        fig.update_traces(mode='lines+markers')
        # fig.update_layout(hovermode=["x unified"])
        fn = os.path.join(settings.MEDIA_ROOT, '', 'plots', 'scores.html')
        fig.write_html(fn)
        context['scores_plot'] = os.path.join(settings.MEDIA_URL, '', 'plots', 'scores.html')

        if n_kind > 1:
            fig = px.line(df, x="date", y="rating", color='game', labels={'date':'Date', 'rating':'Rating', 'versus':'versus'}, hover_data=['game', 'date', 'versus', 'result'], width=800, height=400) #, title=title)
        else:
            fig = px.line(df, x="date", y="rating", hover_data=['game', 'versus', 'result'], width=800, height=400) #, title=title)
        fig.update_traces(mode='lines+markers')
        # fig.update_layout(hovermode=["x unified"])
        fn = os.path.join(settings.MEDIA_ROOT, '', 'plots', 'ratings.html')
        fig.write_html(fn)
        context['ratings_plot'] = os.path.join(settings.MEDIA_URL, '', 'plots', 'ratings.html')

        context['player'] = player
        context['games'] = games

        context['opponent'] = opponent
    return render(request, "game/player_info.html", context)

def reset_all_scores(request):
    players = Player.objects.all()
    for player in players:
        player.rating = 0
        player.bot_rating = 0
        player.human_rating = 0
        player.save()
    return redirect(reverse("game:leaderboard"))

def reset_bot_scores(request):
    players = Player.objects.filter(is_bot=True)
    for player in players:
        player.rating = 0
        player.bot_rating = 0
        player.human_rating = 0
        player.save()
    return redirect(reverse("game:leaderboard"))

def delete_unfinished_games(request):
    not_finished = Game.objects.filter(is_finished=False)
    not_finished.delete()
    return redirect(reverse("game:leaderboard"))

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






