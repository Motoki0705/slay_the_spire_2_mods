# v0.2 実ゲーム確認（Issue #62）

Windows **v0.107.1 / build 59260271 / MegaDot 4.5.1-m.12**、Compatibility rendererで確認した。追加DLLを使わず、所有ゲームの隔離コピーから原main sceneを起動し、内蔵ModManagerでPCKをロードした。validatorは指定・試行・完了とも **0回**。これは制作と通常QA。

版・入力hash・確認区分は [validation.json](../../tests/runtime/v02/validation.json)、状態遷移は [sanitized observations](../../tests/runtime/v02/observations.json)。外観と実録の入口は [README](../../README.md)。H3生成物自体と、ゲームのviewportで同梱動画を再生した実録を区別する。

## 対象と候補の違い

基準commitは `27611c3c388ebf79b24f271f963c885f92774979`。全20rigと５本の選択OGVを含む候補01は、PCK SHA-256 `14005c126351190fa6e38c49e323e8c0398fa12dfe1743673226afddc4cbcb98`。20surfaceのpreflight、５動画の空host decode/readback、全364資源のbyte/hash照合が成功し、`skipped=[]`。

候補01で全５人の選択・代表カード・商人・休憩を確認した。Regentの休憩だけは、背後に旧星形キャラの影が残ったため `preserve_slots` の `shadow` を外した。本人・座席・休憩選択を保持し、戦闘／商人の床影は変更しない。画像・動画・mesh・関節・元イベントは変更していない。最終候補02のPCK SHA-256は `1213c359dc6bee5a129d2f825e876b6ec16a1e8841c4e492c6bfceabbc1b6d94`。再起動した元mainで旧影が消えたことと休憩選択→次への操作を確認した。候補01の他場面は内容hashが一致する範囲で証拠を引き継ぎ、全試験を最終PCKで再実施したとは扱わない。

## 選択画面

全５人をUIで切り替え、`state=video`、動画の進行、人物puppetなし、頭・足・武器のviewport内への収まりと左情報欄の余白を確認。各10秒、1280×720相当・約10fpsの実viewportを収録した。184frame / 約7.6667秒の同梱ループを越えて再生が続く。`capture.json` の実測時刻（`actualtime_ms` / `time_ms`）を保持し、nominal fpsを実測と称さない。

Regentの７中心へ実マウス入力を送り、各星座の発光・離脱を目視。動画と独立したoverlayが動き、キャラ切替と出発入力も通る。SilentではQA専用のruntime設定操作により、reduced motion → poster、disabled → original、missing video → poster、各状態からvideoへの復帰を確認した。退出時にvisibleな動画presenterがなくなり、再入場でvideoに戻ることも確認。最終候補では全５人×６遷移（reduced / enabled / disabled / enabled / missing / restore）を実機で確認し、30遷移すべて期待するstateへ戻った。

設定変更の実運用はPCKを **再build → 再install → 再起動** する。QAの一時的なruntime操作を、利用者向けのhot reload機能として案内しない。破損codec、pause/resume、posterも欠損した静止rig／元aliasへの分岐の網羅は既存Godot fixtureの範囲であり、今回の実ゲーム全件確認と混同しない。

## 代表操作と場面別姿勢

各キャラともNeowをUIで完了し、マップ表示後に元ゲームの `room` コマンドで検証用の戦闘・商人・休憩へ移動した。必要なカードとエネルギーは検証用進行へ元consoleで追加し、カードは実際の手札からドラッグして使用した。全actの通常進行を通した試験ではない。

| キャラ | 実カード操作と確認 | 被弾の区分 | 商人・休憩と接点 |
| --- | --- | --- | --- |
| Ironclad | Strike / Demon Form、attack / cast。敵HP 44→38 | 元consoleで本人へ3 damage、80→77、hurt | 長剣の柄・刃先の支持点と剛体形状、座位の臀部と足を目視 |
| Silent | Strike / Deadly Poison / Shiv、attack / cast。敵HP 55→45 | 元consoleで本人へ3 damage、70→67、hurt | 商人の手の仕草、休憩の膝を立てた座位、短剣の形を目視 |
| Regent | Strike / Venerate / Sovereign Blade、attack / cast / attack_sovereign。別武器の出現と攻撃 | 元consoleで本人へ3 damage、75→72、hurt | 右向きcombatと独立登録した玉座、merchantの別姿勢、rest本人だけの座位 |
| Necrobinder | Strike / Bodyguard / Unleash、attack / cast。Osty 1→6 HPと独立攻撃、敵HP 35→17 | 元consoleで本人へ3 damage、66→63、hurt | ３場面の新髪上端に頭の炎、鎌の握りとVFX位置。Ostyは休憩でも独立 |
| Defect | Strike / Zap / Dualcast、attack / cast。Orb 1→2→1、解放 | **通常の敵ターンの攻撃**で75→71、hurt | 敵向きの構え、商人の品物を見る手、工具を扱う座位、独立Orb |

全15場面でoverlayがactiveとなり、combat / merchant / restそれぞれ異なるbody textureと `contextual_v02` profileを使用する。休憩はAct 1の `overgrowth_loop` を確認した。５人の座席位置・足・衣服の収まりを目視し、初期display heightを採用した。全Actの座席構成を確認したわけではない。

IroncladとNecrobinderの `NCreature.StartDeathAnim` / `StartReviveAnim` は、HPを変えない**描画だけの試験**。剣の形状、Necrobinderの頭の炎の非表示／復帰を確認するためのもの。実死亡・co-op復活の成功証拠にはしない。通常死亡→結果画面は旧v0.1の記録であり、今回再確認したとは書かない。

## 収録と通常検証

QAハーネスは期待する専用userdirの完全一致と `--force-steam=off` を開始前に必須とする。最大収録時間を8秒から12秒へ延長した。１度capture metadataの読取りが公開前に競合したため、JSONをcloseしてからrenameで公開するように修正。最終候補の４秒実録で、この公開済みmetadataを即時に読み取れることも確認した。収録物は旧v0.1の出力を上書きせず、`results-motion-v02` とprivate `/tmp/sts2-motion-v02/native-qa` へ保存した。

候補02の初回ビルドはprocess終了143、再試行は180秒のimport上限で停止し、部分PCKは公開されなかった。import上限を600秒へ延ばし、timeout時のpartial stdoutを外側のコマンドlogにも残すよう修正した。次の同入力ビルドは約97秒で成功した。

今回の修正に対応するcompiler **4件**、PCK builder **19件**、import timeoutの診断保持 **1件**が成功。QA GDScriptのGodot 4.5.1 parse確認も成功。PCKのpreflight/readbackと元mainの操作は今回の実施。既存のGodot315項目、Python23件、15rig／90動作×51位相、lease等の成功記録は依存側の通常検証であり、理由なく全反復していない。

## 保全・納品と未確認

新しい専用userdir `PopSpireWomenQA_MotionV02_20261009` を使用した。入力はv0.1の**偽の検証用進行**だけで、元 `SlayTheSpire2` の進行をコピーしていない。着手時の元プロフィールは新たに一覧・サイズ・SHA-256を採取した400ファイル。前回の400件を流用していない。導入後も400ファイルで、追加・削除・サイズ／hash変更はすべて0件。原gameの４つのpinも最終再照合で一致した。元プロフィール・raw log・元ゲームコードは公開物に含めない。

利用者は同梱動画をローカル再生するためAPIキーやH3契約が不要。公開source ZIP（167ファイル）と、所有ゲーム由来の互換sceneを含む再配布禁止local PCK／ZIPを分離した。source ZIPの全file hash・最終PCK入力との一致、およびPCK／DLL／ctex／互換scene／QA進行の非同梱を確認。local ZIPはPCK・manifest・LOCAL_ONLY通知の３ファイルのみ。ゲーム全プロセスの終了を確認し、所有receiptを検証して既存0.1.0を0.2.0へ更新した。導入後のreceiptと実ファイルhashも一致し、元ディレクトリでゲームを起動していない。設定と保存領域は [MOD利用案内](../../mod/README.md)、生成・導入・削除は [PCK手順](../development/pck-only.md) を参照。通常進行はMOD共通の保存領域へ自動移行されない。

Compatibility rendererはparticle sub-emitter / trailの非対応警告を出す。終了時にはRID・texture・ObjectDB・使用中resourceの解放ログが残り、原因を今回切り分けていない。無警告・リークなし・全VFX同等とはしない。厳密な性能、他renderer／他MOD、全カード・速度・Act通しは [#46](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/46)、実co-op復活・再接続は [#45](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/45) に残す。

## 納品ファイル

| ファイル | SHA-256 |
| --- | --- |
| `dist/PopSpireWomen-0.2.0-source.zip`（公開可） | `bca21dc06ced40655ca0772c07da01026d5af58b02df7f9af447ce9308e85c8d` |
| `dist/PopSpireWomen-0.2.0-local.zip`（再配布不可） | `22e43d68c4dab00e247e8f5a2c5ea3f9ab24f3f1abe7c84e10638293a157f3da` |
| `dist/PopSpireWomen-0.2.0-local/PopSpireWomen/PopSpireWomen.pck` | `1213c359dc6bee5a129d2f825e876b6ec16a1e8841c4e492c6bfceabbc1b6d94` |

ZIPとローカルbuildはGitに含めない。画像・実録と候補間の差分はprivate `/tmp/sts2-motion-v02/readme-handoff.json` でREADME担当へ引き継いだ。root README・公開媒体の選定／変換は別担当の所有範囲。
