const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const toggleBtn = document.getElementById("toggleBtn");
const stepBtn = document.getElementById("stepBtn");
const clearBtn = document.getElementById("clearBtn");
const randBtn = document.getElementById("randBtn");
const speedInput = document.getElementById("speedInput");
const meta = document.getElementById("meta");

const cellSize = 8;
const w = Math.floor(canvas.width / cellSize);
const h = Math.floor(canvas.height / cellSize);

let grid = new Uint8Array(w * h);
let next = new Uint8Array(w * h);
let running = false;
let tick = 0;
let timer = null;

function idx(x, y) {
  return y * w + x;
}

function randomize(density = 0.18) {
  for (let i = 0; i < grid.length; i++) {
    grid[i] = Math.random() < density ? 1 : 0;
  }
  tick = 0;
  render();
}

function clearAll() {
  grid.fill(0);
  tick = 0;
  render();
}

function countNeighbors(x, y) {
  let n = 0;
  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      if (dx === 0 && dy === 0) continue;
      const nx = (x + dx + w) % w;
      const ny = (y + dy + h) % h;
      n += grid[idx(nx, ny)];
    }
  }
  return n;
}

function step() {
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = idx(x, y);
      const alive = grid[i] === 1;
      const n = countNeighbors(x, y);

      // HighLife: B36/S23
      if (alive) {
        next[i] = n === 2 || n === 3 ? 1 : 0;
      } else {
        next[i] = n === 3 || n === 6 ? 1 : 0;
      }
    }
  }

  const tmp = grid;
  grid = next;
  next = tmp;
  tick += 1;
  render();
}

function render() {
  ctx.fillStyle = "#090d13";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#f0f6fc";
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      if (grid[idx(x, y)] === 1) {
        ctx.fillRect(x * cellSize, y * cellSize, cellSize - 1, cellSize - 1);
      }
    }
  }

  const alive = grid.reduce((a, b) => a + b, 0);
  meta.textContent = `Rule B36/S23 | ${w}x${h} | tick ${tick} | alive ${alive}`;
}

function restartLoop() {
  if (timer) clearInterval(timer);
  if (!running) return;
  const speed = Math.max(10, Math.min(1000, Number(speedInput.value) || 80));
  timer = setInterval(step, speed);
}

toggleBtn.addEventListener("click", () => {
  running = !running;
  toggleBtn.textContent = running ? "Stop" : "Start";
  restartLoop();
});

stepBtn.addEventListener("click", () => {
  if (!running) step();
});

clearBtn.addEventListener("click", clearAll);
randBtn.addEventListener("click", () => randomize());
speedInput.addEventListener("change", restartLoop);

canvas.addEventListener("mousedown", (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = Math.floor((e.clientX - rect.left) / cellSize);
  const y = Math.floor((e.clientY - rect.top) / cellSize);
  if (x >= 0 && x < w && y >= 0 && y < h) {
    const i = idx(x, y);
    grid[i] = grid[i] ? 0 : 1;
    render();
  }
});

randomize(0.2);
