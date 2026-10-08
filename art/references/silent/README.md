# Silent — 公式参照索引

ユーザー指定のデザイン目標は [参照MODの選択画面](mod-reference/kaguya-silent-raven/README.md)。公式設定の資料と目的を分けて管理する。下記の調査時点の制作提案に優先する現行方針は [v0.3](../../../docs/design/characters/review-v03.md)。

確認日: 2026-10-08。来歴・取得日・公式性・版・描画対象・読み取れる特徴・SHA256・派生関係は [sources.json](sources.json) を参照。設定と制作提案は [調査本文](../../../docs/research/characters/ironclad-silent.md)。ファンアートは含めていない。

## 制作へ渡す主参照３原典

| 資料 | 用途 | 状態／注意 |
| --- | --- | --- |
| [現行公式 Steam merchant 全身](official/gameplay/silent-merchant-steam.jpg) | 緑の外套に覆われた全身、腕組み、角のある長い頭蓋骨、緑の眼光、手足の巻き布、背面の長い骨 | 現行ストア公開画像。撮影 build 不明。身体を隠す量の基準 |
| [公式５人 lineup](../shared/official/character-lineup.png) | **左から２番目**の頭部と外套、頭蓋骨の鼻先・眼窩・角、骨の装飾 | 2026-02 の発売期の公式画像。頭部基準 |
| [公式 animation GIF](official/gameplay/silent-animation-preview.gif) | 波形の２本の短剣、構え、外套が広がり身体を再び隠す動作 | 2024-10 の開発プレビュー。現行版の最新モーションとは称さない |

GIF から [frame055 の構え](official/gameplay/silent-animation-preview-frame055.png)、[frame080 の攻撃](official/gameplay/silent-animation-preview-frame080.png)、[フレーム一覧](official/gameplay/silent-animation-contact.png) を参照用にデコードした。原本を保持し、切り抜き・描き直し・色の変更はしていない。３派生ファイルを別原典として数えない。

## 全身の現行動作を補強する１点

[現行公式 Steam 協力戦](../regent/official/gameplay/regent-coop-steam.jpg) の**前景中央の緑の人物**を参照。短剣の手が先に動き、大きな外套が身体を包む。原本は Regent 資料に保持されているので重複保存していない。発売期の [協力戦 GIF](../ironclad/official/gameplay/sts2-coop-terror-eel.gif) と [フレーム一覧](../ironclad/official/gameplay/sts2-coop-terror-eel-contact.png) も同じ読み取りを補助する。

## 歴史・補助資料

- [StS2 初期コンセプト集](official/development/silent-concepts.png): StS1 風の参照、初期代案、シェーディング比較を含む。画像内の `Nemesis Skull` 表記は有用だが、すべてを現行衣装へ統合しない。公式記事はより cartoon 的な別方向の可能性だったと明記する。
- [v0.107.1 選択頭部アイコン](official/game-assets/silent-char-select-v0.107.1.webp): 132×195 の小さい頭部。2026-06 ローカル配布版。原 [ctex](official/game-assets/silent-char-select-v0.107.1.ctex) を保持。全身選択背景ではない。

## ゲーム内テキスト

- [英語の関係キー](official/game-assets/silent-localization-eng-v0.107.1.json)
- [日本語の関係キー](official/game-assets/silent-localization-jpn-v0.107.1.json)

選択説明は塔の外から来た**女性狩人**で、ナイフと毒を使う。代名詞は `she / her`。Timeline は**物語のネタバレを含む**。`SILENT6_EPOCH` は、haunter を狩った後、Sisters がその頭蓋骨を彼女へ儀礼的に被せたと記す。したがって本人をスケルトン／リッチへ変換せず、頭蓋骨を狩りと儀礼に結び付いた装具として保つ。元 JSON resource の byte 範囲と MD5 を記録。ローカル v0.107.1 は最新版と称さず、画面での表示到達は未検証。

## このMODで保つ核

元々女性なので、画風のポップ化を中心にする。大きい緑の外套とフード、長い角つきの頭蓋骨、巻き布、波形短剣、背面の骨、毒と無言の狩りを保つ。短い三つ編みを骨の背面装飾の代わりにしない。明るい笑顔・素顔・肌の多いドレス・誘惑するポーズではなく、首と手首の微細な動き、外套の形と素早い重心移動で親しみを表す。
