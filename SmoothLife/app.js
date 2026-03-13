const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const image = ctx.createImageData(canvas.width, canvas.height);

const toggleBtn = document.getElementById("toggleBtn");
const seedBtn = document.getElementById("seedBtn");
const dtInput = document.getElementById("dtInput");
const rInput = document.getElementById("rInput");
const meta = document.getElementById("meta");

const W = 160;
const H = 106;
let R = Number(rInput.value);
const rRatio = 3;

let field = new Float32Array(W * H);
let next = new Float32Array(W * H);
let running = false;
let tick = 0;

function idx(x, y) {
  return y * W + x;
}

function wrap(v, m) {
  return (v + m) % m;
}

function sigmoid(x, a, alpha) {
  return 1 / (1 + Math.exp(-(x - a) * 4 / alpha));
}

function sigma2(x, a, b, alpha) {
  return sigmoid(x, a, alpha) * (1 - sigmoid(x, b, alpha));
}

function reseed() {
  field.fill(0);
  for (let y = H * 0.25; y < H * 0.75; y++) {
    for (let x = W * 0.25; x < W * 0.75; x++) {
      const i = idx(x | 0, y | 0);
      field[i] = Math.random() < 0.38 ? Math.random() : 0;
    }
  }
  tick = 0;
  draw();
}

function avgInRadius(cx, cy, radius, inner = 0) {
  const r2 = radius * radius;
  const in2 = inner * inner;
  let sum = 0;
  let cnt = 0;

  for (let dy = -radius; dy <= radius; dy++) {
    for (let dx = -radius; dx <= radius; dx++) {
      const d2 = dx * dx + dy * dy;
      if (d2 > r2 || d2 <= in2) continue;
      const x = wrap(cx + dx, W);
      const y = wrap(cy + dy, H);
      sum += field[idx(x, y)];
      cnt += 1;
    }
  }

  return cnt ? sum / cnt : 0;
}

function step() {
  const dt = Math.max(0.01, Math.min(1, Number(dtInput.value) || 0.12));
  const alphaN = 0.028;
  const alphaM = 0.147;
  const b1 = 0.278;
  const b2 = 0.365;
  const d1 = 0.267;
  const d2 = 0.445;

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const m = avgInRadius(x, y, R);
      const n = avgInRadius(x, y, R * rRatio, R);

      const birth = sigma2(n, b1, b2, alphaN);
      const death = sigma2(n, d1, d2, alphaN);
      const mix = sigmoid(m, 0.5, alphaM);
      const s = birth * (1 - mix) + death * mix;

      const i = idx(x, y);
      next[i] = Math.max(0, Math.min(1, field[i] + dt * (s - field[i])));
    }
  }

  const tmp = field;
  field = next;
  next = tmp;
  tick += 1;
}

function draw() {
  const sx = canvas.width / W;
  const sy = canvas.height / H;
  const pix = image.data;

  for (let py = 0; py < canvas.height; py++) {
    const y = Math.min(H - 1, Math.floor(py / sy));
    for (let px = 0; px < canvas.width; px++) {
      const x = Math.min(W - 1, Math.floor(px / sx));
      const v = field[idx(x, y)];
      const c = Math.floor(v * 255);
      const p = (py * canvas.width + px) * 4;
      pix[p] = Math.floor(c * 0.35);
      pix[p + 1] = Math.floor(c * 0.8);
      pix[p + 2] = c;
      pix[p + 3] = 255;
    }
  }

  ctx.putImageData(image, 0, 0);
  meta.textContent = `Grid ${W}x${H} | tick ${tick} | R=${R}`;
}

function loop() {
  if (running) {
    step();
    draw();
  }
  requestAnimationFrame(loop);
}

toggleBtn.addEventListener("click", () => {
  running = !running;
  toggleBtn.textContent = running ? "Stop" : "Start";
});

seedBtn.addEventListener("click", reseed);
rInput.addEventListener("change", () => {
  R = Math.max(3, Math.min(20, Number(rInput.value) || 8));
});

reseed();
loop();
