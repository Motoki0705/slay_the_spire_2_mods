# v0.1 実ゲーム確認

対象はWindows **v0.107.1 / 59260271 / MegaDot 4.5.1-m.12**。ゲームの原main sceneを起動し、PCKだけのMODを内蔵ModManagerに読み込ませた。追加DLLは使用していない。検証用にコピーしたゲーム、専用user://、`--force-steam=off` を使用した。

この文書は #11 の通常QA。validatorはユーザー未指定のため、指定・試行・完了とも **0回**。公開用の見た目の入口は [README](../../README.md)。媒体のキャプチャ版とファイルhashは媒体索引、実装の対象は `tests/runtime/validation.json` に記録する。

最終成果物は **production-candidate-05**、PCK SHA-256は `da0bafc06f85520b61f2550fdb2f2bef0cc3f8d1be6023764c0891d5301a1781`。20rig、288格納資源、`skipped=[]`。入力素材114件は最終作業ツリーと照合済み。候補05では候補04からNecrobinderの炎の高さだけを変更し、３場面を改めて確認した。全キャラのカード操作は段階的な候補で実施しており、全試験を最終PCKで繰り返したという意味ではない。

## 確認した動作

| キャラ | 実際のカード操作・効果 | 商人・休憩 | 死亡・復活の範囲 |
| --- | --- | --- | --- |
| Ironclad | Strikeで敵HP43→37、Demon Formのcast、敵攻撃で80→68 | 商人表示、調整後の休憩の大きさと位置を確認 | Lizard Tailによる死亡防止。剣の曲がりを#37で修正し、候補04の実機でdeath→revive描画と刀身の形を再確認 |
| Silent | Strike、Deadly Poison、Shiv、敵攻撃で70→58 | 商人表示。#40修正後に休憩がactive、元表示との切替・復元と休憩選択を確認 | 通常マップから入った戦闘で死亡→Game Over→集計→メニュー。Lizard Tailによる死亡防止 |
| Regent | Strike、Venerate、Sovereign Blade、被弾。独立した剣の出現・攻撃を確認 | 商人・休憩ともactive | 元NCreatureの登録メソッドを使う**描画だけのdeath→revive試験** |
| Necrobinder | Strike、Bodyguard、Unleash、本人への20ダメージ。Ostyの独立した攻撃・HP変化 | 候補05で戦闘・商人・休憩の炎が髪のすぐ上にあることを目視確認 | 候補05の元NCreatureによる描画だけのdeath→reviveで、炎が非表示→表示。HPは66/66のまま |
| Defect | Strike、Zap、Dualcast。Orb数1→2→1と解放、敵の縮小効果に身体・Orb配置が追従 | 商人・休憩ともactive | 元NCreatureを使う描画だけのdeath→revive試験 |

全５人の選択画面・ボタン・上部アイコンを実機で確認。新しい５背景と本体を表示し、頭・足の見切れを修正した。Regentは７中心へマウスを移し、７つの図形が反応すること、離脱、キャラ選択・出発を妨げないことを確認した。会話で使う小アイコンも元のUI経路から新しい顔を表示した。

Godot側の観測では、カード操作に伴う元driverの `idle_loop → attack / cast / shiv / attack_sovereign / hurt → idle_loop` と、カスタム表示の `active` 継続を記録した。演技を手動で再生する試験と、カード・HP・ターンを通す試験を分けている。**Lizard Tailは死亡防止であり、協力プレイの実死亡後の復活とは別**。

## 実機で見つけて直した点

- installerのreceiptを `.json` から `.receipt` へ変更。ゲームがmods内の全JSONをmanifestとして読むため、不正manifestのログを出していた。
- 選択背景の親が2560×1200、画面上では拡大・はみ出しを持つことに合わせ、各画像のalpha範囲から人物の高さと位置を調整。
- Ironcladの長い剣が足の重みに引かれて曲がる問題を、３人の武器の剛体meshで修正。PNGは変更せず、手の骨へ武器を固定する。[方式・数値と目視の証拠](../development/weapon-rig.md)。
- Silentの休憩sceneに、実行時15個と保存済placeholder30個のSpineMesh2Dがあった。所有者を持つ保存ノードを対応から除外し、実行時のmesh数とdraw orderが一致するときだけ抑止する。未知の構造は元表示へ戻す。ノードの削除やSpine driverの停止は行わない。
- 休憩の親scaleと座席に合わせ、休憩用rigのoriginをhipへ、表示高をキャラ別に調整。戦闘用の大きさは維持する。
- Necrobinderの頭と鎌の既存VFXを自作rigのanchorへ接続。明示した炎のサイズ倍率は元値へ掛け、位置とともにfallback時に復元する。元の炎の表示イベント、回転、材質、Ostyの処理は保つ。

候補05の元表示との比較では、戦闘の炎のglobal scaleは約0.14658→0.24430→0.14658となり、明示倍率0.6の適用・解除・再適用を確認。休憩でも倍率0.65の解除と位置の復元を確認した。Ostyの炎の位置・倍率は切替前後で一致した。キャプチャと元のtree/観測JSONのhashは `tests/runtime/validation.json` に記録する。商人の倍率は0.4。

## 保存と検証環境

元の保存の基準は400ファイル。検証用コピーだけを操作し、元プロフィールは起動していない。最終の保存比較と導入結果は下記の納品記録と `tests/runtime/validation.json` に記録する。実機用コピーのexe・PCK・DLL・release_infoは固定した版のhashと照合した。Windowsのapplication controlや証明書・Defender設定は変更していない。

テスト用の進行では４人の解放epochを明示し、Nativeコンソールでカード・エネルギー・部屋を準備した。配布物にはこれらの操作・harness・検証用進行を含めない。カードのプレイは通常のゲームUIから行った。入力イベントだけではゲームが参照するOSマウス位置が変わらなかったため、検証用harnessは自身のviewportへのwarpとnative入力を使う。

検証用コンソールの部屋移動は、開始イベントを通常UIで終えてから行う。起動途中の部屋移動はイベント初期化と競合し、元ゲームの例外を発生させた。また、debug部屋へ移った後の死亡では、元ゲームの履歴にencounter IDがなく集計例外となるケースがあった。これらの失敗をMODの成功試験に数えず、通常マップから入るSilentの死亡でGame Overと集計を改めて確認した。

## 対象版の保存・通信契約

原DLLの型ごとの読み取り調査で確認した規則。原ソースやユーザーの保存内容は公開していない。

- `ModManager.IsRunningModded` はLoaded/FailedのMODがあればtrue。`affects_gameplay=false` でもMOD共通の `modded/profileN` へ保存先が分かれる。
- `ProgressSaveManager.LoadProgress` はその領域と同じパスのbackupを読み、なければ新規進行を作る。現在のバニラプロフィールを自動複製しない。既存の古いディレクトリ形式の移行は別の処理。
- 進行・解放・統計は現在の保存領域から取得する。`settings.save` と `profile.save` はアカウント階層で共通。installerは保存を複製・統合しない。
- `JoinFlow` は版、ゲームプレイMOD一覧、Model ID hashを照合する。非ゲームプレイMODの差は警告して継続する。この申告だけを実際の協力プレイ互換性の証拠にしない。

根拠: 同版の `UserDataPathProvider`、`ProgressSaveManager`、`AccountScopeUserDataMigrator`、`ProfileAccountScopeMigrator`、`JoinFlow`、`ModelIdSerializationCache`。原DLLのSHAは [版のpin](../../tools/pck_mod/game-version.json) と一致。担当は `save_contract`、GPT-6.1 sol / max / default指定の読み取り専用調査。

Native保存からのIronclad戦闘・Silent開始イベントの再開も確認した。全キャラ・全保存地点・協力プレイの再開を網羅した試験ではない。バニラ保存へ戻るにはゲーム内MOD管理で**全MODを無効化して再起動**する。このMODの `Enabled:false` は外観設定なので、それだけでは保存先が変わらない。

## 自動検証と通常QAの境界

- PythonのPCK生成・所有install検査17件と旧build検査10件が成功。未知のファイル・他MODの保護、設定無効・破損時の元path override省略を含む。
- placeholder除外とVFX倍率の修正後、標準Godotのanimation 126件、selection 42件、技術fixtureのPCK export/readbackが成功。loop、速度、seek、割込み、未知animation、元meshとVFXの復元を合成fixtureで検査した。
- native resource helper 204件は#33時点の資源接続試験。武器の剛体mesh 5114件は#37の形状試験。いずれも異なる段階の検証であり、全件を候補05の実カード試験として合算しない。
- 実機では元表示との切替を比較した。他の外観MODを導入した競合試験は未実施。同じresource pathを差し替えるMODとの併用を保証せず、衝突する外観MODを同時に有効にしない。

## 限界

協力プレイの実動作・再接続・真の死亡後復帰は未確認。別の検証用プロセスで内蔵マルチテスト画面を試したが、その `_Ready` が通常起動の `--force-steam=off` とは別にSteam初期化を行うことが分かった。appIDなしで初期化が失敗した段階で中止し、Steamの実アカウントやCloudを有効化しなかった。混在許容の静的契約を、実プレイ成功として記録しない。

実機表示はCompatibility rendererで確認した。元のparticle sub-emitter非対応警告があり、全描画backend・全カード・全act・全外観MODとの併用を保証するものではない。元Spine内部のscene終了時disconnectログも観測したため、「実行時の全ログが無警告」とはしていない。

候補05ではメニューへ戻ってharnessの `SceneTree.quit` で終了した際、RID・shader・textureの解放漏れを示す終了ログも記録した。通常のゲーム終了経路とharness終了経路、元ゲームとMODの寄与は未切分け。実行中のGDScript parse/runtimeエラーとは区別し、ログ原本とhashをローカルに保持する。

Defectの通常被弾は追加未確認（最初の敵行動がdebuffのみ）。実音声の収録比較、event回数・ダメージ時刻・待ち時間の全カード計測、実ゲームの全速度設定・割込みの組合せ、全act通しプレイも未確認。元driver・ゲーム処理を維持する設計と、確認できたカード操作を区別する。

簡易測定では、Silentの同じ戦闘でカスタム表示と元mesh復元の双方が約3.01秒で181処理frameだった。描画切替後も両方の資源はcacheに残り、厳密なメモリ比較ではない。MegaDotの `TIME_PROCESS` 値は実測frame数と整合しなかったので、CPU時間の比較結果としては使わない。

通常のビルド・renderer・mesh・PCKの検証と、上の実プレイ範囲を分けて参照する。新版のゲームではpinを書き換えるだけで使わず、scene・型・動作の契約を確認し直す。


## 納品と元環境の保全

候補05を `dist/PopSpireWomen-0.1.0-local/` へ固定し、次のZIPを作成した。ZIPと生成PCKはGitへ含めない。SHA-256は `tests/runtime/validation.json` に記録する。

| 成果物 | 内容と確認 |
| --- | --- |
| `dist/PopSpireWomen-0.1.0-source.zip` | 自作素材・生成器・root README・利用案内・設定例の129ファイル。ゲームPCK/DLL/ctex/互換sceneとQA操作ツールは含まない。全入力hashを照合し、ZIPを独立した場所へ展開して再bundleした内容も一致 |
| `dist/PopSpireWomen-0.1.0-local.zip` | 個人用のPCK・manifest・LOCAL_ONLY通知の３ファイル。再配布不可 |

QAプロセスの終了と、他のゲームプロセスがないことを確認してから、installerで元ゲームの `mods/PopSpireWomen` だけを作成した。所有receiptは `psw-install.receipt`。導入後もexe・原PCK・sts2.dll・release_infoは固定hashに一致。元プロフィールも400ファイルすべてのサイズ・SHA-256が一致し、変更・追加・欠損は **0**。元ゲームは起動せず、mod同意・ゲーム設定・セキュリティ・進行は変更していない。利用者がゲーム内MOD管理で有効にする準備まで完了した。

削除はゲーム終了後に `python3 scripts/build_pck_mod.py uninstall --mods-dir '/path/to/owned/game/mods'`。installerの所有receiptと全ファイルが一致するフォルダーだけを削除する。Workshopやreleaseへの公開は行っていない。
