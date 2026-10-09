# 開発の案内

[文書案内](../README.md) / [５人の現行デザイン](../design/characters/review-gallery.md) / [Issue地図](issue-map.md)

**2026-10-09（JST）確認。** mainの基準 [`6b190bb82a38052c42de869211586a032140ab84`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/6b190bb82a38052c42de869211586a032140ab84) には、DLL不要のPCK接続・配布（[PR #34](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/34)）と、５人分の本体・背景・まばたき・休憩姿・UI・用途別rig（[PR #35](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/35)）が統合済み。通常の制作・利用経路は **Godot描画＋所有ゲームからローカル生成するPCK**。

Silent v05は基準デザインのユーザー承認を保持。他４人のv02と実装用派生は委任に基づく制作採用。新しい画像ごとのユーザー回答待ちを完成工程の必須条件にはしない。Spine Professionalと動画生成AIは使用せず、不足画像はユーザー指定のCodex内蔵生成で補った。以前のAPI生成・失敗・承認範囲は [制作素材と来歴](../design/characters/production-assets.md) と各キャラの記録に残す。

## 現行の入口

| 確認したいこと | 入口 |
| --- | --- |
| 利用に必要な版・生成・導入・設定変更・削除 | [MOD README](../../mod/README.md) / [PCKのローカル生成と配布](pck-only.md)。`scripts/build_pck_mod.py` が現行入口 |
| 公開source bundleとローカル専用PCKの境界 | [公開とローカル生成の境界](pck-only.md#自作素材の公開とローカル生成の境界)。完成PCKは元scene scaffoldを含むため再配布しない |
| ５人の現行画像、承認・制作採用、旧案との比較 | [ギャラリー](../design/characters/review-gallery.md)。Silent v05／他４人v02を比較対象にする |
| 実装用画像・20用途別rig・５選択scene・25UI PNGの来歴と再組立 | [制作素材 v0.1](../design/characters/production-assets.md)。元rigと生成した用途別rigを区別する |
| 動作名・位相・mix・event・死亡待ちと独立物の契約 | [無料描画runtime](free-animation.md) / [動作一覧](../research/motion/inventory.md)。free-animationに残るC#/Harmony登録・空catalogの説明はPR #30時点の履歴。現在のscene末尾overlay接続は [PCK接続](pck-only.md#接続とcache) を参照 |
| Regentの７星座hover、入力・reduced motion・配置 | [Regent overlay](regent-overlay.md) / [PR #31](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/31)。Godot実装・standalone検証済み、最終native画面のQAは#11 |
| 実機QAの進行と完成までの残り | [Issue #11](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/11) / [完成工程](autonomous-delivery.md) / [Issue地図](issue-map.md) |
| Issue・所有範囲・worktree・PRの運用 | [開発運用](github-workflow.md) / [AGENTS.md](../../AGENTS.md) |

## 検証の境界

PCK担当の記録には **native helper 204項目**、standalone Godot **161項目（描画119＋選択42）**、Python **16件＋旧build 10件**の成功がある。[PR #34の検証記録](../../tests/pck_mod/validation.json)。receipt拡張子を `.receipt` に直した後のPython **17件＋旧build 10件**の成功は親の追加共有による。helperは元ゲームmainを起動しない資源・driver検査で、実プレイ確認とは区別する。本案内の作業でこれらを再実行していない。

親の実機QA共有（2026-10-09）では、元mainの通常PCKロード、５人分の選択アイコンと選択背景の表示、Ironcladのtop portraitを確認。Ironcladは元ID・カードを保持し、native UIのSTRIKEで敵HP **43→37**、overlay **idle_loop→attack→idle_loop** を確認した。選択人物の見切れはproduction descriptorで修正済み。

**全５人の実戦、商人・休憩、死亡/復活・音/VFX・速度・割込み、独立相棒/武器/Orb、保存/再開、co-op、競合、性能、通しプレイのQAは継続中。** 最新結果は [#11](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/11) で追う。親の正式報告先は `docs/validation/runtime-v01.md`（この基準版では未追加）。素材統合・helper成功・`affects_gameplay=false`だけでMOD完成や互換性確認済みとはしない。

対象は **Windows x64 v0.107.1 / 59260271**。ゲーム内MegaDot 4.5.1-m.12と、生成用の通常Godot 4.5.1 stable / Python 3.11以降を分ける。最新版・別ビルド対応は未確認。ゲーム更新後は旧PCKを停止・削除し、互換性を調査してから生成器を更新する。

## 過去の工程・調査を読む

以下は方式選定と検証履歴への入口。現行の導入手順は上のPCK文書を使う。

| 旧工程・資料 | 履歴と現在の位置付け |
| --- | --- |
| C#/RitsuLib基盤 #7 | [PR #14](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/14) / [build.md](build.md)。当時のビルド・依存・検証記録を保存。旧DLL build/exportは#33で停止 |
| 動画/posterの汎用選択再生 #8 | [PR #20](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20) / [select-playback.md](select-playback.md)。合成Theora・Ritsu登録の当時の検証で、現行はGodotのmesh・背景・PCK router |
| 元Spine抽出 #18・旧Editor PoC #9 | [PR #23](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/23) / [spine-extraction.md](spine-extraction.md) / [骨格再利用調査](../research/implementation/rig-reuse.md)。抽出はローカル参考ツール。#9は今回の工程から外してclosed、Editor往復・再skin成功を意味しない |
| 方式比較 | [実装方式](../research/implementation/options.md)。当時の比較・一次資料を保ち、現行採用はPCK文書で確認する |
| 動画AIの制作・尺・料金の検討 | [旧動画方針](../design/animation/video-production-v01.md) / [費用調査](../research/costs/video-generation.md)。今回は見送り。Spine購入や動画AI生成を完成の前提にしない |

## 案内を更新するとき

今回の現行化は [Issue #36](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/36)。旧C#/動画案内と初回レビューを現行入口から分け、PCK・素材統合・親のQA共有へ案内を切り替えた。過去の調査本文、生成失敗、ユーザー承認の対象は書き換えない。

新しい結果は対象版・commit・出典・承認/制作採用・未確認範囲とともに更新し、ギャラリーとIssue地図の対応、旧リンクから原記録へ戻れることを確認する。[文書の拡張の考え方](../README.md#拡張を判断する考え方) に沿い、PR merge・Issue closed・実機合格を一つの状態へまとめない。
