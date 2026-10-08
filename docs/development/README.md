# 開発の案内

[文書案内](../README.md) / [５人のレビュー候補](../design/characters/review-gallery.md) / [Issue地図](issue-map.md)

**2026-10-09（JST）確認。** mainには [Issue #7](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/7) / [PR #14](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/14) のC# MOD基盤、[Issue #8](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/8) / [PR #20](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20) の汎用選択再生・PCK工程、[Issue #18](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/18) / [PR #23](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/23) の元Spine抽出ツールが統合済み。本作業の開始基準は [`e21f02c7e021e2d7ba803cb1885842c8489e4a54`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/e21f02c7e021e2d7ba803cb1885842c8489e4a54)、PR #20の統合commitは [`28c7762b8468245aa0323b781e35cd6836a355a7`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/28c7762b8468245aa0323b781e35cd6836a355a7)。承認済み素材カタログは引き続き空で、５人の候補は別PRの未承認レビュー画像である。

基盤担当の記録では、ローカル **v0.107.1 / 59260271** を参照した実ビルドが **警告０・エラー０**、通常検証 **17件（C# 10件＋Python 7件）**、実コマンドの異常系 **６件** が成功。[ビルド手順と確認範囲](build.md#通常検証の結果) / [基準commitの検証記録](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/e21f02c7e021e2d7ba803cb1885842c8489e4a54/mod/validation/issue-7.json) に戻って確認できる。これは既存担当の検証記録で、本案内作成時にビルドを再実行した結果ではない。**実ゲームの導入・起動・実プレイ、deferred登録と描画、save/co-op/性能は未確認。**

## 目的から辿る

| 確認したいこと | 入口 |
| --- | --- |
| ５人の候補を同じ場所で見比べ、版・人物像・未完了条件を知る | [レビューギャラリー](../design/characters/review-gallery.md)。画像・プロンプト・来歴は各PR headのcommitで固定 |
| 開発の担当、依存、成果PRと現在の待ちを知る | [Issue地図](issue-map.md) / [全体Issue #1](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/1) |
| 固定したSDK・ローカル参照でC#基盤をビルドし、配布物を書き出す | [ビルド・検証・書き出し](build.md) |
| 選択再生の実装と、合成動画・PCKの単独検証を確認する | [PR #20](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20) / [commitで固定した手順](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/b39a6bdec0e2d4ae28a6164a03f2c7d3476ef83f/docs/development/select-playback.md)。汎用描画部としてmain統合済み・実ゲーム未確認 |
| 元Spineを作業用へ抽出し、authoringへ引き継ぐ | [PR #23](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/23) / [commitで固定した抽出手順](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/e7fa9d29efc69e1ee9cf2a8661c870c01e6647fc/docs/development/spine-extraction.md)。main統合済み・Editor往復は未確認 |
| Issue・所有範囲・worktree・PRの作業方法を確認する | [開発運用](github-workflow.md) / [AGENTS.md](../../AGENTS.md) |
| 元の動作、場面、trigger・eventの契約を確認する | [動作一覧](../research/motion/inventory.md) |
| ローダーと外観登録の方式比較を読む | [実装方式](../research/implementation/options.md)。実装済みの基盤は上のPR #14とビルド文書を参照 |
| 元Spineの再利用条件と、再skin/reweightのPoC範囲を知る | [骨格とモーションの再利用](../research/implementation/rig-reuse.md) |
| 選択動画の制作方針を読む | [動画制作方針](../design/animation/video-production-v01.md)。MiniMax H3 / Seedance 2.5は候補で、採用・生成品質は未確定 |
| 動画の生成尺・表示解像度・料金の仮定を確認する | [動画素材仕様と費用](../research/costs/video-generation.md)。動画AI生成料金の比較で、全制作工程の費用ではない |

選択再生 **#8** は汎用描画部として**完了・main統合済み**。Regentの原作７星座hoverの未実装は [**#21**](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/21) に分かれ、デザイン・選択動画方針待ち。元Spine抽出ツール **#18** も**完了・main統合済み**。Spine PoC **#9** はauthoring環境とデザイン承認待ち、正式素材 **#10** と実機QA **#11** は先行成果待ち。具体的な依存・出力先は [Issue地図](issue-map.md) で確認する。抽出の前準備、Editorでの往復、女性デザインへの再skin、実機表示を別の達成として追う。

## 案内を更新するとき

新しいPRや確認結果が出たら、判断に必要な出典・対象commit・版・承認状態・未確認事項を揃え、ギャラリーとIssue地図の対応を確認する。調査書に残る過去の進行記述や、Issueのラベルだけから、実装・実機・承認の状態を推測しない。

文書や分類は [拡張の考え方](../README.md#拡張を判断する考え方) に合わせて変更できる。読む人が候補から来歴へ、開発作業から依存と検証結果へ戻れることを優先し、再編の理由・移行先・リンクの確認結果を残す。
