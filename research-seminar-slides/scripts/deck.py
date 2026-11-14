"""研究発表スライド（1920×1080 の HTML）を組み立てる小さなライブラリ。

使い方は references/html-deck.md を参照。発表ごとの build.py で次のように使う。

    from deck import Deck, ul, hd, panel, svg, box, lbl
    d = Deck(title='論文名 紹介')
    d.slide('手法の概要', ul('入力の形', '問題になる箇所', '変換の考え方'), note='発表者ノート')
    d.build('index.html')

数式は d.m(r'...') で書き、ビルド時に KaTeX でサーバー側描画する（KATEX_DIR に katex パッケージのディレクトリを渡す）。
日本語は BudouX で文節ごとに <wbr> を入れる（uv run --with budoux python build.py）。
"""
import base64, html, json, os, re, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / 'assets' / 'template.html'
INK = '#1a1a1a'

ul = lambda *items: '<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
hd = lambda t: f'<p class="hd">{t}</p>'
col = lambda c, t: f'<span style="color:{c}">{t}</span>'
al = lambda *lines: r'\begin{aligned}' + r'\\[6pt]'.join(lines) + r'\end{aligned}'


def panel(why, *items, x=1040, w=830, top=165):
    """右の説明列。x と w は発表全体で固定し、ページを送っても位置が動かないようにする。"""
    head = f'<p class="why">{why}</p>' if why else ''
    return f'<div class="p" style="left:{x}px;top:{top}px;width:{w}px">{head}' + ''.join(items) + '</div>'


def note_text(text, x=1040, top=836, w=830):
    """余白の ※ 注記。本文より小さいが 30px は下回らない。パネルの中に入れるときは x, top をパネル基準にする。"""
    return f'<div class="ab" style="left:{x}px;top:{top}px;width:{w}px;font-size:30px;line-height:1.4;color:var(--mute)">{text}</div>'


_svg_id = [0]


def svg(edges, style=None):
    """辺を折れ線で描く。edges: 名前 -> [(x, y), ...]。style: 名前 -> (色, 太さ)。

    矢印の marker の id は呼び出しごとに変える。同じ svg 文字列を 2 枚のスライドで使い回すと
    id が重複し、非表示のスライド側の marker が参照されて矢印の先が消える。図は毎回この関数で作る。
    """
    style = style or {}
    _svg_id[0] += 1
    sid = _svg_id[0]
    colors = list(dict.fromkeys([INK] + [v[0] for v in style.values()]))
    out = ['<svg class="edges" viewBox="0 0 1920 1080" aria-hidden="true"><defs>']
    for i, c in enumerate(colors):
        out.append(f'<marker id="mk{sid}x{i}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" '
                   f'markerWidth="20" markerHeight="20" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    out.append('</defs>')
    for k, pts in edges.items():
        c, w = style.get(k, (INK, 3))
        d = ' '.join(f'{x},{y}' for x, y in pts)
        out.append(f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="{w}" marker-end="url(#mk{sid}x{colors.index(c)})"/>')
    out.append('</svg>')
    return ''.join(out)


def box(cx, top, label, kind='', w=260, h=76):
    """図のノード。kind は template.html の .n.<kind>（focus, hl1, hl2, em, dash, dim）。"""
    return f'<div class="n {kind}" style="left:{cx - w // 2}px;top:{top}px;width:{w}px;height:{h}px">{label}</div>'


def lbl(x, y, text, color='#4b5563'):
    """辺のラベル（分岐の真偽、辺の名前など）。線や箱に重ならない位置に置く。"""
    return f'<div class="l" style="left:{x}px;top:{y}px;color:{color}">{text}</div>'


def img(path, style='', alt='図'):
    b = base64.b64encode(Path(path).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{b}" alt="{alt}" style="{style}">'


def figure_of(h):
    """辺とノードの位置。連続するスライドでこれが同じなら、同じ図の別のコマとして 1 ページに数える。"""
    edges = re.findall(r'points="([^"]*)"', h)
    nodes = re.findall(r'class="n [^"]*" style="left:(-?\d+)px;top:(-?\d+)px;width:(\d+)px', h)
    centers = tuple((int(l) + int(w) // 2, int(t)) for l, t, w in nodes)
    return (tuple(edges), centers) if edges and nodes else None


class Deck:
    def __init__(self, title, steps=None):
        self.title, self.steps, self.slides, self.maths = title, steps, [], []

    def m(self, tex, block=True):
        """KaTeX の数式。block なら 1 行の式として置く。"""
        self.maths.append(tex)
        t = f'@@{len(self.maths) - 1}@@'
        return f'<div class="m">{t}</div>' if block else f'<span class="mi">{t}</span>'

    def crumb(self, step, steps):
        steps = steps or self.steps
        if step is None or not steps:
            return ''
        return '<div class="crumb">' + ' → '.join(f'<b>{s}</b>' if j == step else s for j, s in enumerate(steps)) + '</div>'

    def slide(self, title, body, note='', step=None, steps=None, cls='', hidden=False):
        """hidden=True のスライドは、ナビゲーションの hidden ボタンを押すまで出さない（補助の説明用）。"""
        self.slides.append(dict(title=title, note=note, hidden=hidden,
                                html=f'<section class="s {cls}"><h2>{title}</h2>{self.crumb(step, steps)}{body}</section>'))

    def cover(self, title, *lines, note=''):
        body = ''.join(f'<p>{x}</p>' for x in lines)
        self.slides.append(dict(title=title, note=note, hidden=False, html=f'<section class="s cover"><h1>{title}</h1>{body}</section>'))

    def _render_math(self, katex_dir):
        if not self.maths:
            return [], ''
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf8') as f:
            json.dump(self.maths, f, ensure_ascii=False)
            src = f.name
        js = (f"const k=require({json.dumps(str(katex_dir / 'katex.min.js'))});const fs=require('fs');"
              f"const a=JSON.parse(fs.readFileSync({json.dumps(src)},'utf8'));"
              "console.log(JSON.stringify(a.map(t=>k.renderToString('\\\\displaystyle '+t,{throwOnError:true,strict:false,output:'html'}))));")
        try:
            out = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)
        finally:
            os.unlink(src)
        css = (katex_dir / 'katex.min.css').read_text()

        def font(mo):
            p = katex_dir / 'fonts' / mo.group(1)
            return 'url(data:font/woff2;base64,' + base64.b64encode(p.read_bytes()).decode() + ') format("woff2")'
        css = re.sub(r'url\(fonts/([\w-]+\.woff2)\) format\("woff2"\)(?:,url\([^)]*\) format\("[^"]*"\))*', font, css)
        return out, css

    def build(self, out_path, katex_dir=None, template=TEMPLATE):
        katex_dir = Path(katex_dir or os.environ.get('KATEX_DIR', ''))
        if self.maths and not (katex_dir / 'katex.min.js').exists():
            raise SystemExit('KATEX_DIR に katex パッケージの dist（katex.min.js のあるディレクトリ）を指定する')
        rendered, css = self._render_math(katex_dir)
        import budoux
        parser = budoux.load_default_japanese_parser()
        ja = re.compile('[ぁ-んァ-ヶ一-龠]')

        def phrases(h):
            parts = re.split(r'(<[^>]*>|@@\d+@@)', h)
            return ''.join(p if i % 2 or not ja.search(p) else '<wbr>'.join(parser.parse(p)) for i, p in enumerate(parts))

        page, prev = 0, None
        for s in self.slides:
            fig = figure_of(s['html'])
            if fig is None or fig != prev:
                page += 1
            s['page'], prev = page, fig
        body = ''
        for i, s in enumerate(self.slides):
            h = re.sub(r'@@(\d+)@@', lambda mo: rendered[int(mo.group(1))], phrases(s['html']))
            attrs = f'{"" if i == 0 else "hidden "}data-page="{s["page"]}"' + (' data-opt="1"' if s['hidden'] else '')
            body += h.replace('<section class="s', f'<section {attrs} data-note="{html.escape(s["note"], quote=True)}" class="s', 1) + '\n'
        tpl = Path(template).read_text()
        Path(out_path).write_text(tpl.replace('<!--TITLE-->', html.escape(self.title)).replace('/*KATEX*/', css).replace('<!--SLIDES-->', body))
        shown = [s for s in self.slides if not s['hidden']]
        pages = len(dict.fromkeys(s['page'] for s in shown))
        print(f'{len(self.slides)} slides, {pages} pages (hidden を除く), {Path(out_path).stat().st_size // 1024} KB')
