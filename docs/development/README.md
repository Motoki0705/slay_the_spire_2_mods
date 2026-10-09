# 開発の案内

[文書案内](../README.md) / [５人の現行デザイン](../design/characters/review-gallery.md) / [Issue地図](issue-map.md)

**2026-10-09（JST）更新。** v0.2は５本のMiniMax-H3 / 768P選択動画と、戦闘・商人・休憩の専用15姿勢・rigを接続済み。通常の制作・利用経路は **H3選択動画＋場面別Godot描画＋所有ゲームからローカル生成するPCK**。外観と動きは [README](../../README.md)、版・撮影範囲・素材との区別は [v0.2媒体索引](../validation/media/motion-v02-runtime/README.md) から評価できる。実機QA・0.2.0の所有導入は [#62](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/62) で対象範囲を完了、READMEの可視化と[専用導入ガイド](../usage/installation.md)は [#63 / PR #67](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/67) にまとめた。導入先からの起動は未確認。

Silent v05は基準デザインのユーザー承認を保持。他４人のv02、新15姿勢とH3動画は委任に基づく制作採用。画像はCodex内蔵imagegenを使用し、選択動画AIの旧見送りは今回の明示指示で更新された。Spine Professionalは使用しない。以前のAPI生成・失敗・承認範囲は [v0.1制作素材と来歴](../design/characters/production-assets.md) と各キャラの記録に残す。

## 現行の入口

| 確認したいこと | 入口 |
| --- | --- |
| 利用に必要な版・生成・導入・設定変更・削除 | [画像付き導入ガイド](../usage/installation.md) / [MOD README v0.2.0](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/19ed278fb58ff1807b7e01e3f6c496133f17a0c9/mod/README.md) / [PCKのローカル生成と配布](pck-only.md)。`scripts/build_pck_mod.py` が現行入口 |
| 公開source bundleとローカル専用PCKの境界 | [公開とローカル生成の境界](pck-only.md#自作素材の公開とローカル生成の境界)。完成PCKは元scene scaffoldを含むため再配布しない |
| ５人の現行画像、承認・制作採用、旧案との比較 | [ギャラリー](../design/characters/review-gallery.md)。Silent v05／他４人v02を比較対象にする |
| ５本のH3動画、無音loop・poster・入力/出力hash | [生成動画の記録](../../output/videogen/README.md) / [H3契約](../research/costs/minimax-h3-production-v02.md)。原生成８秒と配布loop約7.67秒を区別する |
| 場面専用の15姿勢・rig・剛体武器・接地 | [演技設計](../design/animation/contextual-motion-v02.md) / [場面別rig](contextual-rigs-v02.md) / [制作比較](../validation/media/contextual-v02/README.md) |
| 動画のPCK再生、aspect-cover、静止fallback、切替 | [選択動画・場面別runtime](selection-video-v02.md)。動画再生中は同じ人物のpuppetを重ねない |
| 基準画像・選択用legacy rig・UIの来歴と再組立 | [制作素材 v0.1（履歴）](../design/characters/production-assets.md)。選択５rigと新15rigを区別する |
| 動作名・位相・mix・event・死亡待ちと独立物の契約 | [無料描画runtime](free-animation.md) / [動作一覧](../research/motion/inventory.md)。free-animationに残るC#/Harmony登録・空catalogの説明はPR #30時点の履歴。現在のscene末尾overlay接続は [PCK接続](pck-only.md#接続とcache) を参照 |
| Regentの独立７星座hover、入力・reduced motion・配置 | [Regent overlay](regent-overlay.md) / [選択runtime](selection-video-v02.md)。動画へ操作領域を焼き込まない。新動画との実機７hover・入力確認は#62で実施済み |
| v0.2の実機QAと残る確認 | [QA #62](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/62) / [媒体索引](../validation/media/motion-v02-runtime/README.md) / [協力プレイ #45](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/45) / [追加QA #46](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/46) / [Issue地図](issue-map.md) |
| Issue・所有範囲・worktree・PRの運用 | [開発運用](github-workflow.md) / [AGENTS.md](../../AGENTS.md) |

## 検証の境界

v0.2のruntimeは通常Godot **315項目**とPython **23件**、合成PCKのreadback/decodeを確認した。[runtime検証](selection-video-v02.md#通常検証)。15rigの [単独描画・武器・接点試験](contextual-rigs-v02.md#検証結果と媒体) と、５本の [H3生成・loop検査](../../output/videogen/README.md) は別工程で、ゲーム内のカード/event・座席・VFX・負荷の確認を代替しない。これらは依存実装時の結果。実機QA #62では最終候補02の全364資源をhash照合、５選択と全15場面、代表カード・独立Osty/剣/Orb、全５人×６fallback遷移を確認した。Regentの休憩の旧影だけを修正し、他のpack資源は候補01とhash一致。今回の変更に対応するcompiler４件・PCK builder19件・timeout診断１件とQA GDScript parseも成功。validatorは0回。

最終candidate02の0.2.0はゲーム終了後に所有installerで導入し、receipt/実ファイルhash、原gameの４pin、今回採取した元プロフィール400ファイルの不変を確認した。実機操作は隔離コピーで行い、導入先からの起動は未確認。被弾はDefectだけ通常敵攻撃、他４人はQA console damage。死亡・復活はIronclad/Necrobinderの描画試験で、実死亡・co-op復活へ読み替えない。休憩はAct 1のみ。全Act・カード・速度・他renderer/他MOD・厳密な性能、particle非対応警告と終了時ログの原因は#45/#46に残る。[v0.2 QA報告](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/19ed278fb58ff1807b7e01e3f6c496133f17a0c9/docs/validation/motion-v02.md)。

### v0.1の実機納品と通常検証（履歴）

修正後の通常検証はPython **17件＋旧build 10件**、Godot **126＋42項目**とfixture PCKのexport/readback。先行段階のnative helper **204項目**、武器形状 **5114項目**を最終候補の実プレイ検証として合算しない。[機械可読の最終記録](../../tests/runtime/validation.json)。validatorは指定・試行・完了0回。

元mainの通常PCKロード、５人の選択・代表カード・商人・休憩、独立したOsty・剣・Orbを確認した。Silentの通常戦闘の死亡～結果画面、Ironclad戦闘/Silent開始イベントの保存再開も確認済み。全キャラの全カード・全速度・真の協力復活を網羅したものではない。候補05でNecrobinderの炎を再確認し、ローカル生成物を所有ゲームのMODフォルダへ導入した。元保存400ファイルと原ゲームの固定hashは一致。

v0.1納品時は協力プレイを#45、Defect通常被弾の追加・全act通しプレイ等を#46へ残した。Defect通常被弾はv0.2で確認済み。他の継続範囲は上のv0.2記録を使い、当時の試験と未確認は [v0.1 QA記録](../validation/runtime-v01.md) から辿る。

対象は **Windows x64 v0.107.1 / 59260271**。ゲーム内MegaDot 4.5.1-m.12と、生成用の通常Godot 4.5.1 stable / Python 3.11以降を分ける。最新版・別ビルド対応は未確認。ゲーム更新後は旧PCKを停止・削除し、互換性を調査してから生成器を更新する。

## 過去の工程・調査を読む

以下は方式選定と検証履歴への入口。現行の導入手順は上のPCK文書を使う。

| 旧工程・資料 | 履歴と現在の位置付け |
| --- | --- |
| C#/RitsuLib基盤 #7 | [PR #14](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/14) / [build.md](build.md)。当時のビルド・依存・検証記録を保存。旧DLL build/exportは#33で停止 |
| 動画/posterの汎用選択再生 #8 | [PR #20](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/20) / [select-playback.md](select-playback.md)。合成Theora・Ritsu登録の当時の検証。現行は#50のPCK動画再生と#53の場面別rig |
| 元Spine抽出 #18・旧Editor PoC #9 | [PR #23](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/23) / [spine-extraction.md](spine-extraction.md) / [骨格再利用調査](../research/implementation/rig-reuse.md)。抽出はローカル参考ツール。#9は今回の工程から外してclosed、Editor往復・再skin成功を意味しない |
| 方式比較 | [実装方式](../research/implementation/options.md)。当時の比較・一次資料を保ち、現行採用はPCK文書で確認する |
| 動画AIの制作・尺・料金の旧検討 | [旧動画方針](../design/animation/video-production-v01.md) / [費用調査](../research/costs/video-generation.md)。v0.1の見送りを保存。v0.2は [H3 / 768Pの新契約](../research/costs/minimax-h3-production-v02.md) と実生成記録を使う |

## 案内を更新するとき

初回の現行化は [Issue #36](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/36)、v0.1の納品更新は#1 / PR #47。今回の [#63](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/63) でH3・15姿勢・実機QA #62へ入口を切り替え、旧実録は履歴へ残す。過去の調査本文、生成失敗、ユーザー承認の対象は書き換えない。

新しい結果は対象版・commit・出典・承認/制作採用・未確認範囲とともに更新し、ギャラリーとIssue地図の対応、旧リンクから原記録へ戻れることを確認する。[文書の拡張の考え方](../README.md#拡張を判断する考え方) に沿い、PR merge・Issue closed・実機合格を一つの状態へまとめない。
