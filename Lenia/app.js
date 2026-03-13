const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const image = ctx.createImageData(canvas.width, canvas.height);

const toggleBtn = document.getElementById("toggleBtn");
const seedBtn = document.getElementById("seedBtn");
const dtInput = document.getElementById("dtInput");
const muInput = document.getElementById("muInput");
const sigmaInput = document.getElementById("sigmaInput");
const meta = document.getElementById("meta");

const W = 120;
const H = 80;
const KERNEL_R = 13;

let grid = new Float32Array(W * H);
let next = new Float32Array(W * H);
let running = false;
let tick = 0;

const kernel = [];

function idx(x, y) {
  return y * W + x;
}

function wrap(v, m) {
  return (v + m) % m;
}

function buildKernel() {
  kernel.length = 0;
  let sum = 0;

  for (let dy = -KERNEL_R; dy <= KERNEL_R; dy++) {
    for (let dx = -KERNEL_R; dx <= KERNEL_R; dx++) {
      const r = Math.sqrt(dx * dx + dy * dy) / KERNEL_R;
      if (r > 1) continue;

      const shell = Math.exp(-((r - 0.5) * (r - 0.5)) / (2 * 0.15 * 0.15));
      kernel.push({ dx, dy, w: shell });
      sum += shell;
    }
  }

  for (const k of kernel) k.w /= sum;
}

function reseed() {
  grid.fill(0);
  const cx = Math.floor(W / 2);
  const cy = Math.floor(H / 2);

  for (let y = -18; y <= 18; y++) {
    for (let x = -18; x <= 18; x++) {
      const d = Math.sqrt(x * x + y * y);
      if (d <= 16 && Math.random() < 0.45) {
        grid[idx(wrap(cx + x, W), wrap(cy + y, H))] = Math.random() * 0.8 + 0.2;
      }
    }
  }

  tick = 0;
  draw();
}

function growth(u, mu, sigma) {
  return Math.exp(-((u - mu) * (u - mu)) / (2 * sigma * sigma)) * 2 - 1;
}

function step() {
  const dt = Math.max(0.01, Math.min(0.5, Number(dtInput.value) || 0.1));
  const mu = Math.max(0.05, Math.min(0.5, Number(muInput.value) || 0.15));
  const sigma = Math.max(0.01, Math.min(0.2, Number(sigmaInput.value) || 0.03));

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let u = 0;
      for (const k of kernel) {
        const sx = wrap(x + k.dx, W);
        const sy = wrap(y + k.dy, H);
        u += grid[idx(sx, sy)] * k.w;
      }

      const g = growth(u, mu, sigma);
      const i = idx(x, y);
      next[i] = Math.max(0, Math.min(1, grid[i] + dt * g));
    }
  }

  const t = grid;
  grid = next;
  next = t;
  tick += 1;
}

function palette(v) {
  const a = Math.max(0, Math.min(1, v));
  const r = Math.floor(35 + 220 * Math.pow(a, 0.85));
  const g = Math.floor(20 + 180 * Math.pow(a, 1.4));
  const b = Math.floor(45 + 240 * Math.pow(a, 2.0));
  return [r, g, b];
}

function draw() {
  const sx = canvas.width / W;
  const sy = canvas.height / H;
  const pix = image.data;

  for (let py = 0; py < canvas.height; py++) {
    const y = Math.min(H - 1, Math.floor(py / sy));
    for (let px = 0; px < canvas.width; px++) {
      const x = Math.min(W - 1, Math.floor(px / sx));
      const v = grid[idx(x, y)];
      const [r, g, b] = palette(v);
      const p = (py * canvas.width + px) * 4;
      pix[p] = r;
      pix[p + 1] = g;
      pix[p + 2] = b;
      pix[p + 3] = 255;
    }
  }

  ctx.putImageData(image, 0, 0);
  const mass = grid.reduce((a, b) => a + b, 0).toFixed(1);
  meta.textContent = `Grid ${W}x${H} | tick ${tick} | mass ${mass}`;
}

function frame() {
  if (running) {
    step();
    draw();
  }
  requestAnimationFrame(frame);
}

toggleBtn.addEventListener("click", () => {
  running = !running;
  toggleBtn.textContent = running ? "Stop" : "Start";
});

seedBtn.addEventListener("click", reseed);

buildKernel();
reseed();
frame();
