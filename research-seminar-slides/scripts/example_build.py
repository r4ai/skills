"""deck.py の使い方の例。1 つの CFG を同じ座標のまま 2 コマで解き、式と注記と hidden のスライドを置く。

    KATEX_DIR=<katex の dist> uv run --with budoux python example_build.py out/index.html
"""
import sys
from deck import Deck, ul, hd, panel, svg, box, lbl, note_text, al, col

MUST, MAY, NO = '#1d5fd1', '#c2410c', '#4b5563'
d = Deck(title='例：部分冗長性の紹介', steps=['解析', '複製', 'コード移動'])
d.cover('例：部分冗長性の紹介', '発表者名', 'ゼミ 2026-11-15', note='表紙。題目と発表者だけを置く。')
d.slide('PRE の目的', ul('一部の経路で冗長な計算の除去', 'コード移動で計算を置き直し', '複製で経路を分離'),
        note='タイトルは名詞句で、サブタイトルは付けない。箇条は短い体言止め。', cls='txt')

# 同じ図を毎回 svg() から作る（使い回すと矢印の marker の id が重複する）
E = {'12': [(370, 188), (680, 188), (680, 230)], '13': [(240, 226), (240, 360)], '23': [(680, 306), (680, 398), (370, 398)],
     '34': [(240, 436), (240, 520)]}


def cfg(kinds=None, style=None):
    kinds = kinds or {}
    return (svg(E, style) + box(240, 150, '1: if (A)', kinds.get('1', '')) + box(680, 230, '2: x = a+b', kinds.get('2', ''))
            + box(240, 360, '3: S', kinds.get('3', '')) + box(240, 520, '4: y = a+b', kinds.get('4', ''))
            + lbl(510, 140, '真') + lbl(254, 280, '偽'))


avail = lambda n: r'\mathrm{AVAIL}_{\text{入口}}(%s)' % n
may = r'\textcolor{%s}{\mathsf{May}}' % MAY
d.slide('AVAIL の計算：ノード 3', cfg({'3': 'focus'}, {'23': (MUST, 6)})
        + panel('知りたいこと：ここに a+b の値が届くか', d.m(al(avail(3) + r'&=\mathrm{Must}\sqcap\mathrm{No}', r'&=' + may)),
                ul(col(MUST, '2→3：計算済みの経路'), col(NO, '1→3：未計算の経路'), 'ここで May が発生')),
        note='各ステップに「何のための計算か」を 1 行で置く。', step=0)
d.slide('AVAIL の計算：ノード 4', cfg({'3': 'cmp', '4': 'focus'})
        + panel('知りたいこと：4 で a+b を再利用できるか', d.m(avail(4) + '=' + may), ul('3 の値をそのまま継承', '一部の経路だけ計算済み'))
        + note_text('※ 同じ図が続くコマは 1 ページに数える（下の番号の括弧がコマ）'),
        note='前のスライドと同じ座標なので、同じページの 2 コマ目になる。', step=0)
d.slide('補足：なぜ 3 値か', ul('2 値では一部の経路と全経路なしを区別不可', 'May だけが複製の対象'),
        note='hidden ボタンを押したときだけ出す補足。', cls='txt', hidden=True)
d.slide('まとめ', hd('PRE') + ul('3 値の解析で止まる場所を特定', '止まる場所だけを複製'), note='区切りのまとめ。', cls='txt')
d.build(sys.argv[1] if len(sys.argv) > 1 else 'index.html')
