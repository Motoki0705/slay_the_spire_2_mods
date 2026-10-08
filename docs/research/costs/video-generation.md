# ５人女性化MODの動画素材仕様と生成料金

調査日: **JST 2026-10-09**。入力はローカル公式配布v0.107.1 / 59260271の[動作棚卸し](../motion/inventory.md)。価格は公式公開資料の標準料金。画像/動画生成、課金、外部への素材upload、ゲーム変更は行っていない。

**推奨はA: 選択背景５本をAI動画にし、戦闘・商人・休憩は骨格とモーションを使う。** 原作はSpineのキー・骨・mesh中心で、再利用の可能性がある。[rigの追加調査](../implementation/rig-reuse.md)と承認済み女性デザインのPoCで選ぶ。戦闘動画は必須の本番素材に数えず、Bは連番方式を採用した場合の比較、Cは再利用せず個別に作る上限ケースとする。原作rigの都合へ人の顔・髪・表情のデザインを戻すことは、この費用モデルの条件ではない。

原作１cycleと生成モデルの最短尺は別である。まず原作１cycle＋始終各0.5秒を予算化した場合、選択５本は **7 / 13 / 8 / 9 / 15秒、合計52秒**。H3 2Kなら初回 **$6.76**、平均３試行 **$20.28**、５試行 **$33.80**。新しい選択loopを各６秒にまとめるなら、生成７秒×５本＝35秒で **$4.55 / $13.65 / $22.75** になる。前者は比較用の原cycle保持仮定であり、原作と同じ長さで納品する義務を意味しない。

## 公式サービスと料金の確認

本書の計算は **MiniMax global Open Platformの `MiniMax-H3`** と **BytePlus ModelArkの `dreamina-seedance-2-5-260628`** に固定する。名称が似た非公式サイト、別モデル、subscriptionから換算した実効単価を従量料金として使わない。

| 項目 | MiniMax H3 | Seedance 2.5 / BytePlus ModelArk |
| --- | --- | --- |
| 生成API | `POST https://api.minimax.io/v2/video_generation` | `POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks` |
| 尺 | 4〜15秒、整数 | 通常生成4〜30秒、整数。編集は`duration=-1` |
| 出力 | 768P / 2K | 480p / 720p / 1080p |
| ratio | adaptive, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | 同じ６固定ratio＋adaptive |
| 基本料金 | 768P **$0.08/秒**、2K **$0.13/秒** | 動画参照なし: 480/720p **$10.7/M tokens**、1080p **$11.7/M tokens** |
| 動画参照 | 入力秒にも同じ$0.08/$0.13を加算 | 動画参照あり: 480/720p **$6.4/M**、1080p **$7.0/M**。入力動画秒もtoken量へ加算、最低token量あり |
| 画像参照 | 最初の５枚無料、以後$0.04/枚 | 2.5の料金表に別の画像枚数課金は記載なし。動画参照の有無で料金区分を選ぶ |
| 音声 | native stereo。参照audioは無料。音声なし割引は未確認 | `generate_audio=false`で無音。2.5の料金表は音声有無で分かれない |
| alpha | 透過出力の公開仕様は未確認 | 同左。green screen編集能力はalpha納品の保証ではない |
| 失敗・再試行 | H3従量APIの失敗返金規則は未確認 | generation failedは非課金。出力成功後に作画品質で不採用となった回は課金対象 |

根拠: [MiniMax料金](https://platform.minimax.io/docs/pricing/overview)、[H3 API](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)、[BytePlus料金](https://docs.byteplus.com/en/docs/modelark/model-pricing)、[Seedance 2.5仕様](https://docs.byteplus.com/en/docs/modelark/seedance-2-5)。BytePlusは公開HTML内の本文を読んだ。料金文書更新は2026-10-08T13:17:02Z、仕様更新は2026-09-28T06:48:10Z。[取得日時・本文hash](evidence/source-reads.json)を保存した。

H3のkeyframe方式とreference方式は同時指定できない。本予算は同じ開始/終了姿勢の画像２枚、動画参照0秒、Context-IRなしを基準とする。顔や衣装の複数画像をreference方式で使う場合も５枚以内なら画像追加費は0だが、始終frame制御との両立は別に試す。[H3生成ガイド](https://platform.minimax.io/docs/guides/video-generation)。

H3の768P→2K再生成は$0.05/秒で、元参照素材にも別の再課金がある。画像５枚以内・動画参照なしなら、768Pで３回＋採用takeを2K化１回は`(3×0.08+0.05)×52=$15.08`、５回なら`$23.40`。全takeを2Kで作る$20.28/$33.80より生成料金を減らせる。ただし再生成後の形・loopを再検査する。SeedanceのDraftも480pと最終1080pを別々に課金する。[MiniMax料金](https://platform.minimax.io/docs/pricing/overview)、[Seedance Draft](https://docs.byteplus.com/en/docs/modelark/seedance-2-5#2.5_draft_mode)。

| 別の公式経路 | 確認できた範囲・計算への扱い |
| --- | --- |
| Hailuo AI | H3を使える。web editorは５〜15秒、24fps、1440p/2K。planによる推定単価が案内されるが、必要なcreditと購入額をAPI料金へ混ぜない。[公式H3ページ](https://hailuoai.video/tools/minimax-h3) |
| MiniMax Video Packages / M Plan | H3はVideo Packagesの対象外。H3は従量APIを選ぶ。M PlanのLLM予算が動画代を含むという前提も置かない。[公式料金・対象モデル](https://platform.minimax.io/docs/pricing/overview#video-packages) |
| BytePlus ModelArk | 本計算の対象。開通条件の一案は残高USD30超等。充值額は消費料金と別。日本からの当該accountでの開通は未実施。[公式仕様](https://docs.byteplus.com/en/docs/modelark/seedance-2-5) |
| Volcengine / 火山方舟 | 中国向け`doubao-seedance-2-5-260628`のAPI提供を公式検索結果で確認。現在の料金本文を取得できず、CNY単価・日本からの開通は未確認。本計算へ使わない。[公式教程](https://docs.volcengine.com/docs/ark/seedance-2-5) |
| Jimeng / Doubao Pro | Seedance 2.5への操作経路は公式発表にある。現在のaccount/地域別credit購入額は未確認。[ByteDance発表](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) |
| Dreamina / CapCut | 2.5を提供。公式案内の低単価は年払い/期間限定offerの換算で、API従量価格ではない。必要本数を作る実購入額・地域・renewal条件はcheckout未確認。[公式料金案内](https://dreamina.capcut.com/seedance/seedance-2-5-pricing-2026) |
| BytePlus LAS | 同社でも別operator。取得した資料では2.5は480/720p。ModelArkの新しい1080p仕様・token料金と交換して扱わない。[公式LAS](https://docs.byteplus.com/en/docs/byteplus_las/video_gen_enhanced) |

## 具体的な尺と本数

原アニメの尺はSpine最大timeline終端。attackのdamaging delayやゲーム速度待ち時間とは異なる。clipの最短４秒をそのままゲームのattack待ちへ渡さない。

生成尺は `max(4, ceil(原尺＋1.0))`。H3で原尺＋余白が15秒を超える場合、分割各部へ１秒の余白を付ける。元のfloat値の微小誤差には0.00001秒のceil許容を使う。分割loopの接続成功は未検証。

| 選択 | 元名 / loop | 元cycle | １周保持の生成尺 | 本数 | 納品対象 |
| --- | --- | ---: | ---: | ---: | --- |
| Ironclad | `animation`, loop | 5.333s | 7s | 1 | 1920×1080背景動画＋poster |
| Silent | 同 | 11.667s | 13s | 1 | 同 |
| Regent | 同 | 6.667s | 8s | 1 | 同。星座hoverは独立 |
| Necrobinder | 同 | 8.000s | 9s | 1 | 同。選択でのOstyを含む構図 |
| Defect | 同 | 13.333s | 15s | 1 | 同。選択構図内の装飾orbは可、戦闘orb stateは含めない |
| 合計 | | 45.000s | **52s** | **5** | |

戦闘コアは５人×**６素材＝30素材**。セルは **元尺→生成尺**。loopはidleのみ、ほかはone-shot。通常attackと固有技、castとDefectのprocessを分ける。

| キャラ | idle_loop | attack | cast | hurt | die | 固有動作 | コア生成秒 H3 / Seedance |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| Ironclad | 2.000→4 | 1.167→4 | 1.567→4 | 1.000→4 | 2.333→4 | `attack_heavy` 1.533→4 | 24 / 24 |
| Silent | 1.067→4 | 0.933→4 | 1.300→4 | 0.733→4 | 1.867→4 | `shiv` 0.700→4 | 24 / 24 |
| Regent | 19.444→11＋11 / 21 | 1.389→4 | 1.875→4 | 0.972→4 | 4.340→6 | `attack_sovereign` 1.215→4 | 44 / 43 |
| Necrobinder | 2.000→4 | 1.000→4 | 0.967→4 | 0.833→4 | 2.333→4 | `cast_mighty` 1.667→4 | 24 / 24 |
| Defect | 12.000→13 | 1.500→4 | 1.233→4 | 0.733→4 | 2.233→4 | `process` 1.567→4 | 33 / 33 |
| 合計 | | | | | | 30素材、H3は31task | **149 / 148** |

死亡の終端frameをposter/静止dead poseとして再利用できる。プレイヤー復活はfade＋idle復帰なので新しいrevive動画を増やさない。TheArchitectの本人attack、休憩・イベントからgame-over時の戦闘dieはコアを共用する。商人は別atlasによる見た目差を考慮する。

Cへ追加する候補は以下。**素材候補を全て動画化する上限比較であり、製作指示ではない。**

| 使用箇所・独立entity | 元尺と生成尺 | 追加素材数 | H3 / Seedance生成秒 |
| --- | --- | ---: | ---: |
| 戦闘`relaxed_loop`５人 | 元12 / 7 / 13.889 / 6 / 12→13 / 8 / 15 / 7 / 13 | 5 | 56 / 56 |
| 商人５人 `relaxed_loop`＋`die` | 同じ戦闘skel、別shop atlas。relaxed計56s＋die計22s | 10 | 78 / 78 |
| Ironclad休憩３環境 | 各6.667→8 | 3 | 24 / 24 |
| Silent休憩３環境 | 各8.000→9 | 3 | 27 / 27 |
| Regent休憩３環境 | 各8.000→9 | 3 | 27 / 27 |
| Necrobinder休憩３環境 | 各21.333→12＋12 / 23 | 3 | 72 / 69 |
| Defect休憩３環境 | 各8.000→9 | 3 | 27 / 27 |
| Osty休憩３環境 | 各10.000→11 | 3 | 33 / 33 |
| Osty戦闘７動作 | idle .667、attack1.000、poke .533、hurt .900、die1.333、dead .167、revive .967→各4 | 7 | 28 / 28 |
| Regent通常武器 `attack` / `attack2` | 各 .972→4 | 2 | 8 / 8 |
| Sovereign Blade局所`idle_loop` / `attack` | 2.667 / 1.000→各4。位置と成長は別制御 | 2 | 8 / 8 |
| Lightning / Frost / Dark / Plasma / Glassの表面loop | .417 / 6.250 / 8.333 / 2.778 / 8.333→4 / 8 / 10 / 4 / 10 | 5 | 36 / 36 |
| C追加合計 | | **49** | **424 / 421** |

休憩は`overgrowth_loop / hive_loop / glory_loop`。light_on/offのduration0 trackは照明設定なので動画に数えない。新女性デザインの衣装・camera・解像度を共用できれば商人relaxed/dieの10素材を再利用でき、Cから78生成秒を減らせる。休憩環境差を同じpose＋照明合成で扱える場合も３環境を別生成する必要がなくなる。共用を検証する前の予算へはこの節約を織り込んでいない。

専用block/victory、選択intro/exit、商人buy/sell、休憩smith/sleep、未収録Osty castを作らない。収録のみでruntime未確認のweak/nervous/_ignore/demo等も計上していない。

## 必要pixelと動画モデルのframe

**1920×1080、24fpsを最初の表示・納品基準**とする。`combat_room.tscn`のSceneContainerは1920×1080のminimum/offsetを持つ。[scene:106](../motion/evidence/resources/scenes/rooms/combat_room.tscn)。選択sceneのroot形状は一様な16:9ではなく、例Ironcladは2560×1200相当。新しい動画は表示viewportで構図を作り、ゲームUIとsafe areaに合わせてcrop/letterboxする。元rootへ引き伸ばして合わせない。

下の静的参考値は **Spineのsetup/export bounds×Visualsのlocal scaleをscene単位で計算**しただけで、ゲームの画面実測pixelではない。剣の広がり、dieの倒れ、mesh変形、別VFX、camera/人数によるruntime scaleの全範囲を含まない。atlasのpacking scaleをさらに掛けて二重に縮小しない。最終canvasは全採用motionのrender envelopeと固定pivotをPoCで測って決める。[数値とscene行番号](evidence/static-size-evidence.json)、[rig/atlasの補足](../implementation/rig-reuse.md)。

| entity | 元の静的参考 幅×高さ | 納品sprite canvas案 | 枠を広く取る理由 |
| --- | ---: | ---: | --- |
| Ironclad | 約247×332 scene units | **448×512 px** | 剣・腕・新しい髪の広がり |
| Silent | 約239×284 | **384×512** | 外套・短剣・髪 |
| Regent | 約211×369 | **512×640** | 本体、従者、玉座を一つの主体とし、武器は別 |
| Necrobinder | 約260×336 | **448×576** | 鎌・袖・髪。Ostyを焼き込まない |
| Defect | 約260×292 | **448×512** | 首/腕/衣装。戦闘orbを焼き込まない |
| Osty | 約228×228 | **384×384** | 指、手、独立した炎 |
| Regent通常武器 | setup約201×369（親.29） | **384×512** | 本体から独立、武器の攻撃envelopeはPoC待ち |
| Sovereign Blade局所素材 | export boundsが0で範囲不明 | **256×512** | 刀身の基礎detail用の制作仮定。Forge最大拡大のpixel密度は未確定 |
| ５orb | 元のlocal scale後で約33〜59程度 | **128×128** | 小表示の模様/輪郭用。label/flashは別 |

商人は元scale .47（Defect .23）で戦闘より大きい。元データの静的参考は約414×557 / 387×461 / 343×598 / 452×584 / 478×538。商人納品canvasを順に **576×768 / 576×768 / 640×896 / 576×768 / 640×768** と仮設定する。共有するなら、戦闘用へcropした低解像度frameではなく生成masterから別書き出しする。

休憩sceneの元setup範囲は戦闘と違い、概ねIC402×644、Silent418×671、Regent405×781、Necro371×662（scale1.12518）、Defect650×692（.95）、Osty553×302（.812）。制作canvasは順に **512×896 / 576×896 / 576×1024 / 512×896 / 768×896 / 768×448**。これは制作上の余白込みの案であり、全animationのrender boundsを測った値ではない。

| 生成対象 | H3に渡す設定 | Seedance ModelArkに渡す設定 | 加工 |
| --- | --- | --- | --- |
| 選択背景 | **2K、16:9**。公式sampleは2560×1440/24fpsを確認 | **1080p、16:9 = 1920×1080** | 1920×1080へ納品。UI文字なし、音声track除去、poster抽出 |
| 本人/通常武器/刀身 | **768P、3:4**（名目768×1024、exact API寸法未確認） | **720p、3:4 = 834×1112** | 単色背景等からalphaを作り、isotropic resize、余白/足元pivotを維持して上表canvasへ |
| 戦闘Osty / orb | **768P、1:1**（名目768×768、同じ未確認） | **720p、1:1 = 960×960** | entityごとに切り出す。相棒・orbのstateを本体映像へ焼かない |
| 休憩Osty | **768P、4:3**（名目1024×768、同じ未確認） | **720p、4:3 = 1112×834** | 独立横長spriteへ。flip/配置変更を保持 |

Seedanceの固定ratioの実寸は[公式仕様のpixel表](https://docs.byteplus.com/en/docs/modelark/seedance-2-5#2.5_ratio)。H3の2Kは[公式API sample](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)をread-onlyでffprobeした。[metadata](evidence/h3-public-sample-probe.json)。そのsampleの長さはAPI例の5秒と一致しないため、実寸確認から生成尺/請求の保証は導かない。H3の768P名目寸法をAPIの確定実寸とは呼ばない。

始終画像のratioを固定し、モデルのadaptive条件に従う。生成frame全体を最終sprite canvasへ異方伸縮しない。背景除去、髪/細い刃/炎のalpha縁、固定camera、本人同一性、足元pivot、attack→idle、die終端、loopの速度と位置の接続が加工の検査点である。元timelineに合わせるretimeとevent再送も別工程。

1440pの選択納品は2560×1440が別presetになる。H3は同じ2K料金で試せるが、Seedance ModelArkの公開出力は1080pまでなのでupscaleの費用/品質は未確定。4K納品は両APIのここで確認したnative仕様外であり、旧Seedance 2.0やDreaminaの付加機能を2.5 APIの料金として代入しない。戦闘canvasを1080p基準から拡大する場合は、表示倍率とmasterのpixel密度を測ってから別scenarioを作る。

## シナリオと試行回数別の生成料金

| scenario | 動画素材にする範囲 | 素材数 | H3 task / 秒 | Seedance task / 秒 |
| --- | --- | ---: | ---: | ---: |
| **A（推奨）** | 選択５本、その他はrig/部位絵 | 5 | 5 / 52 | 5 / 52 |
| **B** | 選択＋戦闘コア30素材 | 35 | 36 / 201 | 35 / 200 |
| **C** | 上記＋relaxed、商人、休憩、独立Osty/武器/剣/orb表面の全個別候補 | 84 | 88 / 625 | 84 / 621 |

H3の追加taskはRegent idle１箇所とNecrobinder休憩３環境の長いcycleの分割による。人数、カード枚数、敵数、orb数では本数を増やさず、同じ素材をruntimeで共有する。

| scenario | MiniMax H3 初回 | 平均３試行 | 平均５試行 | Seedance 2.5 初回推定 | 平均３試行 | 平均５試行 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | **$6.76** | **$20.28** | **$33.80** | $29.57 | $88.70 | $147.84 |
| B | $18.68 | $56.04 | $93.40 | $63.99 | $191.97 | $319.95 |
| C | $52.60 | $157.80 | $263.00 | $161.81 | $485.43 | $809.06 |

画像２枚・動画参照0秒・無料枠/割引なし。倍率は品質不採用を含む**仮の制作試行係数**であり、モデルの実測成功率ではない。５試行で完成する保証や予算上限ではない。H3は選択2K / sprite768P、Seedanceは選択1080p / sprite720pという、この用途の品質tierでの比較である。見た目の優劣や透過加工の工数を料金差から判断しない。

| キャラの所有範囲（相棒/武器/orbは詳細CSVで別entity） | A素材数 | B素材数 / H3秒 / Seedance秒 | C素材数 / H3秒 / Seedance秒 |
| --- | ---: | ---: | ---: |
| Ironclad | 1 | 7 / 31 / 31 | 13 / 85 / 85 |
| Silent | 1 | 7 / 37 / 37 | 13 / 84 / 84 |
| Regent＋武器２＋剣２ | 1 | 7 / 52 / 51 | 17 / 131 / 130 |
| Necrobinder＋戦闘Osty７＋休憩Osty３ | 1 | 7 / 33 / 33 | 23 / 184 / 181 |
| Defect＋５orb | 1 | 7 / 48 / 48 | 18 / 141 / 141 |

算式:

```text
H3 = 試行倍率 × Σ(生成秒 × 解像度単価)
     + 試行倍率 × Σ(参照動画秒 × 同解像度の入力単価)
     + 試行倍率 × Σ(max(画像枚数 - 5, 0) × $0.04)

Seedance 推定tokens = (参照動画秒 + 生成秒) × 出力幅 × 出力高 × 24 / 1024
Seedance 推定料金 = 試行倍率 × Σ(tokens × 解像度/動画入力有無の$/M / 1,000,000)
動画入力ありでは公式の最低tokensとのmaxを取る。実請求はusage.completion_tokens。
```

AのSeedanceは `52×1920×1080×24/1024 = 2,527,200 tokens`、`×$11.7/M = $29.56824`。Bはさらに720p portrait `3,216,946.5 tokens`、Cは720pのratio別合計 `12,359,143.125 tokens`を加える。H3のBは`52×.13+149×.08=$18.68`、Cは`52×.13+573×.08=$52.60`。

動画参照を毎task５秒使うと、H3は１試行あたりA **+$3.25**、B **+$15.65**、C **+$36.45**。Seedanceは単価区分が下がっても入力動画tokenを加える。最低token量を未取得なので、動画参照ありの具体総額を確定値として出していない。既存rigのmotionを直接ゲームで流用する場合、この動画参照代自体が不要になる。

## 短い動作と制作範囲の選び方

SilentのShivは元0.7秒だが、各0.5秒の余白を付けても1.7秒。個別生成では４秒を使い、H3 768Pで$0.32となる。余剰秒は生成・切出し用で、ゲームへ４秒のShivを納品する理由にならない。

４つの短い技（attack/cast/hurt/固有）を１本へまとめ、間に0.5秒のidleを３回入れる仮定では、IC8 / Silent7 / Regent8 / Necro7 / Defect8秒＝**38秒**。個別生成の20本×４秒＝80秒より42秒を減らせ、H3で**$3.36/試行**減になる。30個の納品素材のうち20技を５taskから切り出すため、素材数自体は減らない。次の技への形の引継ぎ、時間指定、切出しframe、終端姿勢が４つとも成功するとは限らず、１技の修正で全体を再生成する場合があるため、基準予算へは採用しない。

方式比較は、Aの選択５本に **Ironcladのidle/attack/hurt/die４本だけ**を足す小さい案で足りる。生成各４秒、追加H3費は初回 **$1.28**。選択込みでは **$8.04 / $24.12 / $40.20**、Seedanceは **$33.29 / $99.87 / $166.45**。固有heavy/cast等の正式採用はPoC後に決める。[小比較の再計算表](evidence/variant-totals.csv)。

本体に相棒や戦闘orbを固定合成する案、剣の周回/target/Forge成長、Ostyの生死/配置、orbのchannel/evoke/値、UI操作/energy/card trail、shader/particleの状態依存VFXは、ここでは**動画生成費不要・独立rig/ゲーム制御**とする。Cの剣/orbは局所表面素材の上限費用のみであり、動作制御の動画全置換ではない。

この表は**動画AI生成料金**。rig/mesh/部位作画、Spine Editor、透過処理・整音・合成・event bridge、loop修正、品質review、保存・通信、税は含まない。公開根拠のない人力相場を仮の金額で足して全工程費と呼ばない。正式デザイン、frame envelope、H3の768P実寸、各サービスのaccount開通、動画参照最低token、実際の試行回数は残る確認事項。

成果物: [全素材・尺・pixel・費用CSV](evidence/asset-costs.csv)、[シナリオ別CSV](evidence/scenario-totals.csv)、[設定](evidence/production-policy.json)、[単価/仕様](evidence/provider-specs.json)、[検証](evidence/validation.json)。再計算は `python3 docs/research/costs/evidence/build_cost_model.py`。根拠と限界は[evidence/README](evidence/README.md)。
