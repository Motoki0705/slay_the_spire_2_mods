# レビューと開発のIssue地図

[開発の案内](README.md) / [５人のレビュー候補ギャラリー](../design/characters/review-gallery.md) / [全体Issue #1](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/1)

確認日: **2026-10-09（JST）**。Issue本文・comments、PRの提出・統合状態、制作記録に基づく案内。実担当はIssue本文のエージェント名で、GitHub assigneeは **Motoki0705**。本案内は [Issue #19](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/19) / `review-navigation` の成果で、案内自身のPRは同Issueから追跡する。

## ５人のデザインレビュー

５件ともmain未統合のdraft PRで、画像生成・担当の目視と通常検証の記録がある。**ユーザーのデザイン承認は未取得。** 画像、提案された人物像、全文プロンプト、来歴は [ギャラリー](../design/characters/review-gallery.md) でPR head commitに固定している。

| Issue | 実担当 | 比較する候補と状態 | 成果PR |
| --- | --- | --- | --- |
| [#3 Ironclad](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/3) | `art-ironclad` | v0.1、レビュー待ち。鎧・炎・ポップさと５人比較は未確定 | [#12](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/12) |
| [#2 Silent](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/2) | `art-silent` | v0.5修正後、レビュー待ち。膝下の革バンド省略で装備保持は未完了 | [#13](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/13) |
| [#4 Regent](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/4) | `art-regent` | v0.1、レビュー待ち。従者へ向く視線と慌てる表情は控えめ | [#15](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/15) |
| [#5 Necrobinder](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/5) | `art-necrobinder` | v0.1 corrected、レビュー待ち。Ostyの左手条件は未確認 | [#17](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/17) |
| [#6 Defect](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/6) | `art-defect` | v01、レビュー待ち。オーブ配置と驚きの強さは未確定 | [#16](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/16) |

この単独キャラのv0.1/v01は、不採用の５人集合案v0.1/v0.2とは別。生成成功、PR提出や統合、外観承認を一つの完了状態にまとめない。旧案の不採用理由はギャラリーから辿れる。

## 実装・制作・QAの依存

| Issue | 実担当 | 確認時点の状態 | 依存・次に必要なもの | 成果・出力先の案内 |
| --- | --- | --- | --- | --- |
| [#7 MOD基盤](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/7) | `engine-bootstrap` | **完了・main統合済み**。Issueはclosed | 後続のruntime・素材・実機確認へ進む。基盤の承認済み素材カタログは空 | [PR #14](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/14) / [build.md](build.md) / [固定した検証記録](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/e21f02c7e021e2d7ba803cb1885842c8489e4a54/mod/validation/issue-7.json) |
| [#8 選択再生・汎用描画部](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/8) | `engine-select` | **完了・main統合済み**。Issueはclosed | #7は統合済み。合成動画・poster・PCKの単独検証済み。実ゲーム接続は未確認、正式素材は未収録。Regent固有hoverは#21へ分離 | [PR #20](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20) / [固定した手順](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/b39a6bdec0e2d4ae28a6164a03f2c7d3476ef83f/docs/development/select-playback.md) / [固定した検証記録](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/b39a6bdec0e2d4ae28a6164a03f2c7d3476ef83f/mod/validation/issue-8.json) |
| [#21 Regent星座hover](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/21) | `regent-select-overlay`（担当予定） | **デザイン・選択動画方針待ち**。原作７星座hoverは未実装 | #8は完了。#4 / #10のデザイン・選択動画方針を基に、独立layerの入力・表示・reduced motion・解放を決める | Issue本文の所有予定を参照。予定文書: `docs/development/regent-overlay.md` |
| [#18 元Spine抽出ツール](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/18) | `spine-extraction` | **draft提出・レビュー待ち、main未統合**。#9の前準備 | combat本体５人の明示対応。v0.107.1 / 59260271のSilent・Ironcladで実抽出確認。Editor往復・他３人の実抽出は未確認 | [PR #23](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/23) / [固定した抽出・引継ぎ手順](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/e7fa9d29efc69e1ee9cf2a8661c870c01e6647fc/docs/development/spine-extraction.md)。抽出生データはローカルのみ |
| [#9 Spine PoC](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/9) | `spine-poc` | **authoring環境・デザイン承認待ち** | 先行#7 / #2。適切なSpine 4.2 authoring環境とユーザー承認が必要。#18の抽出後も、Editorでの往復と再skin/reweightを確認する | [骨格再利用調査](../research/implementation/rig-reuse.md)。予定文書: `docs/development/spine-poc.md` |
| [#10 正式素材](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/10) | `asset-production` | **依存待ち** | #2〜#6のデザインレビューと#9。承認を反映した部位・選択動画・UI・戦闘外素材へ展開 | Issue本文の出力先、[動作一覧](../research/motion/inventory.md)、[動画制作方針](../design/animation/video-production-v01.md)、[生成費用調査](../research/costs/video-generation.md) |
| [#11 実機QA](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/11) | `runtime-qa` | **依存待ち**、実ゲーム起動・実プレイは未実施 | #8 / #9 / #10。版と素材を固定し、状態遷移・描画・保存・co-op・性能を確認する | 予定範囲: `tests/runtime/**`、`docs/validation/**`、不具合Issue |

#18の抽出成功は、#9のEditor import/export成功や新デザインの可動確認を意味しない。#9全体を閉じる成果ではない。#8は汎用描画部・PCK工程として完了し、Regentの７星座hoverを#21へ分離した。再生fixtureは正式なAI動画ではなく、#10の素材制作完了として数えない。予定文書は、そのIssueで実際に提出されてからリンクを追加する。

## 検証済みと未確認の境界

#7 / PR #14の統合commitは `e21f02c7e021e2d7ba803cb1885842c8489e4a54`。担当記録には、実ビルド **警告０・エラー０**、通常 **17件（C# 10＋Python 7）**、実コマンドの異常系 **６件**、ZIPの３ファイル構成と依存DLL非混入の確認がある。[親の統合コメント](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/14#issuecomment-6064475751) でも、この記録と実機未確認を区別している。本案内でこれらの実装検証を再実行したとは記録しない。

**ゲーム導入・起動、RitsuLibのdeferred登録・描画、正式PCK素材、save/co-op/性能は未確認。** 対象となるローカル版はv0.107.1 / 59260271、Godot 4.5.1、.NET 9、Spine 4.2系。最新版対応やゲーム互換性が確定したとは扱わない。

#8 / PR #20の検証対象commitは `b39a6bdec0e2d4ae28a6164a03f2c7d3476ef83f`、main統合commitは [`28c7762b8468245aa0323b781e35cd6836a355a7`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/28c7762b8468245aa0323b781e35cd6836a355a7)。[親の統合コメント](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20#issuecomment-6065248417) は汎用描画部・PCK工程の確認と、Regent固有hoverの後続分離を記録している。担当記録では実ビルド警告０・エラー０、Python 10件・C# 12件、合成Theoraを別の試験PCKから実再生した51項目、配布PCKの５scene instantiateが成功。これはstandalone Godotでの通常検証で、実ゲームのloader・Ritsu登録・UI/ロビー、Windows再生、save/co-op/性能は未確認。#21の７星座hoverは接点のみで未実装、承認済み素材カタログは空のまま。正式AI動画の生成や実ゲーム起動の成果として数えない。

#18 / PR #23の検証対象commitは `e7fa9d29efc69e1ee9cf2a8661c870c01e6647fc`。担当記録では33テストと、Silentの１page・Ironcladの４pageのread-only実抽出、元bytes・hash・PNG画素一致・入力状態不変を確認。Editor import/save/export、render round trip、残り３人の実抽出、ゲーム内確認、最新版は未確認。元Editor projectや高解像度PSDの復元、#9全体の完了を示すものではない。

判断の背景は [実装方式](../research/implementation/options.md)、動作の契約は [動作一覧](../research/motion/inventory.md)、モーション再利用の段階は [骨格再利用](../research/implementation/rig-reuse.md) にある。料金の資料は動画AI生成費用の比較で、rig・作画・Editor等を含む全工程費ではない。

## 状態や作業単位を更新するとき

全体Issue #1の進行欄、個別Issue本文・comments、実際のPRに時差がある場合は、対象commitと新しい指示・確認記録を照合する。closed・reviewなどのラベル一つで、デザイン承認・統合・実機確認の全てを推測しない。

更新する目的と根拠を先に書き、依存が解消したのか、成果が提出されたのか、未確認が検証されたのかを区別する。新しいPR、検証の版、承認コメント、残課題、確認日を揃え、ギャラリーとこの地図の対応を確かめる。

Issue分割・表の区分・文書の配置は、判断と作業の独立性に合わせて見直せる。例外や二重管理が増えたら、改名・統合・分割・旧形式の廃止を検討し、変更理由、新旧Issue/出力先の対応、既存リンクから辿れることを残す。[文書の拡張の考え方](../README.md#拡張を判断する考え方) / [開発運用](github-workflow.md) に従い、現在の分類を固定ルールにしない。
