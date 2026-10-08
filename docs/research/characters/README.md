# キャラクター設定と世界観の調査

[文書案内](../../README.md) / [調査担当と出力先](../README.md) / [参照画像](../../../art/references/README.md)

GPT-6.1 sol / xhigh の３担当が、公式文章・公式画像・ローカルゲームの一次資料を照合した。下の概要は、画像生成と動作設計に必要な部分に絞っている。物語の詳細は各レポートのネタバレ節に分離している。

**制作への適用:** 公式の事実と、その見た目を文字どおり維持する制作判断は別。ユーザーはv0.2を「女性化・擬人化が足りない」と却下した。各調査書の原型を保つ制作提案は記録として残すが、現行の [v0.3の翻案方針](../../design/characters/review-v03.md) を優先する。骨・機械・星形の特徴は、人の顔や身体を持つ女性キャラの衣装・装備・所作へ意味を保って翻訳する。

| 対象 | 保存すべき特徴 | 調査本文 | 参照画像 |
| --- | --- | --- | --- |
| アイアンクラッド | 本人の意志に反して戦う最後の兵士。閉じた金銅色の仮面、銀灰色の髪、重い鎧、剣と炎 | [Ironclad / Silent](ironclad-silent.md) | [索引](../../../art/references/ironclad/README.md) |
| サイレント | 既に女性の狩人。儀礼に由来する頭蓋骨、緑の外套、巻き布、波形短剣、背面の骨、毒 | [Ironclad / Silent](ironclad-silent.md) | [索引](../../../art/references/silent/README.md) |
| リージェント | 単眼で橙色の異星人。星の玉座の継承者。尊大さと滑稽さ、玉座、従者、浮遊剣 | [Regent / Necrobinder](regent-necrobinder.md) | [索引](../../../art/references/regent/README.md) |
| ネクロバインダー | 既に女性のリッチ。骨の本体、長衣、鎌、炎、復讐の意志、独立した相棒オスティ | [Regent / Necrobinder](regent-necrobinder.md) | [索引](../../../art/references/necrobinder/README.md) |
| ディフェクト | 生存のため自己改造するオートマトン。不均等な顔、大小のレンズ、大きい四肢、青い胴と布、オーブ | [Defect / 世界観](defect-world.md) | [索引](../../../art/references/defect/README.md) |
| 世界観・画風 | 奇妙さ、不穏さ、遊び心、明快な形と色、顔を覆うキャラの造形 | [Defect / 世界観](defect-world.md) | [索引](../../../art/references/world/README.md) |

## 公式の公開資料

- [Mega Crit — 美術とキャラデザイン方針](https://www.megacrit.com/news/2024-10-02-neowsletter-issue-3/)
- [Mega Crit — Regent紹介](https://www.megacrit.com/news/2025-12-11-neowsletter-issue-17/)
- [Mega Crit — NecrobinderとOsty紹介](https://www.megacrit.com/news/2025-10-16-neowsletter-issue-15/)
- [Mega Crit — ５キャラの発売期画像・映像](https://www.megacrit.com/news/2026-02-19-release-date-trailer/)

ゲーム内設定の引用元キー、取得範囲、MD5・SHA-256と画像の来歴は、各キャラの `sources.json` と詳細レポートにある。ローカル版は **v0.107.1 / commit 59260271 / 2026-06-18**。2026-10の最新ビルドや、全場面での実プレイ表示は未確認。

## 訂正と判断上の注意

- Steam掲載だけでは一次資料とは限らない。以前のDefectの「robot wizard」は外部報道の転載だったため、公式設定の根拠から外した。
- 擬人化では元の身体や顔の形が変わる。重要な役割・装備・色・能力・人物像がどこへ翻訳されたかを追い、元の特徴が単に消えた部分を確認する。翻案による外観を新しい公式設定とは称さない。
- 女性化は今回のMODの解釈。元々女性のキャラを変更したり、全員の年齢・体型・髪型を揃えたりする必要はない。
- 公式記事内のファンアートは現行原画と区別した。開発途中・旧作の画像も、現行の設計図として一括採用しない。

改訂デザインの提案は [review-v03.md](../../design/characters/review-v03.md) にまとめている。
