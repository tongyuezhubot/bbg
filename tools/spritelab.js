/* 像素精灵检视台
   把 HTML 里真正在跑的 drawPerson 抽出来，用自写的 canvas 光栅化成 PNG，
   放大后肉眼检查。改一次画一次，不再盲写坐标。 */
const fs = require("fs");
const zlib = require("zlib");

/* ── 极简 2D context：只需要 fillStyle + fillRect ── */
function parseColor(s) {
  if (typeof s !== "string") return [0, 0, 0, 0];
  s = s.trim();
  if (s[0] === "#") {
    let h = s.slice(1);
    if (h.length === 3) h = h.split("").map(c => c + c).join("");
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16), 1];
  }
  const m = s.match(/rgba?\(([^)]+)\)/);
  if (m) {
    const p = m[1].split(",").map(v => parseFloat(v));
    return [p[0] | 0, p[1] | 0, p[2] | 0, p[3] === undefined ? 1 : p[3]];
  }
  return [0, 0, 0, 0];
}
class MiniCtx {
  constructor(w, h) {
    this.w = w; this.h = h;
    this.buf = new Uint8ClampedArray(w * h * 4);
    this._fill = [0, 0, 0, 1];
    this.globalAlpha = 1;
    this.globalCompositeOperation = "source-over";
  }
  set fillStyle(v) { this._fill = parseColor(v); }
  get fillStyle() { return this._fill; }
  fillRect(x, y, w, h) {
    const [r, g, b, a0] = this._fill;
    const a = a0 * this.globalAlpha;
    if (a <= 0) return;
    x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h);
    for (let j = y; j < y + h; j++) {
      if (j < 0 || j >= this.h) continue;
      for (let i = x; i < x + w; i++) {
        if (i < 0 || i >= this.w) continue;
        const k = (j * this.w + i) * 4;
        const da = this.buf[k + 3] / 255;
        const oa = a + da * (1 - a);
        this.buf[k]     = (r * a + this.buf[k]     * da * (1 - a)) / oa;
        this.buf[k + 1] = (g * a + this.buf[k + 1] * da * (1 - a)) / oa;
        this.buf[k + 2] = (b * a + this.buf[k + 2] * da * (1 - a)) / oa;
        this.buf[k + 3] = oa * 255;
      }
    }
  }
  // 精灵里用不到，留空避免报错
  createLinearGradient() { return { addColorStop() {} }; }
  createRadialGradient() { return { addColorStop() {} }; }
  beginPath() {} arc() {} moveTo() {} lineTo() {} closePath() {} fill() {}
  clearRect(x, y, w, h) {
    for (let j = y; j < y + h; j++) for (let i = x; i < x + w; i++) {
      const k = (j * this.w + i) * 4; this.buf[k] = this.buf[k+1] = this.buf[k+2] = this.buf[k+3] = 0;
    }
  }
  drawImage() {}
}

/* ── PNG 编码 ── */
function writePNG(path, buf, w, h, zoom) {
  const W = w * zoom, H = h * zoom;
  const raw = Buffer.alloc(H * (W * 4 + 1));
  let o = 0;
  for (let y = 0; y < H; y++) {
    raw[o++] = 0;
    const sy = (y / zoom) | 0;
    for (let x = 0; x < W; x++) {
      const sx = (x / zoom) | 0, k = (sy * w + sx) * 4;
      raw[o++] = buf[k]; raw[o++] = buf[k + 1]; raw[o++] = buf[k + 2]; raw[o++] = buf[k + 3];
    }
  }
  const chunk = (type, data) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const td = Buffer.concat([Buffer.from(type, "ascii"), data]);
    const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td) >>> 0);
    return Buffer.concat([len, td, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(W, 0); ihdr.writeUInt32BE(H, 4);
  ihdr[8] = 8; ihdr[9] = 6; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  fs.writeFileSync(path, Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk("IHDR", ihdr),
    chunk("IDAT", zlib.deflateSync(raw)),
    chunk("IEND", Buffer.alloc(0)),
  ]));
}
let CRC_T = null;
function crc32(b) {
  if (!CRC_T) {
    CRC_T = new Int32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      CRC_T[n] = c;
    }
  }
  let c = -1;
  for (let i = 0; i < b.length; i++) c = CRC_T[(c ^ b[i]) & 0xff] ^ (c >>> 8);
  return c ^ -1;
}

/* ── 从 HTML 里取出真正在用的绘制代码 ── */
const html = fs.readFileSync(__dirname+"/../index.html", "utf8");
let js = html.match(/<script>([\s\S]*)<\/script>/)[1];
js = js.replace("let saveT = 0;",
  "let saveT = 0; globalThis.__api={drawPerson,makePerson,CAST,drawPersonLying};");

const RAF = [];
globalThis.requestAnimationFrame = f => RAF.push(f);
globalThis.performance = { now: () => 0 };
globalThis.matchMedia = () => ({ matches: false });
globalThis.addEventListener = () => {};
const store = {};
globalThis.localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); } };
const dummy = () => new Proxy({}, { get: (t, k) => {
  if (k === "createLinearGradient" || k === "createRadialGradient") return () => ({ addColorStop() {} });
  if (k === "canvas") return { width: 0, height: 0 };
  return () => {};
}, set: () => true });
globalThis.document = {
  getElementById: () => ({ getContext: dummy }),
  createElement: () => ({ width: 0, height: 0, getContext: dummy }),
  visibilityState: "visible",
};
eval(js);
const API = globalThis.__api;

/* ── 排版：每个角色一行，四个朝向 + 走路帧 + 躺姿 ── */
const CELL_W = 26, CELL_H = 34;
const DIRS = ["s", "e", "n", "w"];
const cast = Object.keys(API.CAST).concat(['haley']);  // 末行：海莉不戴帽
const COLS = DIRS.length * 2 + 1;          // 每朝向 站/走 两帧，末列留给躺姿
const SHEET_W = CELL_W * COLS, SHEET_H = CELL_H * cast.length;

const ctx = new MiniCtx(SHEET_W, SHEET_H);
// 棋盘底，方便看清轮廓和透明区
for (let y = 0; y < SHEET_H; y++) for (let x = 0; x < SHEET_W; x++) {
  ctx.fillStyle = ((x >> 2) + (y >> 2)) % 2 ? "#3a3a42" : "#2e2e35";
  ctx.fillRect(x, y, 1, 1);
}
// 每行分隔线
ctx.fillStyle = "rgba(255,255,255,.18)";
for (let i = 1; i < cast.length; i++) ctx.fillRect(0, i * CELL_H, SHEET_W, 1);
for (let i = 1; i < COLS; i++) ctx.fillRect(i * CELL_W, 0, 1, SHEET_H);

cast.forEach((key, row) => {
  const baseY = row * CELL_H;
  DIRS.forEach((d, di) => {
    [0, 1].forEach(frame => {
      const n = API.makePerson(key);
      n.hat = row < 4 && !!API.CAST[key].cap;   // 末行故意不戴
      n.dir = d;
      n.seed = 0;
      n.path = frame ? [{ x: 0, y: 0 }] : [];   // 有路径 = 走路帧
      n.px = (di * 2 + frame) * CELL_W + CELL_W / 2;
      n.py = baseY + CELL_H - 5;
      API.drawPerson(ctx, n, frame ? 0.16 : 0);  // time 选在抬腿相位
    });
  });
  // 躺姿
  const l = API.makePerson(key);
  l.dir = "w"; l.seed = 0; l.lying = true;
  l.px = 8 * CELL_W + CELL_W - 4;
  l.py = baseY + CELL_H - 8;
  API.drawPersonLying(ctx, l, 0);
});

writePNG(__dirname + "/sprites.png", ctx.buf, SHEET_W, SHEET_H, 8);
console.log("sheet:", SHEET_W + "x" + SHEET_H, "-> sprites.png (8x)");
console.log("行序:", cast.map(k => API.CAST[k].name).join(" / "));
console.log("列序: 朝下(站,走) 朝东(站,走) 朝上(站,走) 朝西(站,走) 躺");
