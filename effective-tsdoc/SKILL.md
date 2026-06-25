---
name: effective-tsdoc
description: TypeScript の公開 API や複雑な helper に TSDoc を書く、または既存コメントを TSDoc として改善するときに使う。@param、@returns、@remarks、@example、@defaultValue、@see などを効果的に使い、説明文だけで終わらせない。
---

# Effective TSDoc

TSDoc は「何となく説明するコメント」ではなく、API 契約を読むための構造化ドキュメントとして書く。

## 基本方針

- 公開 API には、概要文に加えて必要なタグを書く
- 関数とメソッドには `@param` と `@returns` を省略しない
- 注意点、制約、設計理由は本文に混ぜず `@remarks` に分ける
- 使い方が誤読されやすい API には `@example` を置く
- 既定値があるオプションには `@defaultValue` を置く
- 関連型や関連メソッドがある場合は `@see {@link ...}` でつなぐ

## 書き分け

- 概要文：一文で「何をするか」を書く
- `@remarks`：スコープ規則、制約、内部設計、限界を書く
- `@param`：型から読めない意味、前提、単位、同一性条件を書く
- `@returns`：正常時の値だけでなく、undefined や空配列を返す条件を書く
- `@example`：コンパクトに、実際の呼び出し形が分かるコードを書く

## 避けること

- 実装をそのまま言い換えるだけのコメント
- `@param value 値` のように型名や変数名を反復するだけの説明
- 公開 API でタグを使わず、長い地の文だけで済ませること
- 内部 helper すべてに機械的に長い TSDoc を付けること。複雑なもの、契約が読みにくいものを優先する
