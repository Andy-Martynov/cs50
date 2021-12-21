
# ======================================================= lasker ===============
def lasker(request, obs, config):
    import numpy as np
    import random
    import time

    DELAY = 4.95
    START = time.time()
    FINISH = START + DELAY

    R = 6
    Rp1 = R + 1
    Rm1 = R - 1
    C = 7
    Cp1 = C + 1
    Cm1 = C - 1
    Rp1Cp1 = Rp1 * Cp1

    ################################## heuristic ###############################

    win_score, lost_score = np.inf, -np.inf

    def heuristic(state, mark, depth=0, maximizingPlayer=True):
        depth += 1
        if connected_four(state[mark]):
            return win_score
        if connected_four(state[3-mark]):
            return lost_score

        grid = state_to_grid(state)

        #Convert the grid into a string (default + 90deg rotated + all possible diagonals)
        horizontal_str=str(grid)
        vertical_str=str(grid.transpose())
        diagonal_str=""
        for col in range(0,4):
            for row in range(0,3):
                for i in range(4):
                    diagonal_str+=str(grid[row+i][col+i])+" "
                diagonal_str+=","
            for row in range(3,6):
                for i in range(4):
                    diagonal_str+=str(grid[row-i][col+i])+" "
                diagonal_str+=","

        #Combine all strings into a single one
        combined_str= horizontal_str + vertical_str + diagonal_str

        if mark == 1:
            num_threes =     combined_str.count('1 1 1 0')+combined_str.count('1 1 0 1')+combined_str.count('1 0 1 1')+combined_str.count('0 1 1 1')+combined_str.count('0 0 1 1 0')+combined_str.count('0 1 1 0 0')
            num_threes_opp = combined_str.count('2 2 2 0')+combined_str.count('2 2 0 2')+combined_str.count('2 0 2 2')+combined_str.count('0 2 2 2')+combined_str.count('0 0 2 2 0')+combined_str.count('0 2 2 0 0')
            num_twos =     combined_str.count('1 1 0 0')+combined_str.count('0 1 1 0')+combined_str.count('0 0 1 1')+combined_str.count('1 0 1 0')+combined_str.count('0 1 0 1')+combined_str.count('1 0 0 1')+combined_str.count('0 1 0 0 0')+combined_str.count('0 0 1 0 0')+combined_str.count('0 0 0 1 0')
            num_twos_opp = combined_str.count('2 2 0 0')+combined_str.count('0 2 2 0')+combined_str.count('0 0 2 2')+combined_str.count('2 0 2 0')+combined_str.count('0 2 0 2')+combined_str.count('2 0 0 2')+combined_str.count('0 2 0 0 0')+combined_str.count('0 0 2 0 0')+combined_str.count('0 0 0 2 0')
        else:
            num_threes_opp = combined_str.count('1 1 1 0')+combined_str.count('1 1 0 1')+combined_str.count('1 0 1 1')+combined_str.count('0 1 1 1')+combined_str.count('0 0 1 1 0')+combined_str.count('0 1 1 0 0')
            num_threes =     combined_str.count('2 2 2 0')+combined_str.count('2 2 0 2')+combined_str.count('2 0 2 2')+combined_str.count('0 2 2 2')+combined_str.count('0 0 2 2 0')+combined_str.count('0 2 2 0 0')
            num_twos_opp =   combined_str.count('1 1 0 0')+combined_str.count('0 1 1 0')+combined_str.count('0 0 1 1')+combined_str.count('1 0 1 0')+combined_str.count('0 1 0 1')+combined_str.count('1 0 0 1')+combined_str.count('0 1 0 0 0')+combined_str.count('0 0 1 0 0')+combined_str.count('0 0 0 1 0')
            num_twos =       combined_str.count('2 2 0 0')+combined_str.count('0 2 2 0')+combined_str.count('0 0 2 2')+combined_str.count('2 0 2 0')+combined_str.count('0 2 0 2')+combined_str.count('2 0 0 2')+combined_str.count('0 2 0 0 0')+combined_str.count('0 0 2 0 0')+combined_str.count('0 0 0 2 0')

        score = 900000*num_threes - 900000*num_threes_opp + 30000*num_twos - 30000*num_twos_opp

        num_evens, num_odds = count_even_odd(grid, mark)
        if (maximizingPlayer and even) or (not maximizingPlayer and odd):
            even_odd_rate = num_evens - num_odds
        else:
            even_odd_rate = num_odds - num_evens

        score += 100 * even_odd_rate

        if doublewin(state, mark) : score = 1e8
        if doublewin(state, 3-mark) : score = -1e8

        return score

    ######################################################################################

    def step_number(grid):
        s = 0
        for i in range(R):
            for j in range(C):
                if grid[i][j] == 0:
                    s += 1
        return R*C - s

    def is_odd_player(step):
        # the first is odd
        # grid after move of the player
        return step%2 == 1

    def is_even_player(step):
        # the second is even
        return step%2 == 0

    def count_even_odd(grid, mark):
        odd, even = 0, 0
        for row in range(R):
            for col in range(C):
                if grid[row, col] == mark:
                    if row%2 == 1:
                        odd += 1
                    else:
                        even += 1
        return even, odd

    def doublewin(state, mark):
        win = 0
        for col in valid_moves_list(state):
            n = make_move(state, col, mark)
            if connected_four(n[mark]):
                win += 1
                if win == 2:
                    return True
        return False

    def grid_to_matrix(grid):
        matrix = np.array([0 for i in range(Rp1Cp1)]).reshape(Rp1, Cp1)
        for r in range(R):
            for c in range(C):
                matrix[r+1, c] = grid[r, c]
        return matrix

    def grid_to_state(grid):
        matrix = grid_to_matrix(grid)
        position1, position2 = '', ''
        for c in range(C, -1, -1):
            for r in range(0, Rp1):
                position1 += ['0', '1'][matrix[r,c] == 1]
                position2 += ['0', '1'][matrix[r,c] == 2]
        return {1:int(position1, 2), 2:int(position2, 2)}

    def state_to_grid(state):
        position1 = int_to_bin(state[1])
        position2 = int_to_bin(state[2])
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

    def make_move(state, col, mark):
        mask = state[1] | state[2]
        new_mask = mask | (mask + (1 << (col*7)))
        new_state = state.copy()
        new_state[mark] = state[3-mark] ^ new_mask
        return new_state

    def first_empty_row(state, col):
        m = state[1] | state[2]
        for row in range(6, -1, -1):
            if not (m >> 7*col+6-row) & 1:
                return 6-row

    def connected_four(position):
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

    def vertical_four(position):
        # Vertical
        m = position & (position >> 1)
        if m & (m >> 2): return True
        # Nothing found
        return False

    def int_to_bin(x):
        return bin(x)[2:].zfill(64)

    FULLBOARD = 279258638311359

    # Helper function for minimax: checks if game has ended
    def is_terminal_state(state):
        # Check for draw
        if state[1] | state[2] == FULLBOARD:
            return True
        if connected_four(state[1]):
            return True
        if connected_four(state[2]):
            return True
        return False

    def valid_moves_list(state):
        m = state[1] | state[2]
        return [i for i in [3,2,4,1,5,0,6] if not (m >> 5+7*i) & 1]

    #################################### agent ############################

    # Uses minimax to calculate value of dropping piece in selected column
    def score_move(state, col, mark, nsteps):
        next_state = make_move(state, col, mark)
        return minimax(next_state, nsteps-1, -np.Inf, np.Inf, False, mark)

    # Minimax implementation
    def minimax(node, depth, a, b, maximizingPlayer, mark):

        if time.time() > FINISH:
            return 0

        valid_moves = valid_moves_list(node)
        if depth == 0 or is_terminal_state(node):
            return heuristic(node, mark, depth=depth, maximizingPlayer=maximizingPlayer)

        if maximizingPlayer:
            value = -np.Inf
            for col in valid_moves:
                child = make_move(node, col, mark)
                value = max(value, minimax(child, depth-1, a, b, False, mark))
                a = max(a, value)
                if value >= b:
                    break
            return value
        else:
            value = np.Inf
            for col in valid_moves:
                child = make_move(node, col, 3-mark)
                value = min(value, minimax(child, depth-1, a, b, True, mark))
                b = min(b, value)
                if value <= a:
                    break
            return value

    #########################
    # Agent makes selection #
    #########################

    # Convert the board to a 2D grid
    grid = np.asarray(obs.board).reshape(R, C)

    step = step_number(grid)
    even = is_even_player(step)
    odd = is_odd_player(step)

    # Get list of valid moves
    state = grid_to_state(grid)
    valid_moves = valid_moves_list(state)
    if len(valid_moves) == 1:
        return valid_moves[0]

    for col in valid_moves:
        next_state = make_move(state, col, obs.mark)
        if connected_four(next_state[obs.mark]):
            return col

    # Use the heuristic to assign a score to each possible board in the next step
    N_STEPS = 5
    scores = dict(zip(valid_moves, [score_move(state, col, obs.mark, N_STEPS) for col in valid_moves]))
    while  N_STEPS < 42 - step - 1:

        request.session['depth'] = N_STEPS

        N_STEPS += 1
        scores_2 = dict(zip(valid_moves, [score_move(state, col, obs.mark, N_STEPS) for col in valid_moves]))
        if time.time() > FINISH or np.amax(list(scores_2.values())) <= lost_score:
            break
        scores = scores_2.copy()

    # Get a list of columns (moves) that maximize the heuristic
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]
    # Select the best as nearest to the center of the board from the maximizing columns

    request.session['scores'] = scores

    if len(max_cols) >0:
        col = random.choice(max_cols)
        return col
    col =  random.choice(max_cols)
    return col
# ---------------------------------------------------------- end lasker --------

# ========================================================== alekhin ===========
def alekhin(request, obs, config):
    import numpy as np
    import random
    import time
    import copy

    DELAY = 4.98

    R = 6
    Rp1 = R + 1
    Rm1 = R - 1
    C = 7
    Cp1 = C + 1
    Cm1 = C - 1
    Rp1Cp1 = Rp1 * Cp1

    def step_number(grid):
        s = 0
        for i in range(R):
            for j in range(C):
                if grid[i][j] == 0:
                    s += 1
        return R*C - s

    def is_first_player(step):
        return step%2 == 0

    def int_to_bin(x):
        return bin(x)[2:].zfill(64)

    class State:
        def __init__(self):
            self.pos = dict()

        def valid_moves(self):
            mask = self.pos[1] | self.pos[2]
            return [i for i in [3,2,4,1,5,0,6] if not (mask >> 5+7*i) & 1]

        def from_grid(grid):
            state = State()
            matrix = np.array([0 for i in range(Rp1Cp1)]).reshape(Rp1, Cp1)
            for r in range(R):
                for c in range(C):
                    matrix[r+1, c] = grid[r, c]
            position1, position2 = '', ''
            for c in range(C, -1, -1):
                for r in range(0, Rp1):
                    position1 += ['0', '1'][matrix[r,c] == 1]
                    position2 += ['0', '1'][matrix[r,c] == 2]
            state.pos[1] = int(position1, 2)
            state.pos[2] = int(position2, 2)
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
            mask = self.pos[1] | self.pos[2]
            new_state = State()
            new_mask = mask | (mask + (1 << (col*7)))
            new_state.pos[mark] = self.pos[3-mark] ^ new_mask
            new_state.pos[3-mark] = self.pos[3-mark]
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

        def count23(self, mark):
            n12, n13, n22, n23 = 0, 0, 0, 0
            #vertical
            for col in range(C):
                for row in range(3):
                    w1 = self.pos[mark] >> (col*C+row) & 15
                    w2 = self.pos[3-mark] >> (col*C+row) & 15
                    if not w2:
                        n = 0
                        for i in range(4):
                            if w1 & 1:
                                n += 1
                            w1 >>= 1
                        if n == 2:
                            n12 += 1
                        if n == 3:
                            n13 += 1
                    if not w1:
                        n = 0
                        for i in range(4):
                            if w2 & 1:
                                n += 1
                            w2 >>= 1
                        if n == 2:
                            n22 += 1
                        if n == 3:
                            n23 += 1
            # horizontal
            for row in range(R):
                for col in range(4):
                    n1, n2 = 0, 0
                    for i in range(4):
                        if ((self.pos[mark] >> (col*C+row)) >> 7*i) & 1:
                            n1 += 1
                        if ((self.pos[3-mark] >> (col*C+row)) >> 7*i) & 1:
                            n2 += 1
                    if n2 == 0:
                        if n1 == 2:
                            n12 += 1
                        if n1 == 3:
                            n13 += 1
                    if n1 == 0:
                        if n2 == 2:
                            n22 += 1
                        if n2 == 3:
                            n23 += 1
            #positive diagonal
            for row in range(3):
                for col in range(4):
                    n1, n2 = 0, 0
                    for i in range(4):
                        if (self.pos[mark] >> ((col+i)*C+row+i)) & 1:
                            n1 += 1
                        if (self.pos[3-mark] >> ((col+i)*C+row+i)) & 1:
                            n2 += 1
                    if n2 == 0:
                        if n1 == 2:
                            n12 += 1
                        if n1 == 3:
                            n13 += 1
                    if n1 == 0:
                        if n2 == 2:
                            n22 += 1
                        if n2 == 3:
                            n23 += 1
            #negative diagonal
            for row in range(5, 2, -1):
                for col in range(4):
                    n1, n2 = 0, 0
                    for i in range(4):
                        if (self.pos[mark] >> ((col+i)*C+row-i)) & 1:
                            n1 += 1
                        if (self.pos[3-mark] >> ((col+i)*C+row-i)) & 1:
                            n2 += 1
                    if n2 == 0:
                        if n1 == 2:
                            n12 += 1
                        if n1 == 3:
                            n13 += 1
                    if n1 == 0:
                        if n2 == 2:
                            n22 += 1
                        if n2 == 3:
                            n23 += 1
            return  n12, n13, n22, n23

        def count_even_odd(self, mark):
            odd, even = 0, 0
            for row in range(R):
                rd2 = row%2
                for col in range(C):
                    if (self.pos[mark] >> (7*col+row)) & 1:
                        if rd2 == 0:
                            odd += 1
                        else:
                            even += 1
            return even, odd

        def heuristic(self, mark, maximizingPlayer):

            num_twos, num_threes, num_twos_opp, num_threes_opp = self.count23(mark)
            score = 900000*num_threes - 900000*num_threes_opp + 30000*num_twos - 30000*num_twos_opp

            num_evens, num_odds = self.count_even_odd(mark)
            if first:
                even_odd_rate = num_odds - num_evens
            else:
                even_odd_rate = num_evens - num_odds
            score += 100 * even_odd_rate

            if num_threes > 1:
                if self.doublewin(mark) : score = 1e8
            if num_threes_opp > 1:
                if self.doublewin(3-mark) : score = -1e8
            return score

#         FULLBOARD = 279258638311359

        def score_move(self, col, mark, nsteps):
            next_state = self.make_move(col, mark)
            return minimax(next_state, nsteps-1, -np.Inf, np.Inf, False, mark)

    # Minimax implementation
    def minimax(state, depth, a, b, maximizingPlayer, mark):

        if time.time() > FINISH:
            return 0

        if state.connected_four(mark):
            return np.inf
        if state.connected_four(3-mark):
            return -np.inf
        if state.pos[1] | state.pos[2] == 279258638311359:
            return 0

        if depth == 0:
            move = (state.pos[1], state.pos[2])
            if move in MOVES:
                return MOVES[move]
            h = state.heuristic(mark, maximizingPlayer=maximizingPlayer)
            MOVES[move] = h
            return h

        valid_moves = state.valid_moves()

        if maximizingPlayer:
            value = -np.Inf
            for col in valid_moves:
                child = state.make_move(col, mark)
                value = max(value, minimax(child, depth-1, a, b, False, mark))
                if value >= b:
                    break
                a = max(a, value)
            return value
        else:
            value = np.Inf
            for col in valid_moves:
                child = state.make_move(col, 3-mark)
                value = min(value, minimax(child, depth-1, a, b, True, mark))
                if value <= a:
                    break
                b = min(b, value)
            return value

    START = time.time()
    FINISH = START + DELAY
    MOVES = {}
    N_STEPS = 6

    # Convert the board to a 2D grid
    grid = np.asarray(obs.board).reshape(R, C)

    step = step_number(grid)
    if step < 2:
        return 3

    first = is_first_player(step)

    # Get list of valid moves
    state = State.from_grid(grid)

    valid_moves = state.valid_moves()
    for col in valid_moves:
        next_state = state.make_move(col, obs.mark)
        if next_state.connected_four(obs.mark):
            return col

    # Use the heuristic to assign a score to each possible board in the next step
    scores = dict(zip(valid_moves, [state.score_move(col, obs.mark, N_STEPS) for col in valid_moves]))

    while  N_STEPS < 42 - step:
        N_STEPS += 1

        for vm in valid_moves:
            if scores[vm] == -np.inf:
                valid_moves.remove(vm)
        if len(valid_moves) == 0:
            break

        scores_2 = {}
        win_found = False
        for col in valid_moves:
            score = state.score_move(col, obs.mark, N_STEPS)
            if score == np.inf:
                win_found = True
                return col
            scores_2[col] = score
        if win_found:
            scores = scores_2.copy()
        if time.time() > FINISH or np.amax(list(scores_2.values())) <= -np.inf:
            break
        scores = scores_2.copy()

    # Get a list of columns (moves) that maximize the heuristic
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]

    request.session['depth'] = N_STEPS
    request.session['scores'] = scores

    # Select the best as nearest to the center of the board from the maximizing columns
    if len(max_cols) >0:
        if 3 in max_cols:
            return 3
        if 2 in max_cols and 4 in max_cols:
            return random.choice([2, 4])
        if 2 in max_cols:
            return 2
        if 4 in max_cols:
            return 4

        if 1 in max_cols and 5 in max_cols:
            return random.choice([1, 5])
        if 1 in max_cols:
            return 1
        if 5 in max_cols:
            return 5

        if 0 in max_cols and 6 in max_cols:
            return random.choice([0, 6])
        if 0 in max_cols:
            return 0
        if 6 in max_cols:
            return 6

        col = random.choice(max_cols)
        return col
    col =  random.choice(max_cols)
    return col
# --------------------------------------------------------- end alekhin --------

    # request.session['depth'] = N_STEPS
    # request.session['scores'] = scores


# ========================================================= smyslov ============

def smyslov(request, obs, config):
    import numpy as np
    import random
    import time
    import copy

    DELAY = 4.98
    START = time.time()
    FINISH = START + DELAY

    R = 6
    Rp1 = R + 1
    Rm1 = R - 1
    C = 7
    Cp1 = C + 1
    Cm1 = C - 1
    Rp1Cp1 = Rp1 * Cp1

    def step_number(grid):
        s = 0
        for i in range(R):
            for j in range(C):
                if grid[i][j] == 0:
                    s += 1
        return R*C - s

    def is_odd_player(step):
        # the first is odd
        # grid after move of the player
        return step%2 == 1

    def is_even_player(step):
        # the second is even
        return step%2 == 0

    def int_to_bin(x):
        return bin(x)[2:].zfill(64)

    def count_even_odd(grid, mark):
        odd, even = 0, 0
        for row in range(R):
            rd2 = row%2
            for col in range(C):
                if grid[row, col] == mark:
                    if rd2 == 1:
                        odd += 1
                    else:
                        even += 1
        return even, odd

########### Class State ########################################################

    class State:
        def __init__(self):
            self.pos = dict()
            self.mask = 0

        def valid_moves(self):
            return [i for i in [3,2,4,1,5,0,6] if not (self.mask >> 5+7*i) & 1]

        def from_grid(grid):
            state = State()
            matrix = np.array([0 for i in range(Rp1Cp1)]).reshape(Rp1, Cp1)
            for r in range(R):
                for c in range(C):
                    matrix[r+1, c] = grid[r, c]
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

        def heuristic(self, mark, maximizingPlayer):
            grid = self.to_grid()
            #Convert the grid into a string (default + 90deg rotated + all possible diagonals)
            horizontal_str=str(grid)
            vertical_str=str(grid.transpose())
            diagonal_str=""
            for col in range(0,4):
                for row in range(0,3):
                    for i in range(4):
                        diagonal_str+=str(grid[row+i][col+i])+" "
                    diagonal_str+=","
                for row in range(3,6):
                    for i in range(4):
                        diagonal_str+=str(grid[row-i][col+i])+" "
                    diagonal_str+=","
            #Combine all strings into a single one
            combined_str = horizontal_str + vertical_str + diagonal_str
            if mark == 1:
                num_threes =     combined_str.count('1 1 1 0')+combined_str.count('1 1 0 1')+combined_str.count('1 0 1 1')+combined_str.count('0 1 1 1')+combined_str.count('0 0 1 1 0')+combined_str.count('0 1 1 0 0')
                num_threes_opp = combined_str.count('2 2 2 0')+combined_str.count('2 2 0 2')+combined_str.count('2 0 2 2')+combined_str.count('0 2 2 2')+combined_str.count('0 0 2 2 0')+combined_str.count('0 2 2 0 0')
                num_twos =     combined_str.count('1 1 0 0')+combined_str.count('0 1 1 0')+combined_str.count('0 0 1 1')+combined_str.count('1 0 1 0')+combined_str.count('0 1 0 1')+combined_str.count('1 0 0 1')+combined_str.count('0 1 0 0 0')+combined_str.count('0 0 1 0 0')+combined_str.count('0 0 0 1 0')
                num_twos_opp = combined_str.count('2 2 0 0')+combined_str.count('0 2 2 0')+combined_str.count('0 0 2 2')+combined_str.count('2 0 2 0')+combined_str.count('0 2 0 2')+combined_str.count('2 0 0 2')+combined_str.count('0 2 0 0 0')+combined_str.count('0 0 2 0 0')+combined_str.count('0 0 0 2 0')
            else:
                num_threes_opp = combined_str.count('1 1 1 0')+combined_str.count('1 1 0 1')+combined_str.count('1 0 1 1')+combined_str.count('0 1 1 1')+combined_str.count('0 0 1 1 0')+combined_str.count('0 1 1 0 0')
                num_threes =     combined_str.count('2 2 2 0')+combined_str.count('2 2 0 2')+combined_str.count('2 0 2 2')+combined_str.count('0 2 2 2')+combined_str.count('0 0 2 2 0')+combined_str.count('0 2 2 0 0')
                num_twos_opp =   combined_str.count('1 1 0 0')+combined_str.count('0 1 1 0')+combined_str.count('0 0 1 1')+combined_str.count('1 0 1 0')+combined_str.count('0 1 0 1')+combined_str.count('1 0 0 1')+combined_str.count('0 1 0 0 0')+combined_str.count('0 0 1 0 0')+combined_str.count('0 0 0 1 0')
                num_twos =       combined_str.count('2 2 0 0')+combined_str.count('0 2 2 0')+combined_str.count('0 0 2 2')+combined_str.count('2 0 2 0')+combined_str.count('0 2 0 2')+combined_str.count('2 0 0 2')+combined_str.count('0 2 0 0 0')+combined_str.count('0 0 2 0 0')+combined_str.count('0 0 0 2 0')
            score = 900000*num_threes - 900000*num_threes_opp + 30000*num_twos - 30000*num_twos_opp

            num_evens, num_odds = count_even_odd(grid, mark)
            if (maximizingPlayer and even) or (not maximizingPlayer and odd):
                even_odd_rate = num_evens - num_odds
            else:
                even_odd_rate = num_odds - num_evens
            score += 100 * even_odd_rate

            if num_threes > 1:
                if self.doublewin(mark) : score = 1e8
            if num_threes_opp > 1:
                if self.doublewin(3-mark) : score = -1e8
            return score

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

        def score_move(self, col, mark, nsteps):
            next_state = self.make_move(col, mark)
            return minimax(next_state, nsteps-1, -np.Inf, np.Inf, False, mark)

    #################################### agent ############################

    # Minimax implementation
    def minimax(state, depth, a, b, maximizingPlayer, mark):

        if time.time() > FINISH:
            return 0

        if state.connected_four(mark):
            return np.inf
        if state.connected_four(3-mark):
            return -np.inf
        if state.mask == 279258638311359:
            return 0

        if depth == 0:
            move = (state.pos[1], state.pos[2])
            if move in MOVES:
                return MOVES[move]
            h = state.heuristic(mark, maximizingPlayer=maximizingPlayer)
            MOVES[move] = h
            return h

        valid_moves = state.valid_moves()

        if maximizingPlayer:
            value = -np.Inf
            for col in valid_moves:
                child = state.make_move(col, mark)
                value = max(value, minimax(child, depth-1, a, b, False, mark))
                if value >= b:
                    break
                a = max(a, value)
            return value
        else:
            value = np.Inf
            for col in valid_moves:
                child = state.make_move(col, 3-mark)
                value = min(value, minimax(child, depth-1, a, b, True, mark))
                if value <= a:
                    break
                b = min(b, value)
            return value

    #########################
    # Agent makes selection #
    #########################

    START = time.time()
    FINISH = START + DELAY
    MOVES = {}
    N_STEPS = 6

    # Convert the board to a 2D grid
    grid = np.asarray(obs.board).reshape(R, C)

    step = step_number(grid)
    if step < 2:
        return 3

    even = is_even_player(step)
    odd = is_odd_player(step)

    # Get list of valid moves
    state = State.from_grid(grid)

    valid_moves = state.valid_moves()
    for col in valid_moves:
        next_state = state.make_move(col, obs.mark)
        if next_state.connected_four(obs.mark):
            return col

    # Use the heuristic to assign a score to each possible board in the next step
    scores = dict(zip(valid_moves, [state.score_move(col, obs.mark, N_STEPS) for col in valid_moves]))

    while  N_STEPS < 42 - step:

        request.session['depth'] = N_STEPS

        N_STEPS += 1
#         MOVES = {}



        for vm in valid_moves:
            if scores[vm] == -np.inf:
                valid_moves.remove(vm)
        if len(valid_moves) == 0:
            break

        scores_2 = {}
        win_found = False
        for col in valid_moves:
            score = state.score_move(col, obs.mark, N_STEPS)
            if score == np.inf:
                win_found = True
                return col
            scores_2[col] = score

        if win_found:

            request.session['depth'] = N_STEPS

            scores = scores_2.copy()

        if time.time() > FINISH or np.amax(list(scores_2.values())) <= -np.inf:
            break
        scores = scores_2.copy()

    # Get a list of columns (moves) that maximize the heuristic
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]
    # Select the best as nearest to the center of the board from the maximizing columns

    request.session['scores'] = scores

    if len(max_cols) >0:
        if 3 in max_cols:
            return 3
        if 2 in max_cols and 4 in max_cols:
            return random.choice([2, 4])
        if 2 in max_cols:
            return 2
        if 4 in max_cols:
            return 4

        if 1 in max_cols and 5 in max_cols:
            return random.choice([1, 5])
        if 1 in max_cols:
            return 1
        if 5 in max_cols:
            return 5

        if 0 in max_cols and 6 in max_cols:
            return random.choice([0, 6])
        if 0 in max_cols:
            return 0
        if 6 in max_cols:
            return 6

        col = random.choice(max_cols)
        return col
    col =  random.choice(max_cols)
    return col
# -------------------------------------------------------- end smyslov ---------

# ======================================================== botvinnik ===========
def botvinnik(request, obs, config):
    import numpy as np
    import random
    import time

    DELAY = 4.95
    R = 6
    Rp1 = R + 1
    Rm1 = R - 1
    C = 7
    Cp1 = C + 1
    Cm1 = C - 1
    Rp1Cp1 = Rp1 * Cp1

    ################################## heuristic ###############################

    def heuristic(state, mark, depth=0, maximizingPlayer=True):
        grid = state_to_grid(state)
        #Convert the grid into a string (default + 90deg rotated + all possible diagonals)
        horizontal_str=str(grid)
        vertical_str=str(grid.transpose())
        diagonal_str=""
        for col in range(0,4):
            for row in range(0,3):
                for i in range(4):
                    diagonal_str+=str(grid[row+i][col+i])+" "
                diagonal_str+=","
            for row in range(3,6):
                for i in range(4):
                    diagonal_str+=str(grid[row-i][col+i])+" "
                diagonal_str+=","

        #Combine all strings into a single one
        combined_str= horizontal_str + vertical_str + diagonal_str

        if mark == 1:
            num_threes =     combined_str.count('1 1 1 0')+combined_str.count('1 1 0 1')+combined_str.count('1 0 1 1')+combined_str.count('0 1 1 1')#+combined_str.count('0 0 1 1 0')+combined_str.count('0 1 1 0 0')
            num_threes_opp = combined_str.count('2 2 2 0')+combined_str.count('2 2 0 2')+combined_str.count('2 0 2 2')+combined_str.count('0 2 2 2')#+combined_str.count('0 0 2 2 0')+combined_str.count('0 2 2 0 0')
            num_twos =     combined_str.count('1 1 0 0')+combined_str.count('0 1 1 0')+combined_str.count('0 0 1 1')+combined_str.count('1 0 1 0')+combined_str.count('0 1 0 1')+combined_str.count('1 0 0 1')#+combined_str.count('0 1 0 0 0')+combined_str.count('0 0 1 0 0')+combined_str.count('0 0 0 1 0')
#             num_twos_opp = combined_str.count('2 2 0 0')+combined_str.count('0 2 2 0')+combined_str.count('0 0 2 2')+combined_str.count('2 0 2 0')+combined_str.count('0 2 0 2')+combined_str.count('2 0 0 2')+combined_str.count('0 2 0 0 0')+combined_str.count('0 0 2 0 0')+combined_str.count('0 0 0 2 0')
        else:
            num_threes_opp = combined_str.count('1 1 1 0')+combined_str.count('1 1 0 1')+combined_str.count('1 0 1 1')+combined_str.count('0 1 1 1')#+combined_str.count('0 0 1 1 0')+combined_str.count('0 1 1 0 0')
            num_threes =     combined_str.count('2 2 2 0')+combined_str.count('2 2 0 2')+combined_str.count('2 0 2 2')+combined_str.count('0 2 2 2')#+combined_str.count('0 0 2 2 0')+combined_str.count('0 2 2 0 0')
#             num_twos_opp =   combined_str.count('1 1 0 0')+combined_str.count('0 1 1 0')+combined_str.count('0 0 1 1')+combined_str.count('1 0 1 0')+combined_str.count('0 1 0 1')+combined_str.count('1 0 0 1')+combined_str.count('0 1 0 0 0')+combined_str.count('0 0 1 0 0')+combined_str.count('0 0 0 1 0')
            num_twos =       combined_str.count('2 2 0 0')+combined_str.count('0 2 2 0')+combined_str.count('0 0 2 2')+combined_str.count('2 0 2 0')+combined_str.count('0 2 0 2')+combined_str.count('2 0 0 2')#+combined_str.count('0 2 0 0 0')+combined_str.count('0 0 2 0 0')+combined_str.count('0 0 0 2 0')

        score = ((num_threes - num_threes_opp) << 7) + (num_twos << 3) # - 30000*num_twos_opp
#         score = 900000*num_threes + 30000*num_twos

        num_evens, num_odds = count_even_odd(grid, mark)
        if (maximizingPlayer and even) or (not maximizingPlayer and odd):
            even_odd_rate = num_evens - num_odds
        else:
            even_odd_rate = num_odds - num_evens

        score += even_odd_rate

        if num_threes > 1:
            if doublewin(state, mark) : score = 1e8
        if num_threes_opp > 1:
            if doublewin(state, 3-mark) : score = -1e8

        return score

    ######################################################################################

    def step_number(grid):
        s = 0
        for i in range(R):
            for j in range(C):
                if grid[i][j] == 0:
                    s += 1
        return R*C - s

    def is_odd_player(step):
        # the first is odd
        # grid after move of the player
        return step%2 == 1

    def is_even_player(step):
        # the second is even
        return step%2 == 0

    def count_even_odd(grid, mark):
        odd, even = 0, 0
        for row in range(R):
            rd2 = row%2
            for col in range(C):
                if grid[row, col] == mark:
                    if rd2 == 1:
                        odd += 1
                    else:
                        even += 1
        return even, odd

    def doublewin(state, mark):
        win = 0
        for col in valid_moves_list(state):
            n = make_move(state, col, mark)
            if connected_four(n[mark]):
                win += 1
                if win == 2:
                    return True
        return False

    def grid_to_matrix(grid):
        matrix = np.array([0 for i in range(Rp1Cp1)]).reshape(Rp1, Cp1)
        for r in range(R):
            for c in range(C):
                matrix[r+1, c] = grid[r, c]
        return matrix

    def grid_to_state(grid):
        matrix = grid_to_matrix(grid)
        position1, position2 = '', ''
        for c in range(C, -1, -1):
            for r in range(0, Rp1):
                position1 += ['0', '1'][matrix[r,c] == 1]
                position2 += ['0', '1'][matrix[r,c] == 2]
        return {1:int(position1, 2), 2:int(position2, 2)}

    def state_to_grid(state):
        position1 = state[1]
        position2 = state[2]
        matrix = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0]])
        for c in range(0, Cp1):
            for r in range(R, -1, -1):
                if position1 & 1:
                    matrix[r,c] = 1
                position1 = position1 >> 1
                if position2 & 1:
                    matrix[r,c] = 2
                position2 = position2 >> 1
        return matrix[1:, :-1]

    def make_move(state, col, mark):
        mask = state[1] | state[2]
        new_mask = mask | (mask + (1 << (col*7)))
        new_state = state.copy()
        new_state[mark] = state[3-mark] ^ new_mask
        return new_state

    def first_empty_row(state, col):
        m = state[1] | state[2]
        for row in range(6, -1, -1):
            if not (m >> 7*col+6-row) & 1:
                return 6-row

    def connected_four(position):
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

    def vertical_four(position):
        # Vertical
        m = position & (position >> 1)
        if m & (m >> 2): return True
        # Nothing found
        return False

    def int_to_bin(x):
        return bin(x)[2:].zfill(64)

#     FULLBOARD = 279258638311359

    def valid_moves_list(state):
        m = state[1] | state[2]
        return [i for i in [3,2,4,1,5,0,6] if not (m >> 5+7*i) & 1]

    #################################### agent ############################
    N_STEPS = 6

    # Uses minimax to calculate value of dropping piece in selected column
    def score_move(state, col, mark, nsteps):
        next_state = make_move(state, col, mark)
        return minimax(next_state, nsteps-1, -np.Inf, np.Inf, False, mark)

    # Minimax implementation
    def minimax(state, depth, a, b, maximizingPlayer, mark):

        if time.time() > FINISH:
            return 0

        if connected_four(state[mark]):
            return np.inf
        if connected_four(state[3-mark]):
            return -np.inf
        if state[1] | state[2] == 279258638311359:
            return 0

        if depth == 0:
            move = (state[1], state[2])
            if move in MOVES:
                return MOVES[move]
            h = heuristic(state, mark, depth=depth, maximizingPlayer=maximizingPlayer)
            MOVES[move] = h
            return h

        valid_moves = valid_moves_list(state)

        if maximizingPlayer:
            value = -np.Inf
            for col in valid_moves:
                child = make_move(state, col, mark)
                value = max(value, minimax(child, depth-1, a, b, False, mark))
                if value >= b:
                    break
                a = max(a, value)
            return value
        else:
            value = np.Inf
            for col in valid_moves:
                child = make_move(state, col, 3-mark)
                value = min(value, minimax(child, depth-1, a, b, True, mark))
                if value <= a:
                    break
                b = min(b, value)
            return value

    #########################
    # Agent makes selection #
    #########################

    START = time.time()
    FINISH = START + DELAY
    MOVES = {}

    # Convert the board to a 2D grid
    grid = np.asarray(obs.board).reshape(R, C)

    step = step_number(grid)
    if step < 2:
        return 3

    even = is_even_player(step)
    odd = is_odd_player(step)

    # Get list of valid moves
    state = grid_to_state(grid)
    valid_moves = valid_moves_list(state)
    for col in valid_moves:
        next_state = make_move(state, col, obs.mark)
        if connected_four(next_state[obs.mark]):
            return col

    # Use the heuristic to assign a score to each possible board in the next step
    scores = dict(zip(valid_moves, [score_move(state, col, obs.mark, N_STEPS) for col in valid_moves]))

    if time.time() > FINISH:
        N_STEPS = 2
        FINISH += 0.045
        scores = dict(zip(valid_moves, [score_move(state, col, obs.mark, N_STEPS) for col in valid_moves]))
    while  N_STEPS < 42 - step: # - 1:

        request.session['depth'] = N_STEPS

        N_STEPS += 1
        scores_2 = dict(zip(valid_moves, [score_move(state, col, obs.mark, N_STEPS) for col in valid_moves]))
        if time.time() > FINISH or np.amax(list(scores_2.values())) <= -np.inf:
            break
        scores = scores_2.copy()

    # Get a list of columns (moves) that maximize the heuristic
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]

    request.session['scores'] = scores

    # Select the best as nearest to the center of the board from the maximizing columns

    if len(max_cols) >0:
        if 3 in max_cols:
            return 3
        if 2 in max_cols and 4 in max_cols:
            return random.choice([2, 4])
        if 2 in max_cols:
            return 2
        if 4 in max_cols:
            return 4

        if 1 in max_cols and 5 in max_cols:
            return random.choice([1, 5])
        if 1 in max_cols:
            return 1
        if 5 in max_cols:
            return 5

        if 0 in max_cols and 6 in max_cols:
            return random.choice([0, 6])
        if 0 in max_cols:
            return 0
        if 6 in max_cols:
            return 6

        col = random.choice(max_cols)
        return col
    col =  random.choice(max_cols)
    return col
# --------------------------------------------------------- end botvinnik ------


# ============================================= capablanca aka negamax =========
def capablanca(request, obs, config):
    columns = config.columns
    rows = config.rows
    size = rows * columns

    import numpy as np
    import random
    import time
    import copy

    DELAY = 4.97
    START = time.time()
    FINISH = START + DELAY
    EMPTY = 0

    R = 6
    Rp1 = R + 1
    Rm1 = R - 1
    C = 7
    Cp1 = C + 1
    Cm1 = C - 1
    Rp1Cp1 = Rp1 * Cp1

    def is_first_player(moves_made):
        # the second is even
        return moves_made%2 == 0

    def int_to_bin(x):
        return bin(x)[2:].zfill(64)

    def count_even_odd(grid, mark):
        odd, even = 0, 0
        for row in range(R):
            rd2 = row%2
            for col in range(C):
                if grid[row, col] == mark:
                    if rd2 == 1:
                        odd += 1
                    else:
                        even += 1
        return even, odd

############################## Class State #####################################

    class State:
        def __init__(self):
            self.pos = dict()
            self.mask = 0

        def valid_moves(self):
            return [i for i in MOVES if not (self.mask >> 5+7*i) & 1]

        def from_grid(grid):
            state = State()
            matrix = np.array([0 for i in range(Rp1Cp1)]).reshape(Rp1, Cp1)
            for r in range(R):
                for c in range(C):
                    matrix[r+1, c] = grid[r, c]
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

        def heuristic(self, mark):
            if self.connected_four(mark):
                return np.inf
            if self.connected_four(3-mark):
                return -np.inf
            if self.mask == 279258638311359:
                return 0

            grid = self.to_grid()
            #Convert the grid into a string (default + 90deg rotated + all possible diagonals)
            horizontal_str=str(grid)
            vertical_str=str(grid.transpose())
            diagonal_str=""
            for col in range(0,4):
                for row in range(0,3):
                    for i in range(4):
                        diagonal_str+=str(grid[row+i][col+i])+" "
                    diagonal_str+=","
                for row in range(3,6):
                    for i in range(4):
                        diagonal_str+=str(grid[row-i][col+i])+" "
                    diagonal_str+=","
            #Combine all strings into a single one
            combined_str = horizontal_str + vertical_str + diagonal_str
            if mark == 1:
                num_threes =     combined_str.count('1 1 1 0')+combined_str.count('1 1 0 1')+combined_str.count('1 0 1 1')+combined_str.count('0 1 1 1')+combined_str.count('0 0 1 1 0')+combined_str.count('0 1 1 0 0')
                num_threes_opp = combined_str.count('2 2 2 0')+combined_str.count('2 2 0 2')+combined_str.count('2 0 2 2')+combined_str.count('0 2 2 2')+combined_str.count('0 0 2 2 0')+combined_str.count('0 2 2 0 0')
                num_twos =     combined_str.count('1 1 0 0')+combined_str.count('0 1 1 0')+combined_str.count('0 0 1 1')+combined_str.count('1 0 1 0')+combined_str.count('0 1 0 1')+combined_str.count('1 0 0 1')+combined_str.count('0 1 0 0 0')+combined_str.count('0 0 1 0 0')+combined_str.count('0 0 0 1 0')
#                 num_twos_opp = combined_str.count('2 2 0 0')+combined_str.count('0 2 2 0')+combined_str.count('0 0 2 2')+combined_str.count('2 0 2 0')+combined_str.count('0 2 0 2')+combined_str.count('2 0 0 2')+combined_str.count('0 2 0 0 0')+combined_str.count('0 0 2 0 0')+combined_str.count('0 0 0 2 0')
            else:
                num_threes_opp = combined_str.count('1 1 1 0')+combined_str.count('1 1 0 1')+combined_str.count('1 0 1 1')+combined_str.count('0 1 1 1')+combined_str.count('0 0 1 1 0')+combined_str.count('0 1 1 0 0')
                num_threes =     combined_str.count('2 2 2 0')+combined_str.count('2 2 0 2')+combined_str.count('2 0 2 2')+combined_str.count('0 2 2 2')+combined_str.count('0 0 2 2 0')+combined_str.count('0 2 2 0 0')
#                 num_twos_opp =   combined_str.count('1 1 0 0')+combined_str.count('0 1 1 0')+combined_str.count('0 0 1 1')+combined_str.count('1 0 1 0')+combined_str.count('0 1 0 1')+combined_str.count('1 0 0 1')+combined_str.count('0 1 0 0 0')+combined_str.count('0 0 1 0 0')+combined_str.count('0 0 0 1 0')
                num_twos =       combined_str.count('2 2 0 0')+combined_str.count('0 2 2 0')+combined_str.count('0 0 2 2')+combined_str.count('2 0 2 0')+combined_str.count('0 2 0 2')+combined_str.count('2 0 0 2')+combined_str.count('0 2 0 0 0')+combined_str.count('0 0 2 0 0')+combined_str.count('0 0 0 2 0')
            score = 900000*num_threes - 900000*num_threes_opp + 30000*num_twos # - 30000*num_twos_opp

            if num_threes > 1:
                if self.doublewin(mark) : score = 1e8
            if num_threes_opp > 1:
                if self.doublewin(3-mark) : score = -1e8
            return score

        def fast_heuristic(self, mark):
            if self.connected_four(mark):
                return np.inf
            if self.connected_four(3-mark):
                return -np.inf
            if self.mask == 279258638311359:
                return 0.5
            if self.doublewin(mark):
                return 1
            if self.doublewin(3-mark):
                return -1
            return 0

        def fastest_heuristic(self, mark):
            if self.connected_four(mark):
                return np.inf
            if self.connected_four(3-mark):
                return -np.inf
            if self.mask == 279258638311359:
                return 1
            return 0

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

        def score_move(self, col, mark, nsteps):
            next_state = self.make_move(col, mark)
            return negamax(next_state, nsteps-1, -np.Inf, np.Inf, mark, 1)

        def moves(self):
            s = int_to_bin(self.mask)
            return s.count("1")

        def zero(self, row, col):
            cell = 1 << (col * C + Rm1 - row)
            return cell & self.mask == 0

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

        def native_heuristic(self, column, moves, mark):
            '''
            Score based on cell proximity for a clustering effect.
            '''
            row = self.empty_row(column)
            score = (size + 1 - moves) / 2
            if column > 0 and self.value(row, column - 1) == mark:
                score += 1
            if (column < columns - 1  and self.value(row, column + 1) == mark):
                score += 1
            if row > 0 and self.value(row - 1, column) == mark:
                score += 1
            if row < rows - 2 and self.value(row + 1, column) == mark:
                score += 1
            return score

    ########################### Transposition table ######################################

    class Entry:
        def __init__(self):
            self.value = None
            self.flag = None
            self.depth = None

    class Ttable:
        def __init__(self):
            self.table = dict()

        def store(self, state, entry):
            key = (state.pos[1], state.pos[2])
            self.table[key] = entry

        def lookup(self, state):
            key = (state.pos[1], state.pos[2])
            if key in self.table:
                return self.table[key]
            return None

        def reset(self):
            self.table = dict()

    ########################### Negamax ##################################################

    # Due to compute/time constraints the tree depth must be limited.
    max_depth = 6

    ttable = Ttable()
    EXACT = 0
    LOWERBOUND = -1
    UPPERBOUND = 1

    NORMAL = 0
    FAST = 1
    FASTEST = 2
    MODE = NORMAL

    MOVES = [3, 2, 4, 5, 1, 0, 6]

    def negamax(state, mark, depth, a, b):
        if time.time() > FINISH:
            return ({}, 0, None)
        aorig = a
        entry = ttable.lookup(state)
        if entry:
            if entry.depth >= depth:
                if entry.flag == EXACT:
                    return ({}, entry.value, None)
                elif entry.flag == LOWERBOUND:
                    a = max(a, entry.value)
                elif entry.flag == UPPERBOUND:
                    b = min(b, entry.value)
                if a >= b:
                    return ({}, entry.value, None)

        scores = {}

        # Tie Game
        if state.mask == 279258638311359: #moves == size:
            return (scores, 0, None)

        valid_moves = state.valid_moves()
        # Can win next.
        for column in valid_moves:
            if state.make_move(column, mark).connected_four(mark):
                win = np.inf # (size + 1 - moves_made) / 2
                scores[column] = win
                return (scores, win, column)

        # Recursively check all columns.
        best_score = -np.inf #-size
        best_column = None
        for column in valid_moves:
            # Max depth reached.
            if depth <= 0:
                if MODE == NORMAL:
                    score = state.heuristic(mark)
                elif MODE == FAST:
                    score = state.fast_heuristic(mark)
                elif MODE == FASTEST:
                    score = state.fastest_heuristic(mark)
            else:
                next_state = state.make_move(column, mark)
                (_, score, _) = negamax(next_state, 3-mark, depth - 1, -b, -a)
                score = score * -1
                a = max(a, score)
            scores[column] = score
            if score > best_score:
                best_score = score
                best_column = column
            if a >= b:
                break

        entry = Entry()
        entry.value = best_score
        if best_score <= aorig:
            entry.flag = UPPERBOUND
        elif best_score >= b:
            entry.flag = LOWERBOUND
        else:
            entry.flag = EXACT
        entry.depth = depth
        ttable.store(state, entry)

        return (scores, best_score, best_column)

    # Convert the board to a 2D grid

    grid = np.asarray(obs.board).reshape(R, C)
    state = State.from_grid(grid)
    moves_made = state.moves()
    if moves_made < 2:
        return 3
    if moves_made < 4:
        max_depth = 4
    if moves_made < 8:
        max_depth = 5

    if moves_made % 2 == 0: # first player
        if moves_made >= 18:
            MODE = FAST
            max_depth = 12
    else:
        if moves_made >= 17:
            MODE = FASTEST
            max_depth = 12

    # first iteration
    scores, best_score, column = negamax(state, obs.mark, max_depth, -np.inf, np.inf)

    while  max_depth < 42 - moves_made:

        request.session['depth'] = max_depth

        for move in scores:
            if scores[move] == -np.inf:
                MOVES.remove(move)
        if len(MOVES) < 2:
            break

        max_depth += 1
        scores2, best_score2, column2 = negamax(state, obs.mark, max_depth, -np.inf, np.inf)
        if time.time() > FINISH or column2 == None: # or np.amax(list(scores_2.values())) <= -np.inf:
            break
        scores = scores2.copy()
        best_score = best_score2
        column = column2

    request.session['scores'] = scores

    if column == None:
        column = random.choice([c for c in range(columns) if obs.board[c] == EMPTY])
    return column
# -------------------------------------------------------- end capablanca ------


#___________________________________________________________ PETROSYAN _________
def petrosyan(request, obs, config):
    import numpy as np
    import random
    import time

    DELAY = 4.95
    R = 6
    Rp1 = R + 1
    Rm1 = R - 1
    C = 7
    Cp1 = C + 1
    Cm1 = C - 1
    Rp1Cp1 = Rp1 * Cp1

    def int_to_bin(x):
        return bin(x)[2:].zfill(64)

    def step_number(grid):
        s = 0
        for i in range(R):
            for j in range(C):
                if grid[i][j] == 0:
                    s += 1
        return R*C - s

    def is_odd_player(step):
        # the first is odd
        # grid after move of the player
        return step%2 == 1

    def is_even_player(step):
        # the second is even
        return step%2 == 0

############################## Class State ########################################################

    class State:
        def __init__(self):
            self.pos = dict()
            self.mask = 0

        def step(self):
            mask, count = self.mask, 0
            while mask:
                count += 1
                mask &= mask - 1
            return count

        def count_even_odd(self, mark):
            odd, even = 0, 0
            for row in range(R):
                rd2 = row%2
                for col in range(C):
                    if (self.pos[mark] >> (7*col+row)) & 1:
                        if rd2 == 0:
                            odd += 1
                        else:
                            even += 1
            return even, odd

        def heuristic(self, mark, depth=0, maximizingPlayer=True):
            num_twos, num_threes, num_twos_opp, num_threes_opp = self.num23(mark)
            score = ((num_threes - num_threes_opp) << 7) + (num_twos << 3) # - 30000*num_twos_opp

            num_evens, num_odds = self.count_even_odd(mark)
            if (maximizingPlayer and even) or (not maximizingPlayer and odd):
                even_odd_rate = num_evens - num_odds
            else:
                even_odd_rate = num_odds - num_evens

            score += even_odd_rate

            if num_threes > 1:
                if self.doublewin(mark) : score = 1e8
            if num_threes_opp > 1:
                if self.doublewin(3-mark) : score = -1e8
            return score

        def valid_moves(self):
            return [i for i in [3,2,4,1,5,0,6] if not (self.mask >> 5+7*i) & 1]

        def from_grid(grid):
            state = State()
            matrix = np.array([0 for i in range(Rp1Cp1)]).reshape(Rp1, Cp1)
            for r in range(R):
                for c in range(C):
                    matrix[r+1, c] = grid[r, c]
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

        def moves(self):
            s = int_to_bin(self.mask)
            return s.count("1")

        def zero(self, row, col):
            cell = 1 << (col * C + Rm1 - row)
            return cell & self.mask == 0

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

        def num23(self, mark):
            n12, n13, n22, n23 = 0, 0, 0, 0
            #vertical
            for col in range(C):
                for row in range(3):
                    w1 = self.pos[mark] >> (col*C+row) & 15
                    w2 = self.pos[3-mark] >> (col*C+row) & 15
                    if not w2:
                        n = 0
                        for i in range(4):
                            if w1 & 1:
                                n += 1
                            w1 >>= 1
                        if n == 2:
                            n12 += 1
                        if n == 3:
                            n13 += 1
                    if not w1:
                        n = 0
                        for i in range(4):
                            if w2 & 1:
                                n += 1
                            w2 >>= 1
                        if n == 2:
                            n22 += 1
                        if n == 3:
                            n23 += 1
            # horizontal
            for row in range(R):
                for col in range(4):
                    n1, n2 = 0, 0
                    for i in range(4):
                        if ((self.pos[mark] >> (col*C+row)) >> 7*i) & 1:
                            n1 += 1
                        if ((self.pos[3-mark] >> (col*C+row)) >> 7*i) & 1:
                            n2 += 1
                    if n2 == 0:
                        if n1 == 2:
                            n12 += 1
                        if n1 == 3:
                            n13 += 1
                    if n1 == 0:
                        if n2 == 2:
                            n22 += 1
                        if n2 == 3:
                            n23 += 1
            #positive diagonal
            for row in range(3):
                for col in range(4):
                    n1, n2 = 0, 0
                    for i in range(4):
                        if (self.pos[mark] >> ((col+i)*C+row+i)) & 1:
                            n1 += 1
                        if (self.pos[3-mark] >> ((col+i)*C+row+i)) & 1:
                            n2 += 1
                    if n2 == 0:
                        if n1 == 2:
                            n12 += 1
                        if n1 == 3:
                            n13 += 1
                    if n1 == 0:
                        if n2 == 2:
                            n22 += 1
                        if n2 == 3:
                            n23 += 1
            #positive diagonal
            for row in range(5, 2, -1):
                for col in range(4):
                    n1, n2 = 0, 0
                    for i in range(4):
                        if (self.pos[mark] >> ((col+i)*C+row-i)) & 1:
                            n1 += 1
                        if (self.pos[3-mark] >> ((col+i)*C+row-i)) & 1:
                            n2 += 1
                    if n2 == 0:
                        if n1 == 2:
                            n12 += 1
                        if n1 == 3:
                            n13 += 1
                    if n1 == 0:
                        if n2 == 2:
                            n22 += 1
                        if n2 == 3:
                            n23 += 1
            return  n12, n13, n22, n23

            #################################### agent #########################

    N_STEPS = 6

    # Uses minimax to calculate value of dropping piece in selected column
    def score_move(state, col, mark, nsteps):
        next_state = state.make_move(col, mark)
        return minimax(next_state, nsteps-1, -np.Inf, np.Inf, False, mark)

    # Minimax implementation
    def minimax(state, depth, a, b, maximizingPlayer, mark):

        if time.time() > FINISH:
            return 0

        if state.connected_four(mark):
            return np.inf
        if state.connected_four(3-mark):
            return -np.inf
        if state.mask == 279258638311359:
            return 0

        if depth == 0:
            move = (state.pos[1], state.pos[2])
            if move in MOVES:
                return MOVES[move]
            h = state.heuristic(mark, depth=depth, maximizingPlayer=maximizingPlayer)
            MOVES[move] = h
            return h

        valid_moves = state.valid_moves()

        if maximizingPlayer:
            value = -np.Inf
            for col in valid_moves:
                child = state.make_move(col, mark)
                value = max(value, minimax(child, depth-1, a, b, False, mark))
                if value >= b:
                    break
                a = max(a, value)
            return value
        else:
            value = np.Inf
            for col in valid_moves:
                child = state.make_move(col, 3-mark)
                value = min(value, minimax(child, depth-1, a, b, True, mark))
                if value <= a:
                    break
                b = min(b, value)
            return value

    #########################
    # Agent makes selection #
    #########################

    START = time.time()
    FINISH = START + DELAY
    MOVES = {}

    # Convert the board to a 2D grid
    grid = np.asarray(obs.board).reshape(R, C)

    step = step_number(grid)
    if step < 2:
        return 3

    even = is_even_player(step)
    odd = is_odd_player(step)

    # Get list of valid moves
    state = State.from_grid(grid)
    valid_moves = state.valid_moves()
    for col in valid_moves:
        next_state = state.make_move(col, obs.mark)
        if next_state.connected_four(obs.mark):
            return col

    # Use the heuristic to assign a score to each possible board in the next step
    scores = dict(zip(valid_moves, [score_move(state, col, obs.mark, N_STEPS) for col in valid_moves]))

    if time.time() > FINISH:
        N_STEPS = 2
        FINISH += 0.045
        scores = dict(zip(valid_moves, [score_move(state, col, obs.mark, N_STEPS) for col in valid_moves]))

    while  N_STEPS < 42 - step: # - 1:
        N_STEPS += 1
        scores_2 = dict(zip(valid_moves, [score_move(state, col, obs.mark, N_STEPS) for col in valid_moves]))

        if time.time() > FINISH or np.amax(list(scores_2.values())) <= -np.inf:
            break
        scores = scores_2.copy()

    request.session['scores'] = scores
    request.session['depth'] = N_STEPS - 1


    # Get a list of columns (moves) that maximize the heuristic
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]

    # Select the best as nearest to the center of the board from the maximizing columns

    if len(max_cols) >0:
        if 3 in max_cols:
            return 3
        if 2 in max_cols and 4 in max_cols:
            return random.choice([2, 4])
        if 2 in max_cols:
            return 2
        if 4 in max_cols:
            return 4

        if 1 in max_cols and 5 in max_cols:
            return random.choice([1, 5])
        if 1 in max_cols:
            return 1
        if 5 in max_cols:
            return 5

        if 0 in max_cols and 6 in max_cols:
            return random.choice([0, 6])
        if 0 in max_cols:
            return 0
        if 6 in max_cols:
            return 6

        col = random.choice(max_cols)
        return col
    col =  random.choice(max_cols)
    return col
