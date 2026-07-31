import pytest
import app as sudoku_app


@pytest.fixture
def client():
    sudoku_app.app.config.update(TESTING=True)
    with sudoku_app.app.test_client() as client:
        yield client


def test_index_route_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.content_type.startswith("text/html")


def test_index_contains_timer_display(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'id="timer"' in response.data


def test_new_game_route_returns_puzzle(client):
    response = client.get("/new?clues=30")

    assert response.status_code == 200
    payload = response.get_json()

    assert "puzzle" in payload
    assert isinstance(payload["puzzle"], list)
    assert len(payload["puzzle"]) == 9
    assert all(len(row) == 9 for row in payload["puzzle"])
    assert sudoku_app.CURRENT["puzzle"] == payload["puzzle"]
    assert sudoku_app.CURRENT["solution"] is not None


def test_new_game_route_includes_solution_for_client_validation(client):
    response = client.get("/new?clues=30")

    assert response.status_code == 200
    payload = response.get_json()

    assert "solution" in payload
    assert isinstance(payload["solution"], list)
    assert len(payload["solution"]) == 9
    assert all(len(row) == 9 for row in payload["solution"])


def test_check_solution_without_game_returns_error(client):
    sudoku_app.CURRENT["puzzle"] = None
    sudoku_app.CURRENT["solution"] = None

    response = client.post(
        "/check",
        json={"board": [[0] * 9 for _ in range(9)]},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_check_solution_returns_congratulatory_message_with_time_and_difficulty(client):
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    sudoku_app.CURRENT["puzzle"] = solution
    sudoku_app.CURRENT["solution"] = solution

    response = client.post(
        "/check",
        json={"board": solution, "elapsed_seconds": 125, "difficulty": "hard"},
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Congratulations! You solved the Hard puzzle in 02:05."


def test_hint_route_fills_one_empty_cell_and_updates_state(client):
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    puzzle = [[0] * 9 for _ in range(9)]
    sudoku_app.CURRENT["puzzle"] = puzzle
    sudoku_app.CURRENT["solution"] = solution

    response = client.post("/hint", json={"board": puzzle})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["hinted_cell"] == [0, 0]
    assert payload["puzzle"][0][0] == solution[0][0]
    assert sudoku_app.CURRENT["puzzle"][0][0] == solution[0][0]
    assert sudoku_app.CURRENT["puzzle"][0][1] == 0
