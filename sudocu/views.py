from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

import copy
import random
import pickle
import os

from mysite import settings
from utils.forms import UploadFileForm

X = 9
Y = 9
GAME = None
AI = None
LAST = (X, Y)

def init(request):
    global GAME
    global AI
    GAME = Sudocu()
    AI = SudocuAI(GAME.board, height=X, width=Y)
    return redirect(reverse('sudocu:show'), args=["LET'S PLAY"])

def reduce(request):
    global GAME
    global AI
    AI.try_to_reduce_hints(GAME.board)
    mode = 'PLAY'
    return redirect(reverse('sudocu:show', args=[mode]))

def empty(request):
    global GAME
    global AI
    GAME = Sudocu()
    AI = SudocuAI(GAME.board, height=X, width=Y)
    for i in range(X):
        for j in range(Y):
            GAME.board[i][j]['value'] = 0
            GAME.board[i][j]['hint'] = {1,2,3,4,5,6,7,8,9}
            GAME.board[i][j]['disabled'] = False
    return redirect(reverse('sudocu:show'), args=['PLAY!'])

def random_sudocu(request, n):
    global GAME
    global AI
    GAME = Sudocu()
    AI = SudocuAI(GAME.board, height=X, width=Y)
    for i in range(X):
        for j in range(Y):
            GAME.board[i][j]['value'] = 0
            GAME.board[i][j]['hint'] = {1,2,3,4,5,6,7,8,9}
            GAME.board[i][j]['disabled'] = False
    q1 = quadrant(1,1)
    q5 = quadrant(4,4)
    q9 = quadrant(7,7)
    quadrants = [q1, q5, q9]
    random.seed()
    for q in quadrants :
        s = {1,2,3,4,5,6,7,8,9}
        for c in q :
            while True :
                v = random.randint(1,9)
                if v in s :
                    GAME.board[c[0]][c[1]]['value'] = v
                    s.remove(v)
                    break
    matrix = board_to_matrix(GAME.board)
    solution = find(matrix)
    if solution in [None, -1, 0] :
        mode = 'DEADEND'
        return redirect(reverse('sudocu:show', args=[mode]))
    for i in range(X):
        for j in range(Y):
            GAME.board[i][j]['value'] = solution[i][j][0]
    clues = 0
    while True :
        i = random.randint(0,8)
        j = random.randint(0,8)
        if not GAME.board[i][j]['disabled'] :
            GAME.board[i][j]['disabled'] = True
            clues += 1
            if clues == n :
                break
    for i in range(X):
        for j in range(Y):
            if  not GAME.board[i][j]['disabled'] :
                GAME.board[i][j]['value'] = 0
    return redirect(reverse('sudocu:show'), args=["LET'S PLAY"])

def start(request):
    global GAME
    global AI
    for i in range(X):
        for j in range(Y):
            if GAME.board[i][j]['value'] == 0 :
                GAME.board[i][j]['disabled'] = False
            else:
                GAME.board[i][j]['disabled'] = True
    messages.info(request, "Let's play!", extra_tags='alert-success')
    return redirect(reverse('sudocu:show'), args=['PLAY'])

def show(request, mode='PLAY'):
    global GAME
    global AI

    board = GAME.board.copy()
    if AI.lost(GAME.board):
        mode = 'LOST'
    matrix = []
    for r in range(Y):
        row = []
        for c in range(X):
            v = board[r][c]['value']
            d = board[r][c]['disabled']
            hint = board[r][c]['hint']
            color = board[r][c]['hint_color']
            ok = v in hint
            if len(hint)==0:
                v = 'X'
            last = (r == LAST[0]) and (c == LAST[1])
            row.append((r,c,v,d,hint,ok,last,color))
        matrix.append(row)
    return render(request, "sudocu/sudocu.html", {'matrix':matrix, 's369':[3,6,9], 'last':LAST, 'mode':mode})

def ai_move(request, mode='AI'):
    global GAME
    global AI
    global LAST

    move = None
    l = len(AI.moves)
    if l>0:
        rnd = random.randint(0, l-1)
        move = list(AI.moves)[rnd]
        AI.moves.remove(move)
    else:
        AI.add_knowledge(GAME.board)
        if len(AI.moves)>0:
            move = AI.moves.pop()

    if AI.goal(GAME.board):
        return redirect(reverse('sudocu:show', args=['SOLUTION!']))

    if AI.lost(GAME.board):
        return redirect(reverse('sudocu:show', args=['DEADEND']))

    if move != None :
        GAME.board[move[0]][move[1]]['value'] = move[2]
        LAST = (move[0],move[1])
    else:
        mode = "AI doesn't know what to do ..."

    return redirect(reverse('sudocu:show', args=[mode]))

def move(request, r, c, v):
    global GAME
    global AI
    global LAST
    LAST = (r, c)
    GAME.board[r][c]['value'] = v
    return redirect(reverse('sudocu:show'))

def save(request, name='sudoku'):
    global GAME
    filename = 'game.sudoku'
    fs = FileSystemStorage()

    if fs.exists(filename) :
        fs.delete(filename)
    fn = os.path.join(settings.MEDIA_ROOT, 'download', filename)

    f = open(fn, 'wb')
    pickle.dump(GAME.board, f) # помещаем объект в файл
    f.close()

    fn = os.path.join(settings.MEDIA_URL, 'download', filename)

    file = {}
    file['url'] = fn
    file['name'] = name + '.sudoku'
    file['title'] = 'Download current sudoku'
    files = []
    files.append(file)

    return render(request, 'utils/download.html', {'title': 'SUDOKU', 'current':'SUDOKU', 'files':files})

def load(request):
    global GAME
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file = request.FILES['file']
        if form.is_valid():
            fs = FileSystemStorage()
            fn = os.path.join(settings.MEDIA_ROOT, 'tmp', file.name)
            if fs.exists(fn) :
                fs.delete(fn)
            filename = fs.save(fn, file)

            f = open(fn, 'rb')
            GAME.board = pickle.load(f) # загружаем объект из файла

            return redirect(reverse('sudocu:show', args=["LET'S PLAY"]))
        else :
            messages.info(request, f'upload error {request.FILES["file"]}', extra_tags='alert-info')
    else:
        form = UploadFileForm()
    return render(request, 'utils/upload.html', {'form': form, 'title':'Upload Sudoku'})


# ______________________________________________________ SUDOCU ________________

class Sudocu():
    """
    Sudocu game representation
    """

    def __init__(self):

        # Set initial width, height
        self.height = Y
        self.width = X

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                cell = {}
                cell['value'] = 0
                cell['hint'] = set()
                cell['hint_color'] = 'w3-white'
                row.append(cell)
            self.board.append(row)

        self.board[0][1]['value']=0
        self.board[0][2]['value']=5
        self.board[0][3]['value']=3
        self.board[0][4]['value']=0
        self.board[0][7]['value']=0

        self.board[1][0]['value']=8
        self.board[1][7]['value']=2
        self.board[1][8]['value']=0

        self.board[2][1]['value']=7
        self.board[2][3]['value']=0
        self.board[2][4]['value']=1
        self.board[2][5]['value']=0
        self.board[2][6]['value']=5
        self.board[2][7]['value']=0

        self.board[3][0]['value']=4
        self.board[3][2]['value']=0
        self.board[3][3]['value']=0
        self.board[3][5]['value']=5
        self.board[3][6]['value']=3

        self.board[4][1]['value']=1
        self.board[4][4]['value']=7
        self.board[4][6]['value']=0
        self.board[4][8]['value']=6

        self.board[5][2]['value']=3
        self.board[5][3]['value']=2
        self.board[5][5]['value']=0
        self.board[5][7]['value']=8

        self.board[6][0]['value']=0
        self.board[6][1]['value']=6
        self.board[6][3]['value']=5
        self.board[6][4]['value']=0
        self.board[6][8]['value']=9

        self.board[7][2]['value']=4
        self.board[7][4]['value']=0
        self.board[7][5]['value']=0
        self.board[7][6]['value']=0
        self.board[7][7]['value']=3

        self.board[8][0]['value']=0
        self.board[8][1]['value']=0
        self.board[8][2]['value']=0
        self.board[8][5]['value']=9
        self.board[8][6]['value']=7
        self.board[8][7]['value']=0

        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j]['value']>0:
                    self.board[i][j]['disabled'] = True
                else:
                    self.board[i][j]['disabled'] = False

    def is_digit(self, cell):
        i, j = cell
        return self.board[i][j]['value']>0

    def won(self):
        """
        Checks if all cells are digits.
        """
        w = True
        for i in range(self.height):
            for j in range(self.width):
                n = self.board[i][j]['value']
                h = self.board[i][j]['hint']
                if n==0:
                    w = False
                    break
                if not (n in h):
                    w = False
                    break
        return w


class SudocuAI():
    """
    game player
    """

    def __init__(self, board, height=Y, width=X):

        # Set initial height and width
        self.height = height
        self.width = width

        self.moves = set()

        self.quadrants = []
        self.quadrants.append(self.quadrant((1,1)))
        self.quadrants.append(self.quadrant((1,4)))
        self.quadrants.append(self.quadrant((1,7)))
        self.quadrants.append(self.quadrant((4,1)))
        self.quadrants.append(self.quadrant((4,4)))
        self.quadrants.append(self.quadrant((4,7)))
        self.quadrants.append(self.quadrant((7,1)))
        self.quadrants.append(self.quadrant((7,4)))
        self.quadrants.append(self.quadrant((7,7)))

        self.rows = []
        for i in range(Y):
            self.rows.append(self.row((i,0)))

        self.columns = []
        for i in range(X):
            self.columns.append(self.column((0,i)))

        self.figures = [self.quadrants, self.rows, self.columns]

        # List of sentences about the game known to be true
        self.knowledge = []

        for i in range(self.height):
            for j in range(self.width):
                hint = self.hint((i,j),board)
                board[i][j]['hint'] = hint

    def empty_cells(self, board):
        s = []
        for i in range(self.height):
            for j in range(self.width):
                if board[i][j]['value']==0:
                    s.append((i,j))
        return s

    def quadrant(self, cell):
        f = set()
        y = cell[0] % 3
        x = cell[1] % 3
        for i in range(3):
            for j in range(3):
                f.add((cell[0] - y + i, cell[1] - x + j))
        return f

    def row(self, cell):
        f = set()
        for i in range(X):
            f.add((cell[0], i))
        return f

    def column(self, cell):
        f = set()
        for i in range(Y):
            f.add((i, cell[1]))
        return f

    def family(self, cell):
        f = set()
        y = cell[0] % 3
        x = cell[1] % 3
        for i in range(3):
            for j in range(3):
                f.add((cell[0] - y + i, cell[1] - x + j))
        for i in range(self.height):
            f.add((i, cell[1]))
        for i in range(self.width):
            f.add((cell[0], i))
        return f

    def hint(self, cell, board):
        """
        Returns available digits
        """
        h = {1,2,3,4,5,6,7,8,9}
        f = self.family(cell)
        for c in f :
            value = board[c[0]][c[1]]['value']
            if (c[0], c[1]) != cell :
                if value>0:
                    if value in h :
                        h.remove(value)
        return h

    def check_hint(self, cell, board):
        """
        Try to reduce available digits
        """
        h = board[cell[0]][cell[1]]['hint']
        f = self.family(cell)
        for c in f :
            n = board[c[0]][c[1]]['value']
            if (c[0], c[1]) != cell :
                if n>0:
                    if n in h :
                        h.remove(n)
        return h

    def try_to_reduce_hints(self, board):
        global GAME
        m=''
        for hint_len in range(2, 3):
            m += f'HL={hint_len} = ['
            for cell in self.empty_cells(board):
                if board[cell[0]][cell[1]]['hint_color']=='w3-green':
                    continue
                h = board[cell[0]][cell[1]]['hint']
                m += f'{cell}'
                # GAME.board[cell[0]][cell[1]]['hint_color'] = 'w3-pale-green'
                if len(h) != hint_len:
                    m += 'N '
                    # GAME.board[cell[0]][cell[1]]['hint_color'] = 'w3-yellow'
                    continue
                m += '!='
                figures = [self.quadrant(cell), self.row(cell), self.column(cell)]
                for f in figures :
                    f.remove(cell)
                    f.intersection_update(self.empty_cells(board))
                    for x in f:
                        m += f'{x}f'
                        # GAME.board[x[0]][x[1]]['hint_color'] = 'w3-green'
                    count = 1
                    for c in f :
                        if h == board[c[0]][c[1]]['hint']:
                            m += f'>{h}={h}'
                            # GAME.board[c[0]][c[1]]['hint_color'] = 'w3-aqua'
                            count += 1
                    m += f'  count={count}  '
                    if count == hint_len :
                        m += 'BINGO '
                        GAME.board[cell[0]][cell[1]]['hint_color'] = 'w3-green'
                        for c in f:
                            if board[c[0]][c[1]]['hint'] != h:
                                m += f'+++{c}'
                                for n in h:
                                    if n in board[c[0]][c[1]]['hint']:
                                        GAME.board[c[0]][c[1]]['hint'].remove(n)
                                        GAME.board[c[0]][c[1]]['hint_color'] = 'w3-red'
                            else:
                                GAME.board[c[0]][c[1]]['hint_color'] = 'w3-green'
                break
        return m

    def good(self,cell, board):
        if board[cell[0]][cell[1]]['value'] in board[cell[0]][cell[1]]['hint'] :
            return True
        return False

    def add_sentence(self, sentence):
        if not (sentence in self.knowledge):
            self.knowledge.append(sentence)
            return True
        return False

    def add_knowledge(self, board):
        """
        """
        moves = self.moves.copy()
        for item in moves:
            if board[item[0]][item[1]]['value'] != 0:
                self.moves.remove(item)

        b = board.copy()
        self.knowledge = []

        for i in range(self.height):
            for j in range(self.width):
                hint = self.check_hint((i,j),b)
                board[i][j]['hint'] = hint

                # if board[i][j]['value']==0:
                #     sentence = Sentence((i,j), hint)
                #     self.add_sentence(sentence)

                # Add obvious moves
                l = list(hint)
                if len(hint)==1 :
                    if board[i][j]['value'] == 0:
                        self.moves.add((i,j,l[0]))

        if len(self.moves)==0:
            self.find_by_figures(board)


    def make_safe_move(self, board):
        move = None
        while len(self.moves)>0 :
            move = list(self.moves)[0]
            if move[2] in board[move[0]][move[1]]['hint']:
                return move
            else:
                self.moves.remove(move)
        return None

    def goal(self, state):
        g = True
        for i in range(9):
            for j in range(9):
                if state[i][j]['value']==0:
                    g = False
        return g

    def legal(self, state):
        g = None
        for i in range(9):
            for j in range(9):
                hint = self.hint((i,j), state)
                n = state[i][j]['value']
                if not (n in hint):
                    if n != 0 :
                        return f"({i},{j})={n}<>{hint}"
        return g

    def lost(self, state):
        g = False
        for i in range(Y):
            for j in range(X):
                if len(state[i][j]['hint'])==0:
                    g = True
        return g

    def find_by_figures(self, board):
        add_moves = set()
        found = False
        ccc = None
        for num in range(1, 10):
            for figure in self.figures:
                for q in figure:
                    count = 0
                    for c in q:
                        c_ok = False
                        if board[c[0]][c[1]]['value'] == 0:
                            if num in board[c[0]][c[1]]['hint']:
                                c_ok = True
                        if c_ok:
                            count += 1
                            ccc = c
                    if count == 1:
                        add_moves.add((ccc[0], ccc[1], num))
                        found = True
                        break
                if found:
                    break
        self.moves = add_moves.union(self.moves)
        return found

# _______________________________________________________ SEARCH _______________

def all_moves(board):
    global GAME
    global AI
    s = set()

    for i in range(Y):
        for j in range(X):
            hint = AI.hint((i,j),board)
            board[i][j]['hint'] = hint
            for n in board[i][j]['hint']:
                s.add((i,j,n))
    return s

class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier():
    def __init__(self):
        self.frontier = []
        # self.explored = [] # added

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

def string(board):
    s=''
    for i in range(Y):
        for j in range(X):
            s += str(board[i][j]['value'])
    return s

def path(request):
    global GAME
    global AI
    global MESSAGE
    explored = []

    m = ''

    path = None

    b = string(GAME.board)
    state = copy.deepcopy(GAME.board)

    initial = Node(state, None, None)
    frontier = StackFrontier()
    frontier.add(initial)

    step = 0 # counts steps
    nodes = 0

    solution = False
    while not solution :
        if frontier.empty() :
            m += f'FAIL BOARD={b}  STEPS={step}  NODES={nodes}'
            MESSAGE = m
            return redirect(reverse('sudocu:show', args=['NONE'])) # HttpResponse(f'{m} FAIL BOARD={b}  STEPS={step}  NODES={nodes}')

        step += 1
        m += f'step {step}  \r\n'

        node = frontier.remove()

        if AI.goal(node.state) and (AI.legal(node.state)==None) :
            solution = True
            break

        st = copy.deepcopy(node.state)
        moves = all_moves(st)
        for move in moves :
            # m += f' state={string(node.state)}  '

            m += f'{move}'

            new_state = copy.deepcopy(node.state)
            new_state[move[0]][move[1]]['value'] = move[2]
            ns = string(new_state)
            resp = AI.legal(new_state)
            if resp != None :
                m += f' IL={resp} '
                continue

            # m += f' new={ns} || EXP=[{explored}] '

            contains = False
            for s in explored:
                if s == ns :
                    contains = True
                    m += f'<<{ns}>>'
                    break

            if contains:
                m += '-- '
                continue

            m += '++ '
            new = Node(new_state, node, move)
            nodes += 1
            frontier.add(new)
            explored.append(ns)
            m += f'FR={len(frontier.frontier)} EX={len(explored)}\r\n'
            if AI.goal(new_state) and (AI.legal(new_state)==None):
                g = string(new_state)
                m += f' GOAL = {g} '
                solution = True
                node = new
                break
    if solution :
        path = []
        current = node
        path.append((current.action[0], current.action[1], current.action[2]))
        while current.parent :
            current = current.parent
            if current.action :
                item = (current.action[0], current.action[1], current.action[2])
                path.append(item)
        path.reverse()

        moves = []

        for i in range(Y):
            for j in range(X):
                if b[i*9+j] == '0' :
                    moves.append((i,j,int(g[i*9+j])))

        AI.moves = moves

    return redirect(reverse('sudocu:show', args=['FOUND'])) # HttpResponse(f'{m} BOARD={b}  PATH={path}  MOVES={moves} STEP={step} NODES={nodes}')

# ______________________________________________ RECURSION _____________________

def recursion(request):
    global GAME
    global MESSAGE

    matrix = board_to_matrix(GAME.board)
    solution = find(matrix)
    if solution in [None, -1, 0] :
        mode = 'DEADEND'
        return redirect(reverse('sudocu:show', args=[mode]))

    moves = []
    for i in range(Y):
        for j in range(X):
            if GAME.board[i][j]['value'] == 0 :
                moves.append((i,j,solution[i][j][0]))
    AI.moves = moves
    MESSAGE = 'Recursion found solution!'
    return redirect(reverse('sudocu:show', args=['FOUND'])) # HttpResponse(f'{m} BOARD={b}  PATH={path}  MOVES={moves} STEP={step} NODES={nodes}')

def quadrant(r,c):
    f = set()
    y = r % 3
    x = c % 3
    for i in range(3):
        for j in range(3):
            f.add((r - y + i, c - x + j))
    return f


def family(r,c):
    f = set()
    y = r % 3
    x = c % 3
    for i in range(3):
        for j in range(3):
            f.add((r - y + i, c - x + j))
    for i in range(9):
        f.add((i, c))
    for i in range(9):
        f.add((r, i))
    f.remove((r,c))
    return f

def m_hint(r,c,m):
    h = {1,2,3,4,5,6,7,8,9}
    f = family(r,c)
    for c in f :
        i = c[0]
        j = c[1]
        n = m[i][j][0]
        if n>0:
            if n in h :
                h.remove(n)
    return h

def status(matrix):
    res = 1
    for i in range(9):
        for j in range(9):
            n = matrix[i][j][0]
            h = m_hint(i,j,matrix)
            if n==0:
                if len(h) == 0:
                    print('status', f'zero hint ({i},{j})={h}')
                    return -1
                res = 0
            elif not (n in h):
                print('status', f'{n} not in ({i},{j})={h}')
                return -1
    return res

def find(matrix):
    res = status(matrix)
    if res < 0 :
        return res
    m = copy.deepcopy(matrix)
    for i in range(9):
        for j in range(9):
            if m[i][j][0]==0: #(matrix[i][j][0]==0 or not matrix[i][j][2]) and len(matrix[i][j][1])>1 :
                for n in range(1, 10):
                    m[i][j][0] = n
                    new = find(m)
                    if new != -1 :
                        return new
                return -1
    return m

def board_to_matrix(board):
    m = []
    for i in range(9):
        row = []
        for j in range(9):
            item =[]
            item.append(board[i][j]['value'])
            item.append(board[i][j]['hint'])
            d = (board[i][j]['value'] != 0)
            item.append(d)
            row.append(item)
        m.append(row)
    return m



