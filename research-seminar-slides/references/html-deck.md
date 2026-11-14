# HTML の発表資料の組み立て

## 構成

発表ごとのディレクトリに次を置く。

- `build.py`：`scripts/deck.py` を読み込み、スライドを順に `d.slide(...)` で積んで `d.build('index.html')` する
- `fig/`：論文から切り出した図（PNG）。`img()` で data URI として埋め込む
- `index.html`：組み立てた結果。これを公開する

部が多い発表では、部ごとに Python のファイルを分けて `exec` で読み込むと見通しがよい。

```sh
KATEX_DIR=<katex の dist> uv run --with budoux python build.py
node <skill>/scripts/check_deck.mjs index.html <画像の出力先>
```

KaTeX は npm の `katex` パッケージ（`katex.min.js`、`katex.min.css`、`fonts/`）を使う。
フォントは CSS に data URI で埋め込むので、公開先に外部の読み込みは要らない。

## 画面

- 舞台は 1920×1080 の固定座標で作り、表示領域に合わせて `transform: scale()` で縮める。図の座標を画面の大きさに依存させない。
- 図は左（x ≈ 60〜900）、説明の列は右（`panel()` の既定 x=1040、幅 830、上端 165）に置く。説明の列の位置は全ページで変えない。
- タイトルは 60px、本文 44〜48px、ノードとラベル 36px、表 42〜46px、数式 46px（`.big` で 56px）、注記 30px。
- ノードの種類（`.n.focus`、`.n.cmp`、`.n.must` など）と色は `template.html` の CSS 変数で決める。色の意味（確定、一部、なし）を発表全体で固定する。

## 日本語の改行

次の三つを組み合わせる。

- BudouX で文節の切れ目に `<wbr>` を入れる（`deck.py` がビルド時に行う）
- CSS で `word-break: keep-all; word-break: auto-phrase; line-break: strict; overflow-wrap: anywhere; text-wrap: pretty;` を指定し、`lang="ja"` を付ける
- 見出しには `text-wrap: balance` を付ける。数式、ノード、コードには `word-break: normal` を戻す

それでも 1〜3 文字だけ次の行に落ちる箇条は、`check_deck.mjs` が SHORT として報告する。言い換えて 1 行に収める。

## 同じ図のコマと hidden

- 連続するスライドで、辺の折れ線とノードの中心の座標がすべて同じなら、同じページの別のコマとして数える。番号は `13 / 53（2/4）` のように出る。図のないスライドは 1 枚で 1 ページになり、同じ図のまとまりを区切る。
- `slide(..., hidden=True)` のスライドは、ナビゲーションの hidden ボタンを押すまで出さない。前へ・次へは隠れたスライドを飛ばし、番号は表示中のスライドだけで振り直す。

## 落とし穴

- **矢印の先が消える**：同じ `svg()` の結果を 2 枚で使い回すと marker の id が重複し、非表示のスライド側の marker が参照される。図は毎回関数で作る。
- **スライドが重なって表示される**：CSS の `display` 指定が `hidden` 属性を上書きする。`[hidden] { display: none !important; }` を入れる。
- **headless のプレビューが止まる**：Google Fonts の `<link>` の読み込みが終わらない。検査用のページでは外す（`check_deck.mjs` が行う）。
- **KaTeX で使えないマクロ**：`\bigsqcap` はない。`\mathop{\Large\sqcap}\limits` で代える。マクロの引数に `#` を含む色を渡さず、色は展開して書く。
- **長い式の改行で右端が切れる**：`aligned` の 1 行目を `&` で終えると、2 行目以降が右の列から始まり、かえって右へ伸びる。行頭に `&` を置いて全行を左揃えにする。
- **パネルの中の注記の位置**：`panel()` に渡した要素の `position:absolute` は、パネル基準の座標になる。画面基準で置くなら、パネルの外に足す。
- **既定で隠すスライドへの参照**：hidden にしたスライドで定義した語を、表示されるスライドで前提にしない。

## 検査

`check_deck.mjs` は hidden ボタンを押した状態で全コマを表示し、次を報告する。

- BAD：舞台の外へ出た要素（overflow）、数式の右端の切れ（clip）
- SHORT：最終行が 200px 未満の箇条や段落

タイトルを引数に渡すと、そのコマの画像だけを保存する。変えたスライドは必ず画像で見る。
自動検査は、ラベルと線の重なりや、図の意味の誤りを見つけない。
