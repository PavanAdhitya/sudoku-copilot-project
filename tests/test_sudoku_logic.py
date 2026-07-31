import sudoku_logic


def count_clues(board):
    return sum(1 for row in board for value in row if value != 0)


def is_valid_board(board):
    for row in board:
        values = [value for value in row if value != 0]
        if len(set(values)) != len(values):
            return False

    for col in range(sudoku_logic.SIZE):
        values = [board[row][col] for row in range(sudoku_logic.SIZE) if board[row][col] != 0]
        if len(set(values)) != len(values):
            return False

    for box_row in range(0, sudoku_logic.SIZE, 3):
        for box_col in range(0, sudoku_logic.SIZE, 3):
            values = []
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    value = board[row][col]
                    if value != 0:
                        values.append(value)
            if len(set(values)) != len(values):
                return False

    return True


def test_create_empty_board_returns_9x9_zero_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert board == [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]


def test_generate_puzzle_returns_valid_puzzle_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert isinstance(puzzle, list)
    assert isinstance(solution, list)
    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)

    assert all(0 <= value <= 9 for row in puzzle for value in row)
    assert all(1 <= value <= 9 for row in solution for value in row)
    assert any(0 in row for row in puzzle)
    assert not any(0 in row for row in solution)

    assert is_valid_board(puzzle)
    assert is_valid_board(solution)


def test_generate_puzzle_difficulty_levels_create_unique_solutions():
    expected_clues = {"easy": 40, "medium": 32, "hard": 24}

    for difficulty, clues in expected_clues.items():
        puzzle, _ = sudoku_logic.generate_puzzle(difficulty=difficulty)

        assert count_clues(puzzle) == clues
        assert sudoku_logic.count_solutions(puzzle) == 1
