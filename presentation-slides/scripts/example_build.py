"""deck.py の使い方の例。1 つの図を同じ座標のまま 2 コマで進め、式、注記、hidden のスライドを置く。

    KATEX_DIR=<katex の dist> uv run --with budoux python example_build.py out/index.html
"""
import sys
from deck import Deck, ul, hd, panel, svg, box, lbl, note_text, al, col

C1, C2, MUTE = '#1d5fd1', '#c2410c', '#4b5563'
d = Deck(title='例：二分探索', steps=['準備', '探索', '終了'])
d.cover('例：二分探索', '発表者名', 'ゼミ', note='表紙。題目と発表者だけを置く。')
d.slide('二分探索の考え方', ul('整列済みの配列が前提', '範囲の中央と比較', '比較のたびに範囲を半分に'),
        note='タイトルは名詞句で、サブタイトルは付けない。箇条は短い体言止め。', cls='txt')

# 同じ図を毎回 svg() から作る（使い回すと矢印の marker の id が重複する）
E = {'ab': [(240, 226), (240, 300)], 'bc': [(240, 376), (240, 450)], 'cd': [(370, 488), (680, 488), (680, 530)],
     'ce': [(240, 526), (240, 600)], 'ea': [(110, 638), (40, 638), (40, 188), (110, 188)], 'af': [(370, 188), (550, 188)]}


def flow(kinds=None, style=None):
    kinds = kinds or {}
    return (svg(E, style) + box(240, 150, 'lo ≤ hi', kinds.get('a', '')) + box(240, 300, 'mid を計算', kinds.get('b', ''))
            + box(240, 450, 'a[mid] = x', kinds.get('c', '')) + box(680, 530, '見つかった', kinds.get('d', ''))
            + box(240, 600, '範囲を半分に', kinds.get('e', '')) + box(680, 150, '見つからない', kinds.get('f', ''))
            + lbl(254, 240, '真') + lbl(440, 140, '偽') + lbl(510, 440, '真') + lbl(254, 540, '偽'))


d.slide('探索：中央の計算', flow({'b': 'focus'}, {'ab': (C1, 6)})
        + panel('知りたいこと：どこと比較するか', d.m(r'\mathit{mid}=\left\lfloor\frac{\mathit{lo}+\mathit{hi}}{2}\right\rfloor'),
                ul(col(C1, 'lo、hi：探索範囲の両端'), '端数は切り捨て')),
        note='各ステップに「何のための計算か」を 1 行で置く。', step=1)
d.slide('探索：範囲の更新', flow({'c': 'hl2', 'e': 'focus'}, {'ce': (C2, 6)})
        + panel('知りたいこと：次にどこを探すか', d.m(al(r'a[\mathit{mid}]<x&\Rightarrow\ \mathit{lo}=\mathit{mid}+1', r'a[\mathit{mid}]>x&\Rightarrow\ \mathit{hi}=\mathit{mid}-1')),
                ul('比較のたびに範囲が半分', col(MUTE, '等しければ終了')))
        + note_text('※ 同じ図が続くコマは 1 ページに数える（下の番号の括弧がコマ）'),
        note='前のスライドと同じ座標なので、同じページの 2 コマ目になる。', step=1)
d.slide('補足：計算量', ul('比較の回数は高々 ⌈log₂(n+1)⌉', '範囲が空になれば見つからない'),
        note='hidden ボタンを押したときだけ出す補足。', cls='txt', hidden=True)
d.slide('まとめ', hd('二分探索') + ul('中央と比較して範囲を半分に', '整列済みが前提'), note='区切りのまとめ。', cls='txt')
d.build(sys.argv[1] if len(sys.argv) > 1 else 'index.html')
