# 制作・配布・実機QAのIssue地図

[開発の案内](README.md) / [５人の現行ギャラリー](../design/characters/review-gallery.md) / [全体Issue #1](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/1)

更新日: **2026-10-09（JST）**。今回完了した制作対象は [場面別モーション v0.2 #48](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/48)。H3選択動画５本と15姿勢・rig・再生runtimeはmainに統合済み、実機QA・0.2.0の所有導入は#62で対象範囲を完了、READMEと媒体整理・専用導入ガイドは#63 / PR #67で完了する。導入先からの起動や#45/#46の残課題を、完了した確認へ含めない。実担当はIssue本文のエージェント名で確認し、GitHub assigneeとは区別する。

## v0.2の素材・実装・実機QA

| Issue / 担当 | 成果・状態 | 証拠と確認の範囲 |
| --- | --- | --- |
| [#48 場面別motion](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/48) / 親 | 対象範囲の実機QA・デプロイを完了。方針PR #56、15姿勢PR #60、５動画PR #61を統合し、最終媒体・手順をPR #67へ収録 | [制作画像](../validation/media/contextual-v02/README.md) / [H3動画記録](../../output/videogen/README.md)。15採用姿勢/16出力、５本をH3標準768Pで実生成。対象版の実機QA・導入は#62、最終PR統合判断は親 |
| [#49 H3生成CLI](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/49) / `h3_api` | closed、[PR #54](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/54)統合済み | [H3制作契約](../research/costs/minimax-h3-production-v02.md)。公式仕様、再開とtask照合、秘密情報を公開記録へ残さない経路 |
| [#50 選択動画runtime](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/50) / `motion_runtime_v02` | closed、[PR #52](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/52)統合済み | [PCK再生・静止fallback・場面profile](selection-video-v02.md)。通常Godot 315項目、Python 23件と合成PCK試験。H3素材の実ゲーム再生は#62 |
| [#51 姿勢・演技設計](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/51) / `pose_direction_v02` | closed、[PR #55](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/55)統合済み | [選択・戦闘・商人・休憩の設計](../design/animation/contextual-motion-v02.md)。設計提案と最終画像の制作採用を区別 |
| [#53 場面別rig](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/53) / `contextual_rigging` | closed、[PR #58](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/58)統合済み | [15専用rig・剛体武器・支持点・VFX](contextual-rigs-v02.md) / [単独Godot実演](../../tests/assets/contextual-evidence/README.md)。新15rigはcontextual_v02、選択５rigはlegacy |
| [#57 H3 credits経路](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/57) | closed、[PR #59](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/59)統合済み | [H3契約](../research/costs/minimax-h3-production-v02.md)。明示的なbilling経路を追加。ゲーム利用時のAPI実行ではない |
| [#62 実機QA・納品](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/62) / `native_motion_qa` | 対象範囲の実機QA・0.2.0の所有導入完了、[PR #65](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/65)統合済み | ５選択のloop/切替/退出/静止fallback、Regent７hover、15場面と代表カード・独立Osty/剣/Orb。[媒体索引](../validation/media/motion-v02-runtime/README.md) / [QA報告](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/19ed278fb58ff1807b7e01e3f6c496133f17a0c9/docs/validation/motion-v02.md)。candidate02でRegent休憩の旧影を修正。他の全pack資源は候補01とhash一致し、その範囲の実録を引き継ぐ。導入先からの起動は未確認 |
| [#63 README・媒体](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/63) / `motion_readme_v02` | 媒体・版・確認範囲の整理と通常QA、親による[専用導入ガイド](../usage/installation.md)を完了。[PR #67](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/67) | [README](../../README.md) / [媒体・hash・変換記録](../validation/media/motion-v02-runtime/README.md) / [軽量生成プレビュー](../validation/media/motion-v02-runtime/generated/README.md)。ゲーム実録・生成素材・単独rig実演を区別 |

依存は **#49/#57のH3受付＋#51の演技 → 親の15姿勢・５動画＋#50のruntime＋#53のrig → #62の実機QA・必要修正 → #63の現行媒体 → 親のPR統合・納品判断**。README担当はゲームや導入物を操作せず、最終QAと媒体の版を照合する。Spine Professionalは使用せず、配布はPCK-only。選択動画の再生中は人物puppetを重ねず、Osty・剣・OrbとRegent７hoverは独立制御を維持する設計。

## ５人のデザインと制作採用

**Silent v05のデザインはユーザー承認済み。他４人v02は自律制作の委任に基づく制作採用。５件のデザインPRはmain統合済み・Issueはclosed。** 派生素材・動作・UIへユーザー承認を拡張しない。現行画像・固定commit・旧案は [ギャラリー](../design/characters/review-gallery.md) から辿る。

| Issue / 担当 | 現行デザインと記録 | 統合済みPR |
| --- | --- | --- |
| [#3 Ironclad](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/3) / `art-ironclad-production` | v02、薄い装甲と繊細な身体。委任に基づく制作採用。[v02記録](../design/characters/ironclad/review-v02.md) / [制作](../design/characters/ironclad/production.md) | [#12](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/12) |
| [#2 Silent](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/2) / `art-silent` | v05、基準デザインのユーザー承認。革バンド省略の差分は残る。[承認範囲](../design/characters/silent/review-v05.md#ユーザー承認2026-10-09) / [制作](../design/characters/silent/production.md) | [#13](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/13) |
| [#4 Regent](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/4) / `art-regent-production` | v02、小さい成人の身体と大きな王衣。委任に基づく制作採用。本人と玉座/運び手を分離。[v02記録](../design/characters/regent/review-v02.md) / [制作](../design/characters/regent/production.md) | [#15](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/15) |
| [#5 Necrobinder](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/5) / `art-necrobinder-production` | v02、腰の絞りを緩めた衣服とOstyへの合図。委任に基づく制作採用。概念画のOstyの左手判定は未確定。[v02記録](../design/characters/necrobinder/review-v02.md) / [制作](../design/characters/necrobinder/production.md) | [#17](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/17) |
| [#6 Defect](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/6) / `art-defect-production` | 基準デザインv02、細い機構と補修前腕の対比。委任に基づく制作採用。初期素材はbodyと休憩の座位を共有し、新しい場面別素材は#48/#53で分離。[v02記録](../design/characters/defect/review-v02.md) / [制作](../design/characters/defect/production.md) | [#16](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/16) |

[#24 プロンプト・絵作り調査](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/24) はclosed、[PR #25](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/25) 統合済み。[調査](../research/art-direction/non-generic-characters.md) と [４人の改訂案](../design/characters/slender-revision-brief.md) を後続v02制作に反映した。調査段階の仮説と実画像の採用判断は別に記録する。

## v0.1の実装・素材・QA（履歴）

v0.1の実機修正・導入物・QA記録は [PR #44](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/44)、媒体は [#41 / PR #43](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/43)、納品時の案内は [PR #47](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/47) へ固定されている。

| Issue / 担当 | 成果・状態 | 証拠と確認の範囲 |
| --- | --- | --- |
| [#26 無料描画runtime](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/26) / `free-animation-runtime` | 完了、PR #30 / #34 / #44。Godot meshと元driver観測 | [動作・rig契約](free-animation.md)。５人の代表カード・状態遷移を実機確認。全カードや全速度の保証ではない |
| [#21 Regent星座hover](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/21) / `regent-select-overlay` | 完了、PR #31 | [Regent overlay](regent-overlay.md)。実機で７中心の反応と選択・出発の入力を確認 |
| [#28 Silent素材](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/28) | 完了、PR #29 | [Silent制作記録](../design/characters/silent/production.md)。ユーザー承認は基準v05デザイン、用途別派生は委任による制作採用 |
| [#10 正式素材](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/10) / `production-surfaces`・親 | 完了、PR #32 / #35 / #44。５人の本体・背景・まばたき・休憩姿・20rig・選択scene・25UI PNG | [制作素材](../design/characters/production-assets.md)。不足４背景・４閉じ目は内蔵画像生成で補完。実機５人の選択・商人・休憩を確認 |
| [#33 PCK接続・配布](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/33) / `pck-only-delivery` | 完了、PR #34 / #44。source bundleと所有ゲームからのローカル生成、verify/install/uninstall | [PCK手順](pck-only.md)。最終PCKは20rig・288資源・skippedなし。元ゲームのMODフォルダへ所有installerで導入済み |
| [#37 硬い武器](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/37) / `weapon_rig` | 完了、PR #39 / #44。PNGを保ち剣/短剣/鎌を手へ固定 | [武器rig](weapon-rig.md)。5114形状チェック、実機Ironcladの刀身を再確認 |
| [#40 休憩表示](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/40) / 親 | 完了、PR #44。保存済placeholderの除外と座席のorigin/サイズ | 実機の５人の休憩を確認。未知の構造では元表示へ戻す |
| [#42 Necrobinderの炎](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/42) / 親・`qa_finish` | 完了、PR #44。頭と鎌のanchor、明示倍率とfallback時の復元 | 候補05の戦闘・商人・休憩、描画だけのdeath/reviveで炎の消灯/点灯を確認。独立Ostyを維持 |
| [#11 実機QA](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/11) / 親・`qa_finish` | 対象範囲のQAとローカル納品を完了、PR #44 | [実機QA記録](../validation/runtime-v01.md)。元保存400ファイルとゲーム原本のhashは一致。未確認は下記#45/#46へ分離 |
| [#36 案内](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/36) / `delivery_docs` | 完了、PR #38 | [開発案内](README.md) / [現行ギャラリー](../design/characters/review-gallery.md)。最終状態は#1の納品更新で反映 |
| [#41 README可視化](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/41) / `visual_readme` | 実機５人の画像・約６秒のGIF/MP4・修正前後を制作、PR #43 | [README](../../README.md)。画像ごとの版・日付・変換・hashを媒体索引へ記録 |

#1の完成条件と制作上の権限は [自律完成工程](autonomous-delivery.md)。v0.1は動画AIを使用せず、当時のREADMEの動画はゲーム実録。[旧媒体索引](../validation/media/progress-2026-10-09/README.md)に版と撮影範囲を保持する。

## v0.1の確認履歴と継続するQA

５人の選択・代表カード・商人・休憩、独立したOsty/剣/Orb、Regentの７星座を実機確認。Silentは通常戦闘から死亡・結果画面まで、IroncladとSilentは保存再開も確認した。最終候補05でNecrobinderの炎を再確認して導入した。全キャラの全試験を最終PCKで再実行した意味ではない。キャラ別の操作・候補は [QA記録](../validation/runtime-v01.md) にある。

Python 17＋10件、Godot animation 126件・selection 42件とfixture PCKが成功。先行のnative resource helper 204件と武器形状5114件は別段階の検証。validatorは指定・試行・完了0回。

| 次に確認する範囲 | 追跡先 |
| --- | --- |
| 協力プレイ・接続/再接続・実死亡後復帰・混在MOD | [#45](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/45)。実動作は未確認。オフラインの試行ではマルチ画面独自のSteam初期化が失敗した |
| 全act通しプレイ、速度・割込み・音/event、他renderer/他MOD、厳密な性能、終了ログ（Defect通常被弾はv0.2で確認済み） | [#46](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/46)。未確認と未切分けを分け、原因が分かる前に無害・修正済みとしない |

これらは実施済みのQAに合格した項目として数えない。現在の対象はWindows v0.107.1 / 59260271のみ。更新版はscene・driver・資源契約を再確認してから対応する。

## 旧工程と移行

| Issue | 当時の成果と現行工程への対応 |
| --- | --- |
| [#7 C#基盤](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/7) | closed・[PR #14](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/14) 統合。依存・空catalog・DLL配布は当時の仕様。[build.md](build.md) は履歴、現行build/exportは#33の入口を使う |
| [#8 動画/poster再生](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/8) | closed・[PR #20](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20) 統合。合成Theoraによる汎用描画検証は [select-playback.md](select-playback.md)。v0.1は動画なしのGodot描画、v0.2は#50のPCK動画再生。Regent固有hoverは#21から継続 |
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
