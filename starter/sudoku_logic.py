import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_SETTINGS = {
    "easy": 40,
    "medium": 32,
    "hard": 24,
}


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def count_clues(board):
    return sum(1 for row in board for value in row if value != EMPTY)


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def count_solutions(board, limit=2):
    board = deep_copy(board)

    empty_cell = find_empty_cell(board)
    if empty_cell is None:
        return 1

    row, col = empty_cell
    solutions = 0

    for candidate in random.sample(range(1, SIZE + 1), SIZE):
        if not is_safe(board, row, col, candidate):
            continue

        board[row][col] = candidate
        remaining = limit - solutions
        if remaining <= 0:
            board[row][col] = EMPTY
            return limit

        solutions += count_solutions(board, remaining)
        board[row][col] = EMPTY

        if solutions >= limit:
            return limit

    return solutions


def remove_cells(board, clues):
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    while count_clues(board) > clues:
        row, col = cells.pop()
        if board[row][col] == EMPTY:
            continue

        original_value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) != 1:
            board[row][col] = original_value


def generate_puzzle(clues=None, difficulty="medium"):
    if clues is None:
        normalized_difficulty = str(difficulty).lower()
        clues = DIFFICULTY_SETTINGS.get(normalized_difficulty, DIFFICULTY_SETTINGS["medium"])

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
