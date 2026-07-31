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
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = (row // 3) * 3
    start_col = (col // 3) * 3
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == num:
                return False
    return True


def get_candidates(board, row, col):
    if board[row][col] != EMPTY:
        return []

    used_values = set()
    for x in range(SIZE):
        if board[row][x] != EMPTY:
            used_values.add(board[row][x])
        if board[x][col] != EMPTY:
            used_values.add(board[x][col])

    start_row = (row // 3) * 3
    start_col = (col // 3) * 3
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] != EMPTY:
                used_values.add(board[i][j])

    return [value for value in range(1, SIZE + 1) if value not in used_values]


def fill_board(board):
    empty_cell = find_empty_cell(board)
    if empty_cell is None:
        return True

    row, col, candidates = empty_cell
    random.shuffle(candidates)
    for candidate in candidates:
        if is_safe(board, row, col, candidate):
            board[row][col] = candidate
            if fill_board(board):
                return True
            board[row][col] = EMPTY
    return False


def find_empty_cell(board):
    best_row = best_col = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue

            candidates = get_candidates(board, row, col)
            if not candidates:
                return row, col, []

            if best_candidates is None or len(candidates) < len(best_candidates):
                best_row, best_col = row, col
                best_candidates = candidates
                if len(best_candidates) == 1:
                    return best_row, best_col, best_candidates

    if best_row is None:
        return None

    return best_row, best_col, best_candidates


def count_solutions(board, limit=2):
    """Count solutions up to the provided limit and stop early.

    The solver uses backtracking with constraint checks and a most-constrained-cell
    choice, which is fast enough for puzzle generation while still confirming
    that a puzzle has exactly one solution.
    """

    board = deep_copy(board)

    empty_cell = find_empty_cell(board)
    if empty_cell is None:
        return 1

    row, col, candidates = empty_cell
    if not candidates:
        return 0

    solutions = 0
    random.shuffle(candidates)

    for candidate in candidates:
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
