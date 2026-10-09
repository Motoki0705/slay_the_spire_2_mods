# 制作・配布・実機QAのIssue地図

[開発の案内](README.md) / [５人の現行ギャラリー](../design/characters/review-gallery.md) / [全体Issue #1](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/1)

確認日: **2026-10-09（JST）**。基準mainは `6b190bb82a38052c42de869211586a032140ab84`（PR #35統合）。Issue本文・PRの統合状態・制作記録と親のQA共有を照合した。本案内の現行化は [#36](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/36) / `delivery_docs`。実担当はIssue本文のエージェント名で確認し、GitHub assigneeとは区別する。

## ５人のデザインと制作採用

**Silent v05のデザインはユーザー承認済み。他４人v02は自律制作の委任に基づく制作採用。５件のデザインPRはmain統合済み・Issueはclosed。** 派生素材・動作・UIへユーザー承認を拡張しない。現行画像・固定commit・旧案は [ギャラリー](../design/characters/review-gallery.md) から辿る。

| Issue / 担当 | 現行デザインと記録 | 統合済みPR |
| --- | --- | --- |
| [#3 Ironclad](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/3) / `art-ironclad-production` | v02、薄い装甲と繊細な身体。委任に基づく制作採用。[v02記録](../design/characters/ironclad/review-v02.md) / [制作](../design/characters/ironclad/production.md) | [#12](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/12) |
| [#2 Silent](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/2) / `art-silent` | v05、基準デザインのユーザー承認。革バンド省略の差分は残る。[承認範囲](../design/characters/silent/review-v05.md#ユーザー承認2026-10-09) / [制作](../design/characters/silent/production.md) | [#13](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/13) |
| [#4 Regent](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/4) / `art-regent-production` | v02、小さい成人の身体と大きな王衣。委任に基づく制作採用。本人と玉座/運び手を分離。[v02記録](../design/characters/regent/review-v02.md) / [制作](../design/characters/regent/production.md) | [#15](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/15) |
| [#5 Necrobinder](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/5) / `art-necrobinder-production` | v02、腰の絞りを緩めた衣服とOstyへの合図。委任に基づく制作採用。概念画のOstyの左手判定は未確定。[v02記録](../design/characters/necrobinder/review-v02.md) / [制作](../design/characters/necrobinder/production.md) | [#17](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/17) |
| [#6 Defect](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/6) / `art-defect-production` | v02、細い機構と補修前腕の対比。委任に基づく制作採用。bodyと休憩は座位を共有。[v02記録](../design/characters/defect/review-v02.md) / [制作](../design/characters/defect/production.md) | [#16](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/16) |

[#24 プロンプト・絵作り調査](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/24) はclosed、[PR #25](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/25) 統合済み。[調査](../research/art-direction/non-generic-characters.md) と [４人の改訂案](../design/characters/slender-revision-brief.md) を後続v02制作に反映した。調査段階の仮説と実画像の採用判断は別に記録する。

## 現行の実装・素材・QA

| Issue / 担当 | 確認時点の状態 | 依存と残る確認 | 成果・入口 |
| --- | --- | --- | --- |
| [#26 無料描画runtime](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/26) / `free-animation-runtime` | PR #30統合済み、Issueはopen。Godot meshと元driver観測の実装・standalone検証済み | 原作track/event/待ちを保持する設計。配布接続は#33のPCKへ移行。全５人のnative状態遷移・独立物は#11 | [#30](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/30) / [動作・rig契約](free-animation.md) / [現行PCK接続](pck-only.md#接続とcache) |
| [#21 Regent星座hover](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/21) / `regent-select-overlay` | **closed・PR #31統合済み**。７種のhover・入力非消費・reduced motion・解放をstandaloneで確認 | #35の最終背景/人物/玉座に接続済み。native画面の配置・入力回帰は#11 | [#31](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/31) / [regent-overlay.md](regent-overlay.md) |
| [#28 Silent素材](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/28) | **closed・PR #29統合済み**。body・まばたき・背景を制作採用 | ユーザー承認は元v05デザインのみ。休憩・用途別rig・UIは#10で統合 | [#29](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/29) / [Silent制作記録](../design/characters/silent/production.md) |
| [#10 正式素材](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/10) / `production-surfaces`・親（統合） | PR #32 / #35統合済み、Issueはopen。５人の本体・背景・まばたき・休憩姿・20rig・５選択scene・25UI PNGを接続 | API課金エラー時の不足４背景・４閉じ目は、ユーザー指定のCodex内蔵生成で補完済み。実機での全surface・武器/VFX位置は#11 | [#32](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/32) / [#35](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/35) / [制作素材](../design/characters/production-assets.md) |
| [#33 PCKのみの接続・配布](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/33) / `pck-only-delivery` | PR #34統合済み、Issueはopen。source bundle・所有ゲームからのローカル生成・verify・明示install/uninstallを実装 | #26 / #21 / #10を接続。設定変更は再build/install/restart。元mainの通常ロードは親が確認、残る全surface・競合QAは#11 | [#34](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/34) / [pck-only.md](pck-only.md) / [MOD README](../../mod/README.md) |
| [#11 実機QA](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/11) / 親（`runtime-qa`） | **進行中・open**。通常PCKロード・５人分の選択アイコン・選択背景の表示とIroncladのnativeカード使用を確認 | 全５人の戦闘/商人/休憩、死亡/復活・音/VFX・速度・独立物、保存/再開・co-op・競合・性能・通しプレイを継続 | 親の所有は `tools/runtime/**`、`tests/runtime/**`、`docs/validation/**` と製品修正。正式報告予定 `docs/validation/runtime-v01.md` はこの基準版では未追加 |
| [#36 利用・進行・制作案内](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/36) / `delivery_docs` | 本文書を含む現行化・PR提出の作業 | #34 / #35統合内容と親の共有範囲のみを記載。実機検証やvalidator評価を担当しない | 本案内 / [開発README](README.md) / [ギャラリー](../design/characters/review-gallery.md) / [MOD README](../../mod/README.md) |

#1の完成条件は [自律完成工程](autonomous-delivery.md)。素材制作・PR統合だけで全体完成にしない。旧Spine Editor PoCは必須依存から外し、動画AIを生成工程に入れない。現行のPCK配布はRitsuLib・Harmony・自作/第三者DLLをロードせず、C#の空catalog登録も導入条件にしない。

## 現行QAで確かめた範囲

親の共有（2026-10-09）では、元mainの通常起動でPCKロード、５人分の選択アイコンと選択背景の表示、Ironcladのtop portraitを確認。Ironcladは元ID・カードのまま、native UIからSTRIKEを使用し敵HP **43→37**、overlay **idle_loop→attack→idle_loop** を確認した。選択人物の見切れはproduction descriptorで修正済み。

通常検証の既存記録は [PCK検証](../../tests/pck_mod/validation.json)（native helper **204**、Godot **161**、Python **16**＋旧build **10**）。receipt拡張子 `.receipt` 対応後のPython **17**＋旧build **10**成功は親の追加共有。helperは原main・実プレイを動かしていない。本案内担当は実装テスト・ゲームを再実行していない。validatorは指定0回・試行0回。

全５人の実戦や商人/休憩、co-op、通しプレイの合格はまだ記録しない。最新版対応、保存/RNG・他MODとの互換性、性能も未確認。最新QAと不具合は [#11](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/11) から追う。

## 旧工程と移行

| Issue | 当時の成果と現行工程への対応 |
| --- | --- |
| [#7 C#基盤](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/7) | closed・[PR #14](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/14) 統合。依存・空catalog・DLL配布は当時の仕様。[build.md](build.md) は履歴、現行build/exportは#33の入口を使う |
| [#8 動画/poster再生](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/8) | closed・[PR #20](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20) 統合。合成Theoraによる汎用描画検証は [select-playback.md](select-playback.md)。今回の選択素材は動画なしのGodot描画、Regent固有hoverは#21 |
| [#18 Spine抽出](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/18) | closed・[PR #23](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/23) 統合。抽出生データはローカル専用の参考。PCK接続に原skeleton/atlas/textureを同梱しない |
| [#9 Editor往復PoC](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/9) | **工程から外してclosed**。[親の変更記録](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/9#issuecomment-6071417778)。#26へ置換した判断であり、Editor往復・再skin/reweightが完了したという意味ではない |
| [#19 初回レビュー案内](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/19) | closed・[PR #22](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/22) 統合。初回v01候補を辿る案内から、本#36で現行v02・PCK・QAへ更新 |

## 過去の基盤・抽出の検証記録

以下は **PR #14 / #20 / #23の各対象commitに対する当時の記録**。空catalog・hover未実装・実機未確認の記述は、その検証時点の範囲であり、上記の現行進行を置き換えない。原文と検証の版を保ち、履歴の成功を今の全体合格へ読み替えない。

#7 / PR #14の統合commitは `e21f02c7e021e2d7ba803cb1885842c8489e4a54`。担当記録には、実ビルド **警告０・エラー０**、通常 **17件（C# 10＋Python 7）**、実コマンドの異常系 **６件**、ZIPの３ファイル構成と依存DLL非混入の確認がある。[親の統合コメント](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/14#issuecomment-6064475751) でも、この記録と実機未確認を区別している。本案内でこれらの実装検証を再実行したとは記録しない。

**ゲーム導入・起動、RitsuLibのdeferred登録・描画、正式PCK素材、save/co-op/性能は未確認。** 対象となるローカル版はv0.107.1 / 59260271、Godot 4.5.1、.NET 9、Spine 4.2系。最新版対応やゲーム互換性が確定したとは扱わない。

#8 / PR #20の検証対象commitは `b39a6bdec0e2d4ae28a6164a03f2c7d3476ef83f`、main統合commitは [`28c7762b8468245aa0323b781e35cd6836a355a7`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/28c7762b8468245aa0323b781e35cd6836a355a7)。[親の統合コメント](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20#issuecomment-6065248417) は汎用描画部・PCK工程の確認と、Regent固有hoverの後続分離を記録している。担当記録では実ビルド警告０・エラー０、Python 10件・C# 12件、合成Theoraを別の試験PCKから実再生した51項目、配布PCKの５scene instantiateが成功。これはstandalone Godotでの通常検証で、実ゲームのloader・Ritsu登録・UI/ロビー、Windows再生、save/co-op/性能は未確認。#21の７星座hoverは接点のみで未実装、承認済み素材カタログは空のまま。正式AI動画の生成や実ゲーム起動の成果として数えない。

#18 / PR #23の検証対象commitは `e7fa9d29efc69e1ee9cf2a8661c870c01e6647fc`、main統合commitは [`53d81472bbfb960c190e1ee6e67eaac06d27e447`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/53d81472bbfb960c190e1ee6e67eaac06d27e447)。[親の統合コメント](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/23#issuecomment-6065413654) はローカル制作ツールとしての確認を記録している。担当記録では33テストと、Silentの１page・Ironcladの４pageのread-only実抽出、元bytes・hash・PNG画素一致・入力状態不変を確認。Editor import/save/export、render round trip、残り３人の実抽出、ゲーム内確認、最新版は未確認。元Editor projectや高解像度PSDの復元、#9全体の完了を示すものではない。

判断の背景は [実装方式](../research/implementation/options.md)、動作の契約は [動作一覧](../research/motion/inventory.md)、モーション再利用の段階は [骨格再利用](../research/implementation/rig-reuse.md) にある。料金の資料は動画AI生成費用の比較で、rig・作画・Editor等を含む全工程費ではない。

## 状態や作業単位を更新するとき

全体Issue #1の進行欄、個別Issue本文・comments、実際のPRに時差がある場合は、対象commitと新しい指示・確認記録を照合する。closed・reviewなどのラベル一つで、デザイン承認・統合・実機確認の全てを推測しない。

更新する目的と根拠を先に書き、依存が解消したのか、成果が提出されたのか、未確認が検証されたのかを区別する。新しいPR、検証の版、承認コメント、残課題、確認日を揃え、ギャラリーとこの地図の対応を確かめる。

Issue分割・表の区分・文書の配置は、判断と作業の独立性に合わせて見直せる。例外や二重管理が増えたら、改名・統合・分割・旧形式の廃止を検討し、変更理由、新旧Issue/出力先の対応、既存リンクから辿れることを残す。[文書の拡張の考え方](../README.md#拡張を判断する考え方) / [開発運用](github-workflow.md) に従い、現在の分類を固定ルールにしない。
