# Defect 公式参照

取得・画像確認日: 2026-10-08。設定の整理は [調査メモ](../../../docs/research/characters/defect-world.md)。直接の取得URL、掲載ページ、公式性、新旧の分類、派生操作、寸法とSHA-256は [sources.json](sources.json) に記録した。

## 現行の造形を決める資料

| ファイル | 公式性・版 | 読み取れること |
| --- | --- | --- |
| [sts2-combat-overgrowth.jpg](official/gameplay/sts2-combat-overgrowth.jpg) | Mega Critの現行Steamストア掲載。撮影ビルド不明 | 全身、大きい前腕と脚部・足、暗い関節、丸い青い外殻、首布、爪状の機械の手、身体から離れるオーブ |
| [sts2-lineup-defect-crop.png](official/key-art/sts2-lineup-defect-crop.png) | 2026-02-19公式発売日告知の５人画像から矩形切り出し | 不均等な金属顔板、大小二つの青い円形部品、首布と胴。左右端の他キャラ断片は参照対象外 |
| [sts2-trailer-defect-orbs-099500.png](official/gameplay/sts2-trailer-defect-orbs-099500.png) | 公式Early Accessトレーラー99.5秒のデコード | 全身姿勢、身体の上の弧に並ぶ雷・氷・闇のオーブ。UI・敵は生成対象外 |
| [sts2-trailer-defect-cinematic-095500.png](official/key-art/sts2-trailer-defect-cinematic-095500.png) | 同トレーラー95.5秒のデコード | 身を低く構える重さ、動く布、装甲の背面/斜め後ろ側。顔の正面資料ではない |

顔の原本は [shared/official/character-lineup.png](../shared/official/character-lineup.png)。原本を維持し、切り出しは描き直していない。

## 原作からの継承を確かめる資料

| ファイル | 公式性・版 | 読み取れること |
| --- | --- | --- |
| [sts1-defect-introduction.jpg](official/key-art/sts1-defect-introduction.jpg) | Mega CritのWeekly Patch 27、2018-05-31の公式告知画像 | 旧作でも大小レンズ、青い胴と布、分節四肢があった。植物を見るような穏やかな機械のポーズ |
| [sts1-defect-promo-anailis.png](official/key-art/sts1-defect-promo-anailis.png) | 旧作の公式プロモ絵。制作したAnailis Dortaの一次インタビューに掲載、Mega Critもそのインタビューへリンク | 機械の顔と手、オーブ技術、布と外殻の対比。カード/選択画面寄りの描き込み。現行の形を優先する |

旧作資料は開発途中のStS2原画ではない。`official/development/` には採用できるDefect個別の公式開発原画を今回は置いていない。公式サイトのCommunity Cornerや推測絵は、このフォルダの現行基準に含めていない。

Anailisのプロモ絵は`.png`のURLでWebP形式のバイトが配信された。取得原本を [sts1-defect-promo-anailis.webp](official/key-art/sts1-defect-promo-anailis.webp) に残し、ツール用に実際のPNGへデコードした。リサイズ・描き直しはしていない。

## 動画と文章の原本管理

[sts2-early-access-trailer-video720.mp4](official/gameplay/sts2-early-access-trailer-video720.mp4) はSteam公式HLSの720p映像を再エンコードせずMP4へリマックスした参照元。映像のみで音声は保存していない。二つのPNGはこの保存動画から抽出した。公開元は [Mega Crit公式発売告知](https://www.megacrit.com/news/2026-02-19-release-date-trailer/) / [公式YouTubeトレーラー](https://www.youtube.com/watch?v=PW22jwFNxU8) / [Steamストア](https://store.steampowered.com/app/2868840/Slay_the_Spire_2/)。

ゲーム内文章はインストール済みv0.107.1 / commit 59260271 / 2026-06-18のPCKから対象リソースを読んだ。ゲームを変更・更新・実行していない。対象キーとbyte offset、長さ、MD5一致、SHA-256はmanifestに記録。公開画像の撮影版とは区別する。

新作の代名詞はit/its、オーブの定義はLightning/Frost/Dark/Plasma/Glass。`robot wizard` はSteamに転載された報道記事の表現だったため、開発者の公式設定として採用しない。

ここに置いた公式画像は調査と生成の参照用。生成したMOD用画像とは別に管理する。
