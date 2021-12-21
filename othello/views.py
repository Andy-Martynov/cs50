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

from game.models import Player, Game, GameKind
from .models import OthelloPos

import numpy as np
import pandas as pd

import plotly.express as px

import random
import time

NAME = 'othello'
R, C = 8, 8

#_____________________________________________________________ AGENTS __________

def agent_othello(request, state, mark):
    valid_moves = state.valid_moves(mark)
    if len(valid_moves) == 0:
        return None, None

    very_good_moves = []
    for move in valid_moves:
        if move in [(0,0), (0,7), (7,0), (7,7)]:
            very_good_moves.append(move)
    if len(very_good_moves) > 0:
        very_good_moves_numbers = [i for i in range(len(very_good_moves))]
        n = random.choice(very_good_moves_numbers)
        return very_good_moves[n][0], very_good_moves[n][1]

    good_moves = []
    for cell in [(0,0), (0,7), (7,0), (7,7)]:
        hvcells = state.hv_neighbors(cell[0], cell[1])
        for hvcell in hvcells:
            curr = (hvcell[0], hvcell[1])
            dr, dc = curr[0] - cell[0], curr[1] - cell[1]
            while curr[0] >= 0 and curr[0] < R and curr[1] >= 0 and curr[1] < C:
                if curr in valid_moves:
                    good_moves.append(curr)
                    break
                if state.value(curr[0], curr[1]) == 3-mark:
                    break
                curr = (curr[0] + dr, curr[1] + dc)
    if len(good_moves) > 0:
        good_moves_numbers = [i for i in range(len(good_moves))]
        n = random.choice(good_moves_numbers)
        return good_moves[n][0], good_moves[n][1]

    valid_moves_numbers = [i for i in range(len(valid_moves))]
    n = random.choice(valid_moves_numbers)
    return valid_moves[n][0], valid_moves[n][1]

def agent_desdemona(request, state, mark):
    valid_moves = state.valid_moves(mark)
    if len(valid_moves) == 0:
        return None, None
    valid_moves_numbers = [i for i in range(len(valid_moves))]
    n = random.choice(valid_moves_numbers)
    return valid_moves[n][0], valid_moves[n][1]

AGENTS = {}
AGENTS[27] = agent_othello
AGENTS[28] = agent_desdemona
# AGENTS[15] = alekhin

#___________________________________________________________ POSITION __________

def int_to_bin(x):
    return bin(x)[2:].zfill(64)

class State:
    def __init__(self):
        self.pos = dict()
        self.pos[1] = 0
        self.pos[2] = 0

    def from_pos(one, two):
        state = State()
        state.pos[1] = one
        state.pos[2] = two
        return state

    def from_grid(grid):
        state = State()
        position1, position2 = '', ''
        for r in range(R-1, -1, -1):
            for c in range(C-1, -1, -1):
                position1 += ['0', '1'][grid[r][c] == 1]
                position2 += ['0', '1'][grid[r][c] == 2]
        state.pos[1] = int(position1, 2)
        state.pos[2] = int(position2, 2)
        return state

    def to_grid(self):
        position1 = int_to_bin(self.pos[1])
        position2 = int_to_bin(self.pos[2])
        grid = [[0 for c in range(C)] for r in range(R)]
        for r in range(R):
            for c in range(C):
                if position1[-1] == '1':
                    grid[r][c] = 1
                position1 = position1[:-1]
                if position2[-1] == '1':
                    grid[r][c] = 2
                position2 = position2[:-1]
        return grid

    def copy(self):
        new_state = State()
        new_state.pos[1] = self.pos[1]
        new_state.pos[2] = self.pos[2]
        return new_state

    def show(self):
        print()
        print(self.to_grid())
        print()
        print('one:', bin(self.pos[1])[2:].zfill(64))
        print('two:', bin(self.pos[2])[2:].zfill(64))
        print()

    def moves(self):
        s = int_to_bin(self.pos[1] | self.pos[2])
        return s.count("1")

    def zero(self, row, col):
        cell = 1 << (row * C + col)
        return cell & (self.pos[1] | self.pos[2]) == 0

    def fill(self, row, col, mark):
        new_state = State()
        cell = 1 << (row * C + col)
        new_state.pos[mark] = self.pos[mark] | cell
        new_state.pos[3-mark] = self.pos[3-mark]
        return new_state

    def value(self, row, col):
        cell = 1 << (row * C + col)
        if cell & self.pos[1]:
            return 1
        if cell & self.pos[2]:
            return 2
        return 0

    def eq(self, state):
        return self.pos[1] == state.pos[1] and self.pos[2] == state.pos[2]

    def neighbors(self, row, col):
        cells = []
        for r in range(max(0,row-1), min(R, row+2)):
            for c in range(max(0,col-1), min(C, col+2)):
                if not (r == row and c == col):
                    cells.append((r,c))
        return cells

    def hv_neighbors(self, row, col):
        cells = []
        for r in range(max(0,row-1), min(R, row+2)):
            for c in range(max(0,col-1), min(C, col+2)):
                if not (r == row and c == col):
                    if (r == row or  c == col):
                        cells.append((r,c))
        return cells

    def is_valid(self, row, col, mark):
        if not self.zero(row, col):
            return False
        for r in range(max(0,row-1), min(R, row+2)):
            for c in range(max(0,col-1), min(C, col+2)):
                if not (r == row and c == col):
                    if self.value(r,c) == 3-mark:
                        dr, dc = r-row, c-col
                        xr, xc = r+dr, c+dc
                        while xr >= 0 and xr < R and xc >= 0 and xc < C:
                            if self.zero(xr, xc):
                                break
                            if self.value(xr, xc) == mark:
                                return True
                            xr += dr
                            xc += dc
        return False

    def valid_moves(self, mark):
        cells = []
        for r in range(R):
            for c in range(C):
                if self.is_valid(r, c, mark):
                    cells.append((r,c))
        return cells

    def make_move(self, row, col, mark):
        new_state = State()
        new_state.pos[mark] = self.pos[mark] | (1 << (row*C + col))
        new_state.pos[3-mark] = self.pos[3-mark]
        captives = []
        for r in range(max(0,row-1), min(R, row+2)):
            for c in range(max(0,col-1), min(C, col+2)):
                if not (r == row and c == col):
                    if self.value(r,c) == 3-mark:
                        dr, dc = r-row, c-col
                        xr, xc = r+dr, c+dc
                        enemies = [(r,c)]
                        while xr >= 0 and xr < R and xc >= 0 and xc < C:
                            if self.zero(xr, xc):
                                break
                            if self.value(xr, xc) == mark:
                                captives += enemies
                                break
                            enemies.append((xr,xc))
                            xr += dr
                            xc += dc
        for captive in captives:
            r, c = captive[0], captive[1]
            new_state.pos[mark] |= 1 << (r*C + c)
            new_state.pos[3-mark] &= ~(1 << (r*C + c))
        return new_state

    def count(self, mark):
        qty = 0
        for r in range(R):
            for c in range(C):
                if self.value(r, c) == mark:
                    qty += 1
        return qty

#___________________________________________________________ GAMEPLAY __________
def index(request):
    kind = GameKind.objects.filter(name=NAME).first()
    return redirect(reverse("game:new_game", args=[kind.id]))

#________________________________________________________________ GAME GO ______
def game_go(request, id):
    game = Game.objects.filter(id=id).first()
    game.current = game.first
    game.save()
    kind = game.kind

    context = {}
    context['kind'] = kind.name
    context['game'] = game
    context['championship'] = False
    context['max_games'] = 1
    context['current_game'] = 1

    grid = [[0 for c in range(C)] for r in range(R)]
    grid[3][4] = 1
    grid[4][3] = 1
    grid[3][3] = 2
    grid[4][4] = 2

    state = State.from_grid(grid)
    position, _ = OthelloPos.objects.get_or_create(game=game)
    position.pos1 = int_to_bin(state.pos[1])
    position.pos2 = int_to_bin(state.pos[2])
    position.save()

    # подсказки
    valid_moves = state.valid_moves(1)
    signal = [[0 for c in range(C)] for r in range(R)]
    if game.hints:
        for move in valid_moves:
            signal[move[0]][move[1]] = 1

    context['grid'] = grid
    context['signal'] = signal

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
    return render(request, "othello/game.html", context)

#_____________________________________________________________ PLAY ____________
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
    position = OthelloPos.objects.filter(game=game).first()
    state = State.from_pos(int(position.pos1, 2), int(position.pos2, 2))
    if game.current == game.first:
        mark = 1
    else:
        mark = 2

    row, column = None, None
    is_bot_playing = True

    context = {}
    context['game_id'] = game.id
    context['method'] = 'GET'
    context['gameover'] = False
    context['valid_move'] = False
    context['game_id_ok'] = True

    # if human is playing the move
    if request.method == "POST":
        context['method'] = 'POST'
        data = json.loads(request.body)
        if 'game_id' in data:
            game_id = int(data['game_id'])
            if game_id == game.id:
                if game.gameover:
                    context['gameover'] = True
                    context['message'] = 'Hey, game is over!'
                    return JsonResponse(context, status=200)
                if 'row' in data:
                    row = int(data.get("row"))
                    if 'column' in data:
                        column = int(data.get("column"))
                        is_bot_playing = False
                        if not state.is_valid(row, column, mark):
                            context['message'] = 'Hey, illegal move!'
                            return JsonResponse(context, status=200)
                    else:
                        context['message'] = 'Hey, no column!'
                        return JsonResponse(context, status=400)
                else:
                    context['message'] = 'Hey, no row!'
                    return JsonResponse(context, status=400)
            else:
                context['game_id_ok'] = False
                context['message'] = 'Hey, wrong game ID!'
                return JsonResponse(context, status=200)
        else:
            context = {}
            context['game_id_ok'] = False
            context['message'] = 'Hey, no game ID!'
            return JsonResponse(context, status=200)

    context['valid_move'] = True

    # get the agent if bot is playing the move
    if is_bot_playing:
        bots = Player.objects.filter(is_bot=True)
        bot_players = {}
        for bot in bots:
            if bot.user.id in AGENTS:
                bot_players[bot.user.username] = AGENTS[bot.user.id]
        if mark == 1:
            agent = bot_players[game.first.user.username]
        else:
            agent = bot_players[game.second.user.username]

    # move

    if is_bot_playing:
        row, column = agent(request, state, mark)

    state = state.make_move(row, column, mark)
    # save position
    position = OthelloPos.objects.filter(game=game).first()
    position.pos1 = int_to_bin(state.pos[1])
    position.pos2 = int_to_bin(state.pos[2])
    position.save()
    game.moves += str(mark) + str(row) + str(column)
    game.save()
    #info for update
    context['move'] = {'row':row, 'column':column}
    context['prev'] = mark

    context['grid'] = state.to_grid()
    qty1 = state.count(1)
    qty2 = state.count(2)
    context['qty1'] = qty1
    context['qty2'] = qty2


    # gameover
    gameover = False
    if state.count(0) == 0:
        gameover = True
    elif len(state.valid_moves(1)) + len(state.valid_moves(2)) == 0:
        gameover = True

    if gameover:
        if game.gameover:
            game.is_finished = True
        game.gameover = True
        context['winner'] = 0
        if qty1 > qty2:
            game.winner = game.first
            context['winner'] = 1
        if qty1 < qty2:
            game.winner = game.second
            context['winner'] = 2
        game.save()
    context['gameover'] = gameover

    # переход хода
    valid_moves = state.valid_moves(3-mark)
    if len(valid_moves) > 0:
        mark = 3-mark
    else:
        valid_moves = state.valid_moves(mark)
    if mark == 1:
        game.current = game.first
    else:
        game.current = game.second
    game.save()

    # подсказки
    d = 0
    if game.hints:
        d = 3
    signal = [[0 for c in range(C)] for r in range(R)]

    for move in valid_moves:
        signal[move[0]][move[1]] = mark + d

    context['signal'] = signal

    context['mark'] = mark
    context['valid_move'] = 'yes'
    # request.session['f{KIND}_mark'] = mark

    if not game.is_finished:
        pusher_client.trigger('my-channel', f'{game.kind.name}_move', context)

    return JsonResponse(context, status=200)

# __________________________________________________________ REPLAY ____________
@csrf_exempt
def make_move(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if 'grid' in data and 'row' in data and 'column' in data and 'mark' in  data:
            grid = data['grid']
            mark = data['mark']
            row = data['row']
            column = data['column']
            state = State.from_grid(grid)
            new_state = state.make_move(row, column, mark)
            new_grid = new_state.to_grid()
            context = {}
            context['grid'] = new_grid
            return JsonResponse(context, status=200)
    return JsonResponse({}, status=400)



def game_replay(request, id):
    '''
    Replay finished game
    '''
    game = Game.objects.filter(id=id).first()
    game.current = game.first
    game.save()

    # key = f'game_{game.id}'
    # kind_game_busy = f'{game.kind}_busy'
    # kind_game_id = f'{game.kind}_game_id'

    # if key in request.session:
    #     del request.session[key]
    # if kind_game_id in request.session:
    #     del request.session[kind_game_id]
    # if kind_game_busy in request.session:
    #     request.session[f'{game.kind}_busy'] = 'free'
    #     del request.session[f'{game.kind}_busy']
    # request.session.modified = True

    context = {}
    context['kind'] = game.kind.name
    context['game'] = game
    context['championship'] = False
    context['max_games'] = 1
    context['current_game'] = 1

    grid = [[0 for c in range(C)] for r in range(R)]
    grid[3][4] = 1
    grid[4][3] = 1
    grid[3][3] = 2
    grid[4][4] = 2

    state = State.from_grid(grid)
    position, _ = OthelloPos.objects.get_or_create(game=game)
    position.pos1 = int_to_bin(state.pos[1])
    position.pos2 = int_to_bin(state.pos[2])
    position.save()

    # подсказки
    valid_moves = state.valid_moves(1)
    signal = [[0 for c in range(C)] for r in range(R)]
    if game.hints:
        for move in valid_moves:
            signal[move[0]][move[1]] = 1

    context['grid'] = grid
    context['signal'] = signal
    context['human_num'] = 0

    context['num_moves'] = len(game.moves) // 3
    return render(request, "othello/game_replay.html", context)










