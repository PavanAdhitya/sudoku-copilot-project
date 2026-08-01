// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let solution = [];
let timerInterval = null;
let elapsedSeconds = 0;
let timerRunning = false;
let hintsUsed = 0;

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function buildCompletionMessage(difficulty, totalSeconds) {
  const difficultyLabel = difficulty ? difficulty.charAt(0).toUpperCase() + difficulty.slice(1) : 'Medium';
  return `Congratulations! You solved the ${difficultyLabel} puzzle in ${formatTime(totalSeconds)}.`;
}

// Leaderboard keys and helpers
const LEADERBOARD_KEY = 'sudokuLeaderboard';
let _puzzleSolvedHandled = false;

function loadLeaderboard() {
  try {
    const raw = localStorage.getItem(LEADERBOARD_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed;
  } catch (e) {
    return [];
  }
}

function saveLeaderboard(entries) {
  localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(entries));
}

function addLeaderboardEntry(name, timeSeconds, difficulty) {
  const entries = loadLeaderboard();
  const entry = {name: name || 'Anonymous', time_seconds: timeSeconds, difficulty: difficulty || 'medium', hints: hintsUsed ,created_at: Date.now()};
  entries.push(entry);
  entries.sort((a, b) => a.time_seconds - b.time_seconds);
  const top = entries.slice(0, 10);
  saveLeaderboard(top);
}

function formatDifficultyLabel(d) {
  if (!d) return 'Medium';
  return d.charAt(0).toUpperCase() + d.slice(1);
}

function renderLeaderboard() {
  const container = document.getElementById('leaderboard');
  if (!container) return;
  const entries = loadLeaderboard();
  if (!entries || entries.length === 0) {
    container.innerHTML = '<div class="leaderboard-empty">No entries yet. Solve a puzzle to appear here.</div>';
    return;
  }
  const rows = entries.map((e, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${escapeHtml(e.name)}</td>
      <td>${formatTime(e.time_seconds)}</td>
      <td>${escapeHtml(formatDifficultyLabel(e.difficulty))}</td>
      <td>${e.hints ?? 0}</td>
    </tr>
  `).join('');
  container.innerHTML = `
    <table class="leaderboard-table">
      <thead>
      <tr>
        <th>Rank</th>
        <th>Player</th>
        <th>Time</th>
        <th>Difficulty</th>
        <th>Hints</th>
      </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

function escapeHtml(text) {
  if (!text) return '';
  return String(text).replace(/[&<>\"']/g, function (s) {
    return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[s];
  });
}

function updateTimerDisplay() {
  const timer = document.getElementById('timer');
  if (timer) {
    timer.textContent = formatTime(elapsedSeconds);
  }
}

function startTimer() {
  elapsedSeconds = 0;
  updateTimerDisplay();
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  timerRunning = true;
  timerInterval = setInterval(() => {
    if (!timerRunning) {
      return;
    }
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function pauseTimer() {
  timerRunning = false;
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  timerRunning = false;
}

function isBoardSolved(board) {
  if (!solution || solution.length === 0) {
    return false;
  }
  for (let i = 0; i < SIZE; i += 1) {
    for (let j = 0; j < SIZE; j += 1) {
      if (board[i][j] !== solution[i][j]) {
        return false;
      }
    }
  }
  return true;
}

function maybeStopTimerOnSuccess(board) {
  if (isBoardSolved(board)) {
    stopTimer();
    const difficulty = document.getElementById('difficulty-select')?.value || 'medium';
    handlePuzzleSolved(difficulty, elapsedSeconds);
  }
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function updateCellValidation(input) {
  input.classList.remove('incorrect');
  if (input.disabled || input.value === '') {
    return;
  }

  const row = parseInt(input.dataset.row, 10);
  const col = parseInt(input.dataset.col, 10);
  const expected = solution[row][col];
  const entered = parseInt(input.value, 10);

  if (entered !== expected) {
    input.classList.add('incorrect');
  }
}

function getCellClassName(row, col) {
  const blockRow = Math.floor(row / 3);
  const blockCol = Math.floor(col / 3);
  return (blockRow + blockCol) % 2 === 0 ? 'sudoku-cell block-even' : 'sudoku-cell block-odd';
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = getCellClassName(i, j);
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateCellValidation(e.target);
        maybeStopTimerOnSuccess(getBoardFromInputs());
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, sol) {
  puzzle = puz;
  solution = sol;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.className = getCellClassName(i, j);
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
      inp.classList.remove('incorrect');
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty-select').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle, data.solution);
  _puzzleSolvedHandled = false;
  hintsUsed = 0;
  startTimer();
  document.getElementById('message').innerText = '';
  // refresh leaderboard display (in case user cleared storage elsewhere)
  renderLeaderboard();
}

async function checkSolution() {
  const board = getBoardFromInputs();
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const difficulty = document.getElementById('difficulty-select').value;
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board, partial: false, elapsed_seconds: elapsedSeconds, difficulty})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    const row = Number(inp.dataset.row);
    const col = Number(inp.dataset.col);
    inp.className = getCellClassName(row, col);
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }
  if (incorrect.size === 0) {
    stopTimer();
    handlePuzzleSolved(difficulty, elapsedSeconds);
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function checkPuzzle() {
  const board = getBoardFromInputs();
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board, partial: true})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    // keep the cell value — only toggle the incorrect highlight
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    } else {
      inp.classList.remove('incorrect');
    }
  }
  if (incorrect.size === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = 'No incorrect entries found.';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some entries are incorrect.';
  }
}

async function applyHint() {
  const board = getBoardFromInputs();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  renderPuzzle(data.puzzle, solution);
  hintsUsed++;
  msg.style.color = '#388e3c';
  msg.innerText = 'Hint applied.';
}

const THEME_KEY = 'sudokuTheme';

function applyTheme(theme) {
  const body = document.body;
  const toggle = document.getElementById('theme-toggle');
  const isDark = theme === 'dark';
  body.classList.toggle('dark-mode', isDark);
  if (toggle) {
    toggle.textContent = isDark ? 'Light mode' : 'Dark mode';
  }
}

function loadSavedTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === 'light' || saved === 'dark') {
    return saved;
  }
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function toggleTheme() {
  const current = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  localStorage.setItem(THEME_KEY, next);
}

// Called when a puzzle is solved to capture name and save leaderboard entry
function handlePuzzleSolved(difficulty, totalSeconds) {
  if (_puzzleSolvedHandled) return;
  _puzzleSolvedHandled = true;
  const msg = document.getElementById('message');
  if (msg) {
    msg.style.color = '#388e3c';
    msg.innerText = buildCompletionMessage(difficulty, totalSeconds);
  }
  // Ask for player name
  try {
    const promptMsg = `You solved the puzzle in ${formatTime(totalSeconds)}. Enter your name for the leaderboard:`;
    const name = window.prompt(promptMsg, '');
    if (name === null) {
      // user cancelled - do not save but still show leaderboard
      renderLeaderboard();
      return;
    }
    const cleaned = name.trim() || 'Anonymous';
    addLeaderboardEntry(cleaned, totalSeconds, difficulty);
    renderLeaderboard();
  } catch (e) {
    // ignore prompt errors
    renderLeaderboard();
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-puzzle').addEventListener('click', checkPuzzle);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', applyHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  // initialize
  applyTheme(loadSavedTheme());
  renderLeaderboard();
  newGame();
});