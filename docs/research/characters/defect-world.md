# Defect と Slay the Spire 2 世界観 — 一次資料調査

> 制作提案の扱い: この調査時点の原型維持の提案は、後のユーザーレビューで擬人化不足と判断された。公式事実は資料として採用し、外観の現行方針は [v0.3](../../design/characters/review-v03.md) を参照。

確認日: 2026-10-08。画像生成・実装・validator評価は行っていない。公式の文章、画像からの観察、MOD用の解釈を区別する。

公開資料は確認日時点の公式サイト・Steamストア、ゲーム内文章はインストール済み **v0.107.1 / commit 59260271 / 2026-06-18** に固定した。公開画像の撮影ビルドは不明であり、このローカル版と同一とは扱わない。PCKは他担当が調べた索引の範囲を直接読み、原本を変更していない。

## 結論となる short character bible

| 項目 | 確認できた核 | 制作への意味 |
| --- | --- | --- |
| 存在 | 生存のために自分を改造し続けるオートマトン。戦闘が必要な場合にオーブ技術を展開する | 「人間の女性が機械のスーツを着る」構造へ置換すると設定の核が消える |
| 性別・呼称 | 現行英語のキャラ定義は **it / its**。公式に女性であるという確認はない | 女性化は本MODの解釈として明記。女性的な身体部位を必須条件にしない |
| 動機 | 壊れながらも生き延び、答えを求める。仲間への思いを持つ | 冷たい無感情な端末にも、こちらに微笑むだけの美少女にも限定しない |
| 人格の根拠 | 自分の機能・存在意義を考える。Flaw と友達になる。会話には好奇心、照れ、恐れ、決意を伴うビープがある | 顔を人間に変えなくても、機械のふるまいに感情を宿せる |
| 視覚の核 | 不均等な金属の顔板、大小二つの青い円形レンズ、青い丸い胴、青い首布、金色の分節した四肢、暗色の露出した接続部 | 顔板とレンズを残した機械のまま、形と動きで女性として再解釈する |
| 戦闘の核 | 本体の動作と、身体から離れて並ぶオーブ。ローカル版の実用オーブ名は Lightning / Frost / Dark / Plasma / Glass | オーブをアクセサリーや髪飾りへ縮小しない。雷・氷・闇の三つを選ぶ場合も、公式全種類とは呼ばない |

文章の根拠: PCK内 `localization/{eng,jpn}/characters.json` の `DEFECT.description`、代名詞キー、`DEFECT.eventDeathPrevention`、`DEFECT.goldMonologue`。人格は `epochs.json` の `DEFECT3_EPOCH`、`DEFECT4_EPOCH` と `ancients.json` の Defect会話キー。取得範囲・offset・MD5・SHA-256は [Defect sources.json](../../../art/references/defect/sources.json) に記録した。

## 出自と物語の確定範囲

ローカル版の `DEFECT1_EPOCH.description` は、破損したコアと動きにくい四肢を持つ Defect が、他の構造物の装甲・部品で自分を修復する場面を描く。継ぎ合わせた機械という読みは、単なる衣装の趣味より強い根拠を持つ。

`DEFECT2_EPOCH.description` は Neow による復活と、創造主について答えを求めて上へ向かう動機を記す。ただしこのEpochの題は **Tricked** であり、Neow の言葉を全知の作者による事実認定に読み替えない。Ancient会話にも Architect、Factory、友人の修復への言及があるが、発言者の意図と真偽が絡むため、これだけで全起源を断定しない。

`DEFECT3_EPOCH`・`DEFECT4_EPOCH` の哲学的な問いと友情、`DARV.talk.DEFECT` の好奇心、`NONUPEIPE.talk.DEFECT` の照れ、`NEOW.talk.DEFECT` の決意、`VAKUU.talk.DEFECT` の恐怖は、機械としての感情表現を設計する一次根拠になる。各場面の機械音を、人間の口・眉・まつ毛がある証拠にはしない。

旧作からの復帰は [公式発売日告知](https://www.megacrit.com/news/2026-02-19-release-date-trailer/) と現行５人の画像が確認できる。旧作の [Weekly Patch 27: Hello World](https://steamcommunity.com/games/646570/announcements/detail/1667901382266210881) の公式画像、および制作した本人が公開した [Anailis Dorta の一次インタビュー](https://www.moregamesplease.com/art-in-boardgames/2025/5/27/anailis-dorta-amp-bruce-brenneise-slay-the-spire-art-in-board-games-76) の Defect公式プロモ絵にも、金属顔板・大小レンズ・青い胴・布・オーブがある。現在の姿への視覚的連続性は明瞭。旧作テキストにおける自我獲得の原因や、千年間の全経歴は今回確認していない。

**以前の出典の修正:** `robot wizard` は [2018年のSteamニュース集合ページ](https://store.steampowered.com/news/posts/?appids=646570&enddate=1526311185) に転載された PC Gamer / Rock Paper Shotgun の記事の表現であり、Mega Critの公式説明としては引用できない。Steam内でも `steam_community_announcements` と報道記事の配信元を区別する。

## 現行画像からの観察

| 部位 | 観察 | 生成で維持する点 |
| --- | --- | --- |
| 顔 | 金色の板に不均等な突起・切れ込み。大きい青い円形部品と上側の小さい青い円形部品。通常の左右一対の目ではない | 二枚のレンズの大小とずれ、板の輪郭を維持。機能を勝手に「目と口」と命名しない |
| 胴と首 | 膨らんだ青い外殻と暗い接続部。首の周囲に青い布が重なる | 丸い胴を女性の胸甲二枚や細腰へ分解しない。布と硬い殻の対比を残す |
| 四肢 | 大きな前腕、分節した膝・すね・足先。関節は暗く細いが、四肢全体は重量を持つ | 「細い機械の手足」だけに一般化しない。幅のある脚部と大きな足、機械の爪状の手を残す |
| 損傷・再構成 | 顔板の不均等さ、異なる形の装甲、露出する接続部 | 新品の均整の取れた女性型アンドロイドへ磨き切らない。傷を過度な汚しにする必要もない |
| オーブ | 本体より上に弧状に並ぶ独立した雷・氷・闇のオーブが、公式トレーラー99.5秒で見える | オーブの形・色・離れた配置が小さい表示でも読めるようにする |
| 動き | 公式トレーラー94–98秒では低く身構え、布が広がる。99–102秒は機械の身体の向きと独立したオーブ/VFXが協働する | 首かしげだけで固定せず、観察する時と戦闘する時の重さを分ける |

根拠: [現行Steam公式全身](../../../art/references/defect/official/gameplay/sts2-combat-overgrowth.jpg)、[現行顔の切り出し](../../../art/references/defect/official/key-art/sts2-lineup-defect-crop.png)、[公式トレーラー95.5秒](../../../art/references/defect/official/key-art/sts2-trailer-defect-cinematic-095500.png)、[公式トレーラー99.5秒](../../../art/references/defect/official/gameplay/sts2-trailer-defect-orbs-099500.png)。画像上の色を材質の厳密な設定として断定せず、金色/真鍮を思わせる色と呼ぶ。

## 世界観と画風の brief

Spireは千年間の休眠後、危険と謎を抱えて再び開いた場所。５人はそれぞれの動機と秘密を持ち、登り直す中で断片的な歴史と古い住民に出会う。これは [公式発売告知](https://www.megacrit.com/news/2026-02-19-release-date-trailer/) と [Steam公式説明](https://store.steampowered.com/app/2868840/Slay_the_Spire_2/) の基礎設定。全５人が不老で千年間同じ姿だった、という設定には拡張しない。Neow は [公式ストアの画面](../../../art/references/world/official/gameplay/sts2-neow-chamber.jpg) に **Mother of Resurrection (Exiled)** と表示される。復活と追放の位置づけは確認できるが、全体の真相は未確定。

[2024年10月のアートディレクション解説](https://www.megacrit.com/news/2024-10-02-neowsletter-issue-3/) は、暗い題材を残しながら、遊び心、明快な形、アニメーション、映画的な画面、読みやすい色を増やす方針を示す。同時に、元の世界の気味悪さと楽しさを継承し、顔を露出しすぎる人物や奇妙さが足りない怪物は馴染まないと説明する。初期のより漫画的なSilent案は探索であり、採用された完成形ではない。「ポップ」を極端なデフォルメや全員の美少女顔化と同一視しない。

旧作の絵も単一の描き方ではない。[Anailis / Bruce の一次インタビュー](https://www.moregamesplease.com/art-in-boardgames/2025/5/27/anailis-dorta-amp-bruce-brenneise-slay-the-spire-art-in-board-games-76) は、カード・イベント・選択画面などの描き込みの差を、共通する形と雰囲気で結び付けていたと説明する。Bruce は有機的・骨のような建築と画面内の読みやすさも語る。StS2の機械を背景から独立して読める形にする判断へ使える。

デザイン用の読み: [Terror Eel の共闘画面](../../../art/references/world/official/gameplay/sts2-coop-terror-eel.jpg) の多数の目と誇張された攻撃動作、[Symbiote画面](../../../art/references/world/official/gameplay/sts2-symbiote-event.jpg) の暗い有機物と大きな色面、Neowの丸い巨体と傷・異常な目を一緒に見ると、親しみと不穏さが同居する。どちらかだけに揃えない。この三点は現行公式掲載物で、各キャラの髪型や性格を追加する設定資料ではない。

## 女性化・ポップ化に使える解釈

以下は公式設定ではなく、今回の制作判断の候補。

- **機械の姿を保つ女性化を第一候補にする。** MOD内の解釈・呼称、布の流れ、細かな仕草で女性として読ませる。人間の顔、髪、胸の形を女性化の必須部品にしない。
- ポップさは青・金・暗い接続部の色面の整理、頭と胴の丸い形と四肢の角張った形の対比、オーブを見る丁寧な動作から作る。照れや好奇心の根拠はあるが、「首をかしげる＝女性」という固定観念にはしない。
- 感情は固定されたレンズの光、頭・胴の向き、間、機械の手の開き、布の遅れで表す案が可能。これらの具体的な動かし方はMOD側の演出案であり、公式仕様の写しではない。
- 感情豊かな機械としての親しみと、必要な時に身構える重さを両立させる。友人との関係を、こちらを見る誘惑する笑顔へ置換しない。

人間の顔を追加すると、特徴的なレンズ構成、壊れた構造物が自分を修復する存在、ビープで伝わる人格、原作の露出した顔を抑えた視覚言語が弱まる。この損失は、露出の少ない衣装に変更するだけでは解消しない。

## v0.1 / v0.2 仮案に対する修正点

| 対象 | 修正判断 |
| --- | --- |
| v0.1 の人型・ボブ・シアンの人間の瞳・微笑み | 公式の機械の顔を失うため、次の参照・造形の基礎から外す |
| v0.2 の非対称頭部・青い胴・布・機械の顔の維持 | 調査で支持できる。ただし顔の大小二部品と暗い接続部まで具体化する |
| v0.2 の「丸い胴と細い関節」 | 現行の大きい前腕・膝・足先を追記する。女性化のために四肢全体を細くすると原型が弱い |
| v0.2 の「首をかしげる仕草で女性的」 | 女性化の根拠にはしない。好奇心を示す演出候補として記述する |
| 性格の扱い | 照れ・好奇心・恐れ・決意・友情を機械のふるまいへ返す。「無表情な機械」も「常に柔らかく微笑む女性」も原文を十分に表さない |
| 新旧の扱い | 現行画像を形の基準、旧作プロモを継承の確認とする。旧作の傷・布の破れ・描き込みを新作必須形状にしない |

## 生成へ渡す資料の優先順

1. **現行全身** `official/gameplay/sts2-combat-overgrowth.jpg`: 姿勢、脚の太さ、足、胴、爪状の手、布の基準。
2. **現行顔** `official/key-art/sts2-lineup-defect-crop.png`: 板と大小レンズの基準。矩形切り出しの端に他キャラの断片があるため、中央のDefectのみを読む。共通原本は `../shared/official/character-lineup.png`。
3. **現行オーブ** `official/gameplay/sts2-trailer-defect-orbs-099500.png`: 身体から離れて弧を描く雷・氷・闇。UIや敵は生成対象外。
4. **動作・背面補助** `official/key-art/sts2-trailer-defect-cinematic-095500.png`: 低い重心と布・装甲の広がり。裏側から見た劇的な瞬間なので、これ一枚を顔や待機姿勢の基準にしない。
5. **旧作の継承確認** `official/key-art/sts1-defect-promo-anailis.png` と `sts1-defect-introduction.jpg`: 作家による公式プロモ原画と公式告知絵。現行の形を優先した後に補助として使う。

六点すべてを `view_image` で確認した。原本動画は `official/gameplay/sts2-early-access-trailer-video720.mp4` に保存した720p映像。Steamの公式HLSを**映像のみ、再エンコードなしでMP4へリマックス**したもので、音声付きの未加工原配信ファイルと称さない。派生PNGの秒位置とハッシュはmanifestに記録。

## 未確認・限界

- 公式で女性であるという設定、レンズ一つ一つの正式な機能名、外殻の厳密な材質名は確認できない。
- 自我獲得の全起源、創造主とNeowの発言の全真相、千年の全経歴を推測で確定しない。
- ローカル版の `DEFECT8_EPOCH`・`DEFECT9_EPOCH` は TODO。レリックの多くのflavorも後日公開用プレースホルダーであり、そこから新たな出自を作れない。
- オーブの五つの名前・説明はローカル版で確認。選んだ画像で形・配色を直接確認したのは雷・氷・闇。Glass / Plasmaを描く場合はその現行視覚資料を追加取得する。
- 2026-10-08時点のゲーム本体を更新・実行して検証していない。2026年9月の公式Neowsletterには新エリア等の予告があり、今後の情報で物語・美術が拡張される可能性がある。
- 画像の公式掲載はMODでの再配布許諾と同義ではない。ここに保存したものは調査・生成用参照であり、MODの完成素材ではない。

## 管理ファイル

- [Defect資料README](../../../art/references/defect/README.md) / [sources.json](../../../art/references/defect/sources.json)
- [世界観資料README](../../../art/references/world/README.md) / [sources.json](../../../art/references/world/sources.json)

公式Neowsletterの表紙、Community Corner、Spire Spottingの投稿された推測絵、外部作者のファンアートは、公式サイトに掲載されていても現行設定原画として採用していない。
