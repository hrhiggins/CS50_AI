"""
Tic Tac Toe Player
"""
import copy
import math

# Define states
X = "X"
O = "O"
EMPTY = None

# Initial empty starting state of board
def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Starting states
    x_count = 0
    o_count = 0
    empty_count = 0

    # Iterate through each row --> then iterate through each cell in the row
    # Count quantity of empty cells, X cells and O cells
    # From this info, turn can be established
    for row in board:
        for cell in row:
            if cell == EMPTY:
                empty_count += 1
            elif cell == X:
                x_count += 1
            elif cell == O:
                o_count += 1
            # If cell does not contain EMPTY, X or O then raise an error
            else:
                raise ValueError

    # Check that correct number of items have been counted
    # If not then raise an error
    if o_count + x_count + empty_count != 9:
        raise ValueError

    # If all cells are empty then the game has not started yet. Thus, X starts (X always starts)
    if empty_count == 9:
        return X
    # If more X tiles then O then it must be O turn
    if x_count > o_count:
        return O
    # If same number of X and O tiles then must be X turn (as X goes first)
    if x_count == o_count:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Create movement set
    moves = set()

    # Iterate through rows
    for row in range(3):
        # Iterate through cells in row
        for col in range(3):
            # If the cells is empty then add it to the possible move set
            if board[row][col] == EMPTY:
                moves.add((row, col))
    # Return all possible moves
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Check that the provided action is possible, by seeing if it exists in the action set
    if action in actions(board):
        # Creat new board, do not use original one
        r = copy.deepcopy(board)
        # An action is a move (i, j)
        # So on the board set whom ever go it is (established by player(board) to that open space
        r[action[0]][action[1]] = player(board)
        # Return the altered board
        return r
    else:
        raise Exception("No such action")


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Iterate through rows on board
    for row in range(3):
        # If each cell in that row contains the same thing then:
        if board[row][0] == board[row][1] == board[row][2]:
            # If X then X has won
            if board[row][0] == X:
                return X
            # If O then O has won
            elif board[row][0] == O:
                return O
            # Otherwise pass (empty row)
            else:
                pass

    # Iterate down columns on board
    for col in range(3):
        # If each cell in that column contains the same thing then:
        if board[0][col] == board[1][col] == board[2][col]:
            # If X then X has won
            if board[0][col] == X:
                return X
            # If O then O has won
            elif board[0][col] == O:
                return O
            # Otherwise pass (empty row)
            else:
                pass

    # Checking for diagonals. If the diagonals are all X then X wins and vice versa
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return X
    elif board[0][0] == O and board[1][1] == O and board[2][2] == O:
        return O
    elif board[2][0] == X and board[1][1] == X and board[0][2] == X:
        return X
    elif board[2][0] == O and board[1][1] == O and board[0][2] == O:
        return O
    else:
        pass

    # If none of this is true then return None as no one has won
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # If there is a winner then it is clearly true, as this is a terminal state
    if winner(board):
        return True

    # The other terminal state is when all spaces on the baord are taken up
    # Iterate through rows
    for row in range(3):
        # Iterate through cell in each row
        for col in range(3):
            # If the space is empyt then it is not a terminal state as not all spaces have been filled
            if board[row][col] == EMPTY:
                # Thus return false
                return False
    # If no empty spaces then all spaces are filled, thus terminal state
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Establish winner of game
    game_winner = winner(board)
    if game_winner == X:
        return 1
    elif game_winner == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == X:
        # X picks action with the highest value of min_value
        return max_value(board)[1]
    else:
        # O picks action with the lowest value of max_value
        return min_value(board)[1]


def max_value(board):
    # Initial starting value
    v = float("-inf")
    # Initial starting move
    move = None
    # If terminal state then no need to continue
    if terminal(board):
        return [utility(board), None]
    # Iterate through actions in the action set
    for act in actions(board):
        # Find the minumum value of the results that can occur using that action on the current board
        current = min_value(result(board, act))[0]
        # If the minimum value is greater than the previous/starting value then update the recommended move
        if current > v:
            v = current
            move = act
    return [v, move]

def min_value(board):
    # Initial starting value
    v = float("inf")
    # Initial starting move
    move = None
    # If terminal state then non need to continue
    if terminal(board):
        return [utility(board), None]
    # Iterate through actions in the action set
    for act in actions(board):
        # Find the maximum value of the results that can occur using that action on the current board
        current = max_value(result(board, act))[0]
        # If the maximum value is greater than the previous/starting value then update the recommended move
        if current < v:
            v = current
            move = act
    return [v, move]
