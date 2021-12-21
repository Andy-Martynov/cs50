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

from .agents import lasker, capablanca, alekhin, botvinnik, smyslov, petrosyan

from game.models import Player, Game, GameKind
from .models import Connect4Pos

AGENTS = {}
AGENTS[13] = lasker
AGENTS[14] = capablanca
AGENTS[15] = alekhin
AGENTS[16] = botvinnik
AGENTS[17] = smyslov
AGENTS[18] = petrosyan

NAME = 'connect4'

import numpy as np

import time

R = 6
Rp1 = R + 1
Rm1 = R - 1
C = 7
Cp1 = C + 1
Cm1 = C - 1
Rp1Cp1 = Rp1 * Cp1

#______________________________________________________ ABOUT __________________
from common.instruments import show_md

def about(request):
    entry_rus = os.path.join(settings.MEDIA_ROOT, 'four', 'md', 'about_rus.md')
    entry_eng = os.path.join(settings.MEDIA_ROOT, 'four', 'md', 'about_eng.md')
    return show_md(request, entry_rus=entry_rus, entry_eng=entry_eng, layout='connect4/layout.html')

# -------------------------------------------------- environment ---------------

class Config:
    def __init__(self):
        self.rows = 6
        self.columns = 7
        self.inarow = 4

class Obs:
    def __init__(self):
        self.board = np.array([0 for i in range(R*C)])
        self.mark = 0

# -------------------------------------------------- some helpers --------------
def int_to_bin(x):
    return bin(x)[2:].zfill(64)

# -------------------------------------------------- State ---------------------
# copied from agents
class State:
    def __init__(self):
        self.pos = dict()
        self.pos[1] = 0
        self.pos[2] = 0
        self.mask = 0

    def from_pos(one, two):
        state = State()
        state.pos[1] = one
        state.pos[2] = two
        state.mask = one | two
        return state

    def valid_moves(self):
        return [i for i in range(C) if not (self.mask >> 5+7*i) & 1]

    def from_grid(grid):
        state = State()
        matrix = np.array([0 for i in range(Rp1Cp1)]).reshape(Rp1, Cp1)
        for r in range(R):
            for c in range(C):
                matrix[r+1, c] = grid[r][c]
        position1, position2 = '', ''
        for c in range(C, -1, -1):
            for r in range(0, Rp1):
                position1 += ['0', '1'][matrix[r,c] == 1]
                position2 += ['0', '1'][matrix[r,c] == 2]
        state.pos[1] = int(position1, 2)
        state.pos[2] = int(position2, 2)
        state.mask = state.pos[1] | state.pos[2]
        return state

    def to_grid(self):
        position1 = int_to_bin(self.pos[1])
        position2 = int_to_bin(self.pos[2])
        matrix = np.array([0 for i in range(Rp1Cp1)]).reshape(Rp1, Cp1)
        for c in range(0, Cp1):
            for r in range(R, -1, -1):
                if position1[-1] == '1':
                    matrix[r,c] = 1
                position1 = position1[:-1]
                if position2[-1] == '1':
                    matrix[r,c] = 2
                position2 = position2[:-1]
        return matrix[1:, :-1]

    def connected_four(self, mark):
        position = self.pos[mark]
        # Horizontal check
        m = position & (position >> 7)
        if m & (m >> 14): return True
        # Diagonal \
        m = position & (position >> 6)
        if m & (m >> 12): return True
        # Diagonal /
        m = position & (position >> 8)
        if m & (m >> 16): return True
        # Vertical
        m = position & (position >> 1)
        if m & (m >> 2): return True
        # Nothing found
        return False

    def make_move(self, col, mark):
        new_state = State()
        new_state.mask = self.mask | (self.mask + (1 << (col*7)))
        new_state.pos[mark] = self.pos[3-mark] ^ new_state.mask
        new_state.pos[3-mark] = self.pos[3-mark]
        return new_state

    def copy(self):
        new_state = State()
        new_state.mask = self.mask
        new_state.pos[1] = self.pos[1]
        new_state.pos[2] = self.pos[2]
        return new_state

    def doublewin(self, mark):
        win = 0
        for col in self.valid_moves():
            next_state = self.make_move(col, mark)

            if next_state.connected_four(mark):
                next_state_opp =  self.make_move(col, 3-mark)
                if next_state_opp.make_move(col, mark).connected_four(mark):
                    return True # win with this c first or second move, unstoppable
                win += 1
                if win == 2:
                    return True # more than one winning move
        return False

    FULLBOARD = 279258638311359

    # Helper function for minimax: checks if game has ended
    def is_terminal(self):
        # Check for draw
        if self.mask == 279258638311359:
            return True
        if self.connected_four(1):
            return True
        if self.connected_four(2):
            return True
        return False

    def show(self):
        print()
        print(self.to_grid())
        print()
        print('one:', bin(self.pos[1])[2:].zfill(64))
        print('two:', bin(self.pos[2])[2:].zfill(64))
        print('msk:', bin(self.mask)[2:].zfill(64))
        print()

    def moves(self):
        s = int_to_bin(self.mask)
        return s.count("1")

    def zero(self, row, col):
        cell = 1 << (col * C + Rm1 - row)
        return cell & self.mask == 0

    def fill(self, row, col, mark):
        new_state = State()
        cell = 1 << (col * C + Rm1 - row)
        new_state.mask = self.mask | cell
        new_state.pos[mark] = self.pos[mark] | cell
        new_state.pos[3-mark] = self.pos[3-mark]
        return new_state

    def threat(self, row, col, mark):
        if not self.zero(row, col):
            return False
        new_state = self.fill(row, col, mark)
        if new_state.connected_four(mark):
            return True
        return False

    def value(self, row, col):
        cell = 1 << (col * C + Rm1 - row)
        if cell & self.pos[1]:
            return 1
        if cell & self.pos[2]:
            return 2
        return 0

    def empty_row(self, col):
        for row in range(Rm1, -1, -1):
            if self.zero(row, col):
                break
        return row

    def eq(self, state):
        return self.pos[1] == state.pos[1] and self.pos[2] == state.pos[2] and self.mask == state.mask

# -------------------------------------------- helpers for play ----------------
config = Config()

def drop(grid, col, piece):
    next_grid = grid.copy()
    for row in range(R-1, -1, -1):
        if next_grid[row][col] == 0:
            break
    next_grid[row][col] = piece
    return next_grid, row, col

def check_win(g, piece):
    # Returns True if dropping piece in column results in game win
    grid = np.asarray(g)
    # horizontal
    for row in range(config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[row,col:col+config.inarow])
            if window.count(piece) == config.inarow:
                return True
    # vertical
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns):
            window = list(grid[row:row+config.inarow,col])
            if window.count(piece) == config.inarow:
                return True
    # positive diagonal
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row+config.inarow), range(col, col+config.inarow)])
            if window.count(piece) == config.inarow:
                return True
    # negative diagonal
    for row in range(config.inarow-1, config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
            if window.count(piece) == config.inarow:
                return True
    return False

def winning(g, piece):
    # Returns 4 winnig line
    grid = np.asarray(g)
    # horizontal
    for row in range(config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[row,col:col+config.inarow])
            if window.count(piece) == config.inarow:
                four = [(row,c) for c in range(col, col+4, 1)]
                return four
    # vertical
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns):
            window = list(grid[row:row+config.inarow,col])
            if window.count(piece) == config.inarow:
                four = [(r,col) for r in range(row, row+4, 1)]
                return four
    # positive diagonal
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row+config.inarow), range(col, col+config.inarow)])
            if window.count(piece) == config.inarow:
                four = [(row+i,col+i) for i in range(4)]
                return four
    # negative diagonal
    for row in range(config.inarow-1, config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
            if window.count(piece) == config.inarow:
                four = [(row-i,col+i) for i in range(4)]
                return four
    return []

def norm(scores):
    '''
    scores: Bot player send move scores via session

    As scores schema differs for every bot, we normalize them

    Return normalized scores
    '''
    s = []
    smin, smax = np.inf, -np.inf
    for i in range (7):
        if i in scores:
            if not scores[i] in [-np.inf, np.inf]:
                smin = min(scores[i], smin)
                smax = max(scores[i], smax)
    for i in range (7):
        if i in scores:
            if not scores[i] in [-np.inf, np.inf]:
                if smin != smax:
                    s.append(round((scores[i] - smin) / (smax - smin), 2))
                else:
                    s.append(0)
            else:
                if scores[i] == -np.inf:
                    s.append('-&#8766;')
                else:
                    s.append('&#8766;')
        else:
            s.append('_')
    return s


#___________________________________________________________ GAMEPLAY __________
def index(request):
    kind = GameKind.objects.filter(name=NAME).first()
    return redirect(reverse("game:new_game", args=[kind.id]))

# __________________________________________________________ GAME GO ___________
def game_go(request, id):
    game = Game.objects.filter(id=id).first()
    position, _ = Connect4Pos.objects.get_or_create(game=game)

    context = {}
    context['game'] = game
    context['championship'] = False
    context['max_games'] = 1
    context['current_game'] = 1
    matrix = [[0 for c in range(C)] for r in range(R)]
    context['matrix'] = matrix

    context['human_num'] = 0
    if request.user.is_authenticated:
        if request.user.player == game.first:
            context['human_num'] = 1
        if request.user.player == game.second:
            context['human_num'] = 2
    else: # Guest
        if not game.first.is_bot:
            context['human_num'] = 1
        if not game.second.is_bot:
            context['human_num'] = 2
    context['uid'] = request.user.id
    return render(request, "connect4/game.html", context)

# _____________________________________________________________ PLAY ___________
@csrf_exempt
def play(request):
    '''
    Process of playing
    '''
    # if bot is playing the methud is PUT
    if request.method in ["PUT", "POST"]:
        data = json.loads(request.body)
        if 'game_id' in data:
            game_id = int(data['game_id'])
        else:
            context = {}
            context['game_id_ok'] = False
            context['message'] = 'Hey, no game ID!'
            return JsonResponse(context, status=200)
    game = Game.objects.filter(id=game_id).first()

    column = None
    is_bot_playing = True

    if request.method == "POST":
        data = json.loads(request.body)
        if 'game_id' in data:
            game_id = int(data['game_id'])
            if game_id == game.id:
                if 'column' in data:
                    column = int(data.get("column"))
                    is_bot_playing = False
                    if not column in [0,1,2,3,4,5,6]:
                        return JsonResponse({"error": f"I could not get column method {request.method}, data {data}, column <{column+0}>"}, status=400)
                else:
                    return JsonResponse({"error": "no column in data"}, status=400)
            else:
                return JsonResponse({"error": f"game id <{game_id}> != <{game.id}>"}, status=400)
        else:
            return JsonResponse({"error": "no game_id"}, status=400)

    context = {}
    context['game_id'] = game.id
    position = Connect4Pos.objects.filter(game=game).first()
    state = State.from_pos(position.one, position.two)

    grid = state.to_grid()
    moves_made = state.moves()
    if moves_made % 2 == 0:
        mark = 1
    else:
        mark = 2

    if is_bot_playing:
        agents = Player.objects.filter(is_bot=True)
        bot_players = {}
        for agent in agents:
            if agent.user.id in AGENTS:
                bot_players[agent.user.username] = AGENTS[agent.user.id]

        if moves_made % 2 == 0:
            agent = bot_players[game.first.user.username]
        else:
            agent = bot_players[game.second.user.username]

    if not game.gameover:
        obs = Obs()
        obs.mark = mark
        obs.board = list(np.asarray(grid).flatten())
        config = Config()

        start = time.time()

        if is_bot_playing:
            col = agent(request, obs, config)
        else:
            col = column

        delay = time.time() - start
        context['delay'] = f'{delay:.2f}"'
        context['move'] = col

        row = state.empty_row(col)
        grid[row][col] = mark
        game.moves += str(col)
        moves_made += 1

    gameover = False
    for m in [1, 2]:
        if check_win(grid, m):
            if m == 1:
                game.winner = game.first
                game.loser = game.second
                context['winner'] = 1
            else:
                game.winner = game.second
                game.loser = game.first
                context['winner'] = 2
            gameover = True
            game.is_finished = True
            break

    state = State.from_grid(grid)
    position.one = state.pos[1]
    position.two = state.pos[2]
    position.save()
    game.save()

    if not game.is_finished and moves_made == 42:
        gameover = True
        context['winner'] = 0
        game.is_finished = True

    if gameover:
        game.is_finished = True
    game.save()

    if 'depth' in request.session:
        context['depth'] = request.session['depth']
    else:
        context['depth'] = 0

    if 'scores' in request.session:
        context['scores'] = norm(request.session['scores'])
    else:
        context['scores'] = norm({})
    request.session['scores'] = {}

    context['gameover'] = gameover

    signal = [[0 for c in range(C)] for r in range(R)]

    if gameover:
        if context['winner'] == 1:
            context['four'] = winning(grid, 1)
        if context['winner'] == 2:
            context['four'] = winning(grid, 2)

        if 'current_game' in request.session:
            request.session['current_game'] += 1
        request.session['championat_game_id'] = None

        if request.user.is_authenticated:
            request.user.fourplayer.is_playing = False
            request.user.fourplayer.ready = True
            request.user.fourplayer.save()
    else:
        if game.hints:
            for r in range(R):
                for c in range(C):
                    if grid[r][c] == 0:
                        if state.threat(r, c, 1):
                            signal[r][c] += 1
                        if state.threat(r, c, 2):
                            signal[r][c] += 2
        context['signal'] = signal

    if not (game.first.is_bot or game.second.is_bot):
        context['move'] = col
        context['pos1'] = int_to_bin(position.one)
        context['pos2'] = int_to_bin(position.two)

        pusher_client.trigger('my-channel', 'connect4_move', context)
    return JsonResponse(context, status=200)


def game_replay(request, id):
    '''
    Replay finished game
    '''
    game = Game.objects.filter(id=id).first()
    context = {}
    context['game'] = game
    context['num_moves'] = len(game.moves)
    context['steps'] = [(i, i%2) for i in range(1, 43)]
    matrix = [[0 for c in range(C)] for r in range(R)]
    context['matrix'] = matrix
    return render(request, "four/game_replay.html", context)





