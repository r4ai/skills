// 組み立てた index.html を headless Chromium で 1 コマずつ表示し、崩れを検査して画像を残す。
//
//   node check_deck.mjs <index.html> <出力ディレクトリ> [タイトル ...]
//
// - hidden ボタンを押して、隠すスライドも含めた全コマを検査する
// - はみ出し（舞台の外へ出た要素）、数式の右端の切れ（clip）、最終行が短すぎる改行（SHORT）を報告する
// - タイトルを渡すとそのコマだけ、渡さなければ全コマの画像を out/sNN.png に保存する
// Chromium は playwright の chromium_headless_shell を使う（CHROME で上書きできる）。
// Google Fonts の <link> は外す。headless では読み込みが終わらず、ページが止まることがある。
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, readdirSync, mkdirSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';

const [input, outDir, ...titles] = process.argv.slice(2);
if (!input || !outDir) {
  console.error('usage: node check_deck.mjs <index.html> <out-dir> [title ...]');
  process.exit(2);
}
const out = resolve(outDir);
mkdirSync(out, { recursive: true });
const base = process.env.HOME + '/.cache/ms-playwright/';
const shell = readdirSync(base).find((x) => x.startsWith('chromium_headless_shell'));
const chrome = process.env.CHROME ?? `${base}${shell}/chrome-headless-shell-linux64/chrome-headless-shell`;
const page = `${out}/page.html`;
writeFileSync(page, '<!doctype html><html><head><meta charset=utf-8></head><body>' +
  readFileSync(input, 'utf8').replace(/<link rel="stylesheet"[^>]*>/g, '') + '</body></html>');

const port = 9300 + Math.floor(Math.random() * 600);
const profile = `${out}/.profile`;
rmSync(profile, { recursive: true, force: true });
const proc = spawn(chrome, ['--headless', '--no-sandbox', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, '--hide-scrollbars'], { stdio: 'ignore' });
try {
  let targets;
  for (let i = 0; i < 50 && !targets; i++) {
    await new Promise((r) => setTimeout(r, 200));
    targets = await fetch(`http://127.0.0.1:${port}/json`).then((r) => r.json()).catch(() => null);
  }
  const target = targets.find((x) => x.type === 'page') ??
    await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' }).then((r) => r.json());
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  let id = 0;
  const pending = new Map();
  ws.onmessage = (m) => { const x = JSON.parse(m.data); if (pending.has(x.id)) { pending.get(x.id)(x.result); pending.delete(x.id); } };
  const send = (method, params = {}) => new Promise((r) => { pending.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
  const ev = async (expression) => (await send('Runtime.evaluate', { expression, returnByValue: true })).result.value;

  await send('Emulation.setDeviceMetricsOverride', { width: 960, height: 580, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'file://' + page });
  await new Promise((r) => setTimeout(r, 3000));
  await ev(`document.getElementById('thidden')?.click()`);
  const n = await ev('slides.length');
  let problems = 0;
  for (let i = 0; i < n; i++) {
    const [title, bad, short] = await ev(`(()=>{show(${i});const s=slides[cur],st=stage.getBoundingClientRect(),k=st.width/1920,bad=[],short=[];
      s.querySelectorAll('.p,.ab,.m,table,ul,pre,.n,.t,.l').forEach(e=>{const b=e.getBoundingClientRect();
        if(b.bottom>st.bottom+1||b.right>st.right+1)bad.push((e.className||e.tagName)+':overflow');
        if(e.classList.contains('m')&&e.scrollWidth>e.clientWidth+2)bad.push('m:clip');});
      s.querySelectorAll('li,p,td').forEach(e=>{if(e.querySelector('ul,table,li'))return;const r=document.createRange();r.selectNodeContents(e);
        const rs=[...r.getClientRects()].filter(x=>x.width>1),tops=[...new Set(rs.map(x=>Math.round(x.top)))].sort((a,b)=>a-b);if(tops.length<2)return;
        const w=rs.filter(x=>Math.round(x.top)===tops[tops.length-1]).reduce((a,x)=>a+x.width,0);if(w/k<200)short.push(Math.round(w/k)+'px:'+e.textContent.slice(0,30));});
      return [s.querySelector('h1,h2').textContent,bad.join(', '),short.join(' | ')]})()`);
    if (bad) { problems++; console.log(`BAD   ${i + 1} ${title}: ${bad}`); }
    if (short) console.log(`SHORT ${i + 1} ${title}: ${short}`);
    if (!titles.length || titles.includes(title)) {
      const shot = await send('Page.captureScreenshot', { format: 'png' });
      writeFileSync(`${out}/s${String(i + 1).padStart(2, '0')}.png`, Buffer.from(shot.data, 'base64'));
    }
  }
  console.log(`checked ${n} slides, ${problems} with overflow or clipping`);
  ws.close();
} finally {
  proc.kill();
  rmSync(profile, { recursive: true, force: true });
}
