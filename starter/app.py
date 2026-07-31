from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    clues_arg = request.args.get('clues')
    difficulty = request.args.get('difficulty', 'medium').lower()

    if clues_arg is not None:
        clues = int(clues_arg)
        puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
    else:
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'solution': solution})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    partial = data.get('partial', False)
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            # If partial checking is requested, only validate cells
            # that the player has filled (non-zero). For full checks,
            # compare every cell against the solution.
            if partial:
                if board[i][j] != 0 and board[i][j] != solution[i][j]:
                    incorrect.append([i, j])
            else:
                if board[i][j] != solution[i][j]:
                    incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def apply_hint():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    if board is None:
        return jsonify({'error': 'No board provided'}), 400

    updated_board = sudoku_logic.deep_copy(board)
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if updated_board[i][j] == sudoku_logic.EMPTY:
                updated_board[i][j] = solution[i][j]
                CURRENT['puzzle'] = updated_board
                return jsonify({'puzzle': updated_board, 'hinted_cell': [i, j]})

    return jsonify({'error': 'No empty cells remaining'}), 400

if __name__ == '__main__':
    app.run(debug=True)