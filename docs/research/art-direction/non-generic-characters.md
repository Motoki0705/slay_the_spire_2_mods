# キャラの均一化と誇張を避けるプロンプト・絵作りの調査

確認日: **2026-10-09（JST）**。[Issue #24](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/24) / [次の４案への適用](../../design/characters/slender-revision-brief.md) / [現在のレビュー画像](../../design/characters/review-gallery.md)。

**抽象的な「AIっぽくしない」を、体型・所作・描画の観察可能な条件へ分ける。** 今回は華奢な身体、装備の量感、行動に沿う目線と手、焦点に応じた描き込みを別々に扱う。プロンプトだけで「AIっぽさ」を消せる保証や、特定語の改善率を示す根拠は、今回読んだ一次資料からは確認できなかった。

ユーザーはSilent v0.5を承認し、他４人は「スタイルが良すぎる」「華奢な感じが魅力的」とレビューした。「AIっぽさ」は統一された測定指標ではなく、このプロジェクトの表現を判断するための問題提起として扱う。下記の公式仕様、絵作りの指針、旧案の観察、未生成の改善仮説を区別する。

## モデルの公式文書から採用すること

| 調査で確認できた指針・仕様 | 今回の制作への適用 | 限界 |
| --- | --- | --- |
| 素材・色・画法、人物の視線や行動を具体的に書く [O1] | 「美しい女性」だけにせず、肩・胴・手足と、何を見て何をしているかを書く | 指定語と画質の因果や改善率を測った資料ではない |
| 入力画像の番号と役割、変更対象と保持対象を分ける [O1] | 原作は装備、旧案は人物の翻案、Silentは塗りと光、という役割を明示する | 参照した顔や体型の混入が必ず防げるわけではない |
| 参照の画風を保ち、題材を変える編集例がある [O2] | Silentの透明感を参考にしつつ、４人の顔・髪・身体・行動は個別に設計する | 本MODでの成功例はまだない |
| 小さな変更を反復し、保持条件を再記述する [O1, O2] | 体格・表情・光を一度に全変更せず、比較の目的を一つずつ決める | １枚の差を特定語の効果と断定しない |
| `gpt-image-2`では`input_fidelity`を指定しない [O4]。高忠実度入力、構図や一貫性の限界が記される [O5] | 直したい体型まで保持条件に含めず、必要なら旧案を装備資料として再構成する | 高忠実度は「体型や姿勢が変更不能」という意味ではない |
| 公開Images APIスキーマに専用`negative_prompt`・`seed`・プロンプト重みの欄は見当たらない [O3, O4] | 必要な除外は普通の文章で書く。同一seedの比較と称さない | 閲覧した公開スキーマの範囲での確認 |

長文だから必ず悪化する、否定語は必ず逆効果、`masterpiece`を消すだけで自然になる、という結論は得ていない。具体化する理由は、**要求と出力の差を説明し、次の変更を選びやすくすること**。公式も短文・段落・構造化した形式などを許容している。[OpenAI Image prompting][O1]

Midjourneyの`--no`は専用機能であり、GPT Imageへそのまま使う構文ではない。SD系の重み表記もGPTのパラメータとして定義されたものとは扱わない。[Midjourneyの公式説明][M1] / [GPTの生成仕様][O3]

参照した現在の一般ガイドの作例はGPT Image 2.5が中心。今回のモデルを自動変更せず、GPT Image 2向けCookbookと現行API仕様を照合した。古いCookbookの一部コードには`input_fidelity`指定が残るため、プロンプトの考え方と実行パラメータを分け、後者は現行仕様を優先する。[Cookbook][O2] / [edit仕様][O4]

## 華奢さを指定するときの未検証の仮説

「細身」「華奢」だけでは、長身・脚長・強いくびれを持つ体型にも解釈され得る。今回のユーザー意図への制作上の解釈として、肩幅、胴の厚み、四肢、衣服の収まりを明示し、脚の長さと胸腰の誇張は抑える。これは特定語の効果を実証した主張ではない。

身体と装備も分ける。華奢な上腕の上に巨大な肩当てを置けば、外形は大きく見える。小さな胴を強く絞る衣装で囲めば、細身でも体型の強調は残る。本人の身体を細くする、肩当てを薄くする、衣服を直線的に落とす、という別の変更として検討する。

肌の汚れ、無秩序な線、ランダムな装飾や左右差を足すことを「人が描いた感じ」の必須条件にしない。写真向けの毛穴・傷みの作例を、透明感のあるアニメ調へそのまま転用する根拠はない。顔や手の焦点、静かな布の面、素材ごとの反射など、意味のある強弱を設計する。

これらは[４人の改訂案](../../design/characters/slender-revision-brief.md)と、後の画像比較で確かめる。今回、画像API・動画APIは呼び出していない。

## 絵作りの一次資料から採用すること

以下はキャラクターの読みやすさや人物描写の根拠であり、画像AIへの特定語の効果を測った資料ではない。Prokoは著者のLesson Notesを根拠にし、受講者コメントを混ぜていない。

| 資料 | 確認した内容 | 今回の応用と限界 |
| --- | --- | --- |
| [The Walt Disney Family Museum — Silhouette][A1]（PDF全３ページ） | 輪郭から人物を識別し、身体・髪・服の形が埋もれないよう配置する | 華奢な身体と大きい装備を区別して読む。複雑な細部だけで個性を作らない。衣服越しの実寸は測れない |
| [同 — Shape Language][A2]（PDF全５ページ） | 形の印象と組合せ。ただし形と意味の対応を固定規則とはしない | ５人を同じ細長い形へ揃えず、役割や所作に応じて大きな形を選ぶ |
| [Stan Prokopenko — How to Draw Gesture][A3] | 動作や感情を、身体の流れと部位の関係から描く | 目線・手・重心を同じ目的へ向ける。動作を分かりやすくすることと、体型を誇張することを分ける |
| [同 — Human Proportions – Average Figure][A4] | 比率体系は比較の目安で、個人差や短縮遠近を考慮する | 脚長・小顔へ自動的に寄せない。教材の7.5頭身には平均的な欧州男性という由来があり、全女性の正解として採用しない |
| [Walt Disney Animation Studios — Visual Development][A5] | 物語の意図を、人物・衣装・色・構図と、一つの感情的な瞬間へまとめる | 人物の行動から魅力を設計する。華奢さの寸法や生成プロンプトの正解を示す資料ではない |

## 旧４案で確認した指示と画像

`character-art-research`が４人の対象PNGと承認済みSilentを目視した。以下は視覚判断であり身体寸法の測定ではない。**現行プロンプトには誇張体型や媚びを避ける記述が既にある**ため、「禁止指定がなかった」とは結論しない。

| キャラ | 現行プロンプトの実際の指定 | 画像の観察 | 改訂仮説 |
| --- | --- | --- | --- |
| Ironclad | [L10・14][IC]の `athletic, believable body`、`broad shoulder plates` | 肩・前腕・すねの装甲と、絞った胴が目立つ | 軽い体格と短い肩当てを別指定し、剣・手・踵の荷重で強さを見せる |
| Regent | [L14・16][RG]の `compact, sturdy build`、`weighty seated silhouette` | 大きい王衣と堂々とした態度。衣服から実際の肩幅は断定できない | 大きい王衣は残し、袖口・肘・胴脇で小さな身体との差を見せる |
| Necrobinder | [L12・14][NC]の `compact, wiry, adult-looking woman`、大きい尖った襟 | 既に細い。腰の絞り、長い裾、襟・鎌の縦長感が強い | 細さの追加より、胴の布の落ち方と普通の四肢比率、Ostyへの合図を調整する |
| Defect | [L13][DF]の `Substantial forearms`、大きいすね・足、`compact, slightly sturdy silhouette` | 修理とオーブへの注意は読める。前腕・膝・すね・足の大きさが全身の重さを作る | 細い機構と、局所的に大きい補修部品へ量感を配分する。人体の胸腰だけを直す問題にはしない |

`curvy`、`heroic`、`statuesque`、`long limbs`、`polished fantasy`は、指定された４つの初回プロンプトにはない。`polished anime`等はあるが、その語単独が原因と特定したわけではない。参照、構図、複数の要求、生成時の変動を切り分ける実験はしていない。

Necrobinderの比較対象はcorrected版。[補正指示][NC-fix]で人物自体を保持した上でOstyを修正しているため、初回指示だけで修正版の全特徴を説明しない。画像とプロンプトの固定commit・来歴は[ギャラリー](../../design/characters/review-gallery.md#制作条件担当固定した出典)にまとまっている。

**反証として、承認済みSilentにも大きい外套と相当量の細部がある。** 「布や細部を減らせばよい」という一律の結論は採用しない。承認の理由を目の大きさ・露出・体型の一つへ特定することもできない。４人は身体、装備、所作、焦点の関係をそれぞれ見直す。

## 技術一次資料

全て上記確認日に担当がウェブ本文を閲覧。O1・O2・O4・O5の主要根拠は親も照合した。発行日表示がないものは閲覧日を記録する。

| ID | 資料 | 対象・採用範囲 |
| --- | --- | --- |
| O1 | [OpenAI — Image prompting][O1] | GPT Image共通指南。現行作例は2.5中心。具体指定・参照の役割・変更と保持 |
| O2 | [OpenAI Cookbook — GPT Image Generation Models Prompting Guide][O2] | 2026-04-21、GPT Image 2中心のアーカイブ。画風の転写と制作パターン。実験的な改善率は示さない |
| O3 | [OpenAI — Create image][O3] | 公開生成スキーマ。今回使っていない制御機能を推測で追加しない |
| O4 | [OpenAI — Create image edit][O4] | 画像入力と現行パラメータ。GPT Image 2では`input_fidelity`省略 |
| O5 | [OpenAI — Image generation][O5] | 高忠実度入力と、一貫性・構図等の限界。現行作例と今回のモデルを区別 |
| M1 | [Midjourney — No][M1] | 別モデルの専用否定構文との比較に限定。GPTでの効果の根拠にはしない |

## 調査担当と確認範囲

Issueで問いと出力先を先に定め、履歴をforkしない独立CLIの読み取り専用セッションを２つ並行した。`prompt-api-research`は**GPT-6.1 sol / max**でモデル公式文書、`character-art-research`は**GPT-6 astra / max**で絵作りの一次資料と旧案を担当。親が本書・改訂案・承認状態の更新を専用worktreeからPRへ提出する。

固定scoutロールは指定モデル・tierを満たさないため使っていない。両セッションに`service_tier="default"`を明示し、取得できるturn contextでそれぞれのモデル・max・read-onlyを照合した。応答tierはCLIログに公開されておらず、サーバーの実効tierを直接観測したとは記録しない。グローバル設定の変更、fastへの切替、追加の子エージェント起動は行っていない。

開始指定commitは `5d20a14716e862c1aa40db8c813236d6e12addf9`。調査中に親が承認済みSilentのPR #13を統合し、作業worktreeのHEADは `945821018c9d71caf46c1e27f8138d5f18ddc20c` になった。４人の観察対象はリンク先の各固定commitのPNG・プロンプトで、調査中の画像変更はない。原作の設定は既存の[キャラ調査](../characters/README.md)を参照し、再抽出していない。

本作業は次案のための調査であり、validatorによる完成物の合否評価ではない。生成効果、比較実験、４人の新デザイン承認は未確認。

[O1]: https://developers.openai.com/api/docs/guides/image-prompting
[O2]: https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
[O3]: https://developers.openai.com/api/reference/resources/images/methods/generate
[O4]: https://developers.openai.com/api/reference/resources/images/methods/edit
[O5]: https://developers.openai.com/api/docs/guides/image-generation
[M1]: https://docs.midjourney.com/hc/en-us/articles/32173351982093-No
[A1]: https://www.waltdisney.org/sites/default/files/2020-05/T%26T_Silhouette-final2.pdf
[A2]: https://www.waltdisney.org/sites/default/files/2020-04/T%26T_ShapeLang_v9.pdf
[A3]: https://static.proko.com/static/course-lesson/how-to-draw-gesture
[A4]: https://www.proko.com/course-lesson/human-proportions-average-figure/
[A5]: https://www.disneyanimation.com/process/visual-development/
[IC]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/87ce8c21536fac2c2d1ce360e513fddb7e4e296d/art/prompts/ironclad-v01.txt#L10
[RG]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/4f97a7a700cfb42e9b1435b6f8049d9b48fb75af/art/prompts/regent-v01.txt#L14
[NC]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31/art/prompts/necrobinder-v01.txt#L12
[NC-fix]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31/output/imagegen/necrobinder/necrobinder-v01.correction.txt#L11
[DF]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/f033dd6b8f7cb0de6c6d0b1db43ab42cdd9036a8/art/prompts/defect-v01.txt#L13
