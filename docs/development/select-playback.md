# 選択背景の動画・poster・PCK

[Issue #8](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/8)、担当 `engine-select`。
基準commit `e21f02c7e021e2d7ba803cb1885842c8489e4a54`。対象は **v0.107.1 / 59260271 / Godot 4.5.1**。

**背景だけを入れ替えるruntimeとPCK工程を実装し、standalone Godotで合成動画を実再生した。ゲームへの導入・起動はしていない。**
承認済みの画像・動画は０件で、[ApprovedSkinCatalog](../../mod/code/Routing/SkinDefinition.cs)は引き続き空。
５人分のsceneは接続用の空の定義であり、完成した女性化素材ではない。生成AI APIは呼んでいない。

## 接続と所有範囲

[方式比較](../research/implementation/options.md#選択背景の動画仕様と生命周期)と[動作一覧](../research/motion/inventory.md#１-キャラ選択と画面の小さい動き)を設計入力にした。
既存のC# loader/RitsuLib接点を保ち、描画はGDScriptにした。C# Node script、source generator、ゲームDLL配布を増やさず、同じ描画コードを標準Godotで実行検証できる。

```text
内蔵loader → Bootstrap.Initialize
  → SkinSettings / 対象版 / 承認済みcatalog / sceneのExists + Load + CanInstantiate
  → RitsuSkinRegistrar → CharacterAssetReplacement(既存ID)
  → CharacterUiAssetSet(CharacterSelectBgPath: MODのscene)
  → ゲームのAnimatedBg内へ選択背景だけをInstantiate
```

既存IDは `IRONCLAD / SILENT / REGENT / NECROBINDER / DEFECT`。
背景sceneは `res://PopSpireWomen/select/{小文字ID}.tscn`。選択用の登録ではCombatScene等をnullに保つ。
UI、入力、アンロック、ロビー、出発操作、選択SE/BGMの処理はゲームが所有する。
登録の実装とコンパイルは確認済みだが、Ritsuのdeferred登録とゲームのPreloadManagerからの実呼出しは未確認。

catalogが空の現版は、５人を設定で有効にしても登録・資源検査の呼出しが０になる。
後続の承認時には、sceneに承認済みposter/video pathを設定し、既存IDの `SelectScene` のみをcatalogへ追加する。
sceneの存在確認だけで承認flagを立てない。Regentは後述のhoverを完成してから有効化する。

## 描画と寿命

実装: [select_background.gd](../../mod/assets/PopSpireWomen/select/select_background.gd)、[scene](../../mod/assets/PopSpireWomen/select/select_background.tscn)、[video_loads.gd](../../mod/assets/PopSpireWomen/select/video_loads.gd)。

| 状態・操作 | 実装した動作 |
| --- | --- |
| 入場 | 小さいposterをロードして表示し、動画をthreaded request。再生位置が進み、有効な映像textureを得てからvideoへ切替 |
| ループ | `VideoStreamPlayer.loop=true` のみ。Finishedに接続せず、周回待ちや手動再開をしない |
| 切替・離脱 | 世代を進め、読み込み先から自分を取り消し、`stop()`と`stream=null`。poster・overlay・原背景の参照も解放 |
| A→B→A | sceneごとの世代とweak reference。旧結果が別sceneや新しい設定を更新できない |
| 再入場 | 新規sceneだけでなく、Ready済みの同じnodeをRemove/Addしても再開 |
| 自分/親が非表示 | decoderを停止・解放。表示に戻ると先頭から開始。非表示のままdecodeさせない |
| reduced motion | poster表示、動画要求なし。動的 `set_preferences(true, true)` でもstreamを解放 |
| 無効化 | 元の固定scene pathへ戻る。Ritsuのgetterを再帰的に呼ばない |
| 動画欠損・load/decode失敗 | posterを保持。３秒間進行しないdecodeもposterへ戻し、同じ警告の連打を抑える |
| poster欠損・誤った型 | 動画を開始せず元の背景を生成。standaloneに元sceneがない場合はunavailableを報告 |
| アプリ終了 | tree所有のloaderが未回収requestを `load_threaded_get` で回収。背景の退出では待たない |

`ResourceLoader`のthreaded requestには取消APIがないため、画面から消えたclientを保持せず、専用loader１個が完了結果を回収して捨てる。
通常はLOADED/FAILEDをポーリングしてからgetし、メインスレッドを待たせない。**アプリ全体のtree終了時だけは未完了の資源I/Oを待つ可能性がある**。動画の再生尺・Finished・ゲーム出発操作をawaitする処理はない。

posterと元sceneのロード、decoderの生成自体はメインスレッド上で行う。小さいfixtureでの成功を本番の高解像度映像の無停止・低負荷の保証にはしない。

描画は親の大きさを使い、posterはKEEP_ASPECT_COVERED、videoも同じ中央cropで比率を保持する。
元のAnimatedBgは16:9固定ではないため、本番素材の顔や手のsafe area・crop位置は実機確認が必要。
Video/Poster/rootはMouseFilter=Ignoreで、背景は入力イベントを処理しない。音は二重化しないよう、配布工程で**音声trackを含む.ogvを拒否**し、playerもvolume=0にする。

Godot 4.5の一次資料: [VideoStreamPlayer](https://docs.godotengine.org/en/4.5/classes/class_videostreamplayer.html)、[ResourceLoader](https://docs.godotengine.org/en/4.5/classes/class_resourceloader.html)、[PCK export](https://docs.godotengine.org/en/4.5/tutorials/export/exporting_pcks.html)。
固定4.5.1で実行した検証結果と、仕様説明を区別する。

## 設定とoverlay

`user://PopSpireWomen/settings.json` の例:

```json
{"SchemaVersion":1,"Enabled":false,"EnabledCharacters":[],"ReducedMotion":false}
```

C#は起動時に設定を検査し、メモリ上のProjectSettingsの `PopSpireWomen/select/enabled` / `reduced_motion` へ渡す。背景はReady時に読む。
設定ファイルの監視・書込み・設定UIは追加していない。ファイル変更は再起動時に反映する。
runtimeの `set_preferences(enabled, reduced_motion)` は将来のUI接続用で、今回のテストでも状態遷移に使用した。

`Overlay`はvideoの上の独立Control。`overlay_scene_path` にMOD固有のsceneを設定できる。
子sceneが `set_presentation_state(active, reduced_motion)` を持てば、入場・設定変更・退出時に通知する。
rootの `presentation_changed` signalも公開している。canvasはIgnore、hoverが必要な局所ControlだけPASS等へ明示変更する。
テストは動画とは別の小さいhover領域が反応し、同時に出発ボタンが動くことを実入力で確認した。

**Regentの７つの星座hoverは未実装。** 原作は `NRegentCharacterSelectBg` がSpineのskinを切り替えるため、元の全画面sceneを動画の上に置くだけでは独立overlayにならない。
７領域と対応する星座の絵・位置・非hover時の復帰を別sceneへ移す作業が必要。今回は接点とsynthetic hoverだけを評価した。
空catalogによって原作のRegentは変更されない。hoverを動画へ焼き込んだ代替素材も作っていない。

## PCKを含むビルド

[C#基盤の手順](build.md)に対する追加工程。旧文書の「PCKなし」は既定の素材なしモードについて引き続き正しい。
`--with-pck` を指定した場合だけ、この手順を使う。Godotの.NET版やexport templateは不要。

公式標準editor **4.5.1.stable.official.f62fdbde1** を使用。今回の取得先は [Godot 4.5.1 release](https://github.com/godotengine/godot/releases/tag/4.5.1-stable) の
`Godot_v4.5.1-stable_linux.x86_64.zip`。同releaseの `SHA512-SUMS.txt` と照合して `/tmp/sts2-tools/issue-8/` に展開した。
ゲームフォルダやシステムへインストールしていない。

```bash
python3 scripts/build_mod.py export --with-pck \
  --dotnet /tmp/sts2-tools/issue-7/dotnet/dotnet \
  --godot /tmp/sts2-tools/issue-8/Godot_v4.5.1-stable_linux.x86_64 \
  --game-dir '/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2'
```

1. 固定hashのゲームDLLを参照してC#をビルド。既存のlocked restoreを保つ。
2. `mod/assets/` だけをGodot projectとしてimport。C#、ゲームDLL、tests、レビュー画像のあるディレクトリはproject外。
3. .ogvがあればFFprobeでTheora１stream/音声なしを確認。
4. 公式 `--export-pack Resources` でPCKを作る。独自のPCK writerは使わない。
5. 元projectのない一時hostへPCKをmountし、５人のsceneをload/instantiate。parse errorはGodotがexit=0でもbuild失敗とする。
6. 成功後だけ `mod/build/PopSpireWomen.pck` を確定し、配布manifestの `has_pck=true` とともにZIPへ入れる。

配布物はDLL / JSON / README / 任意のPCKのallowlist。
ソースのmanifestは `has_pck=false` のままで、PCKを省略したexportでは３ファイル・falseへ戻る。古い自MODのPCKを次のDLLのみZIPへ混ぜない。
`build` も `--with-pck` を受け取る。`test` は従来どおりPython/C#だけで、描画検証は次節の別コマンド。

PCKの自作資源pathは `res://PopSpireWomen/` に限定し、scriptの新規UIDを管理する。Godot exporterが生成する `.godot/exported/`、cache、`project.binary` もPCKに含まれる。
ゲームと同名のsceneを上書きするpackやautoloadは作らない。別MODとのmount順・UID/cacheの実機共存は未確認。

receiptとimport/export/pack検査logは `mod/build/`、配布物は `dist/`（いずれもgit対象外）。
既定のDLLのみbuild/exportはGodot・FFmpegを必要とせず、ゲームへのcopy/導入工程もない。

## 再現する検証

Python 3.11+、固定.NET SDK、公式Godot 4.5.1、FFmpeg/FFprobe、Xvfb、`xvfb-run`とOpenGL software rendererが必要。

```bash
python3 scripts/build_mod.py test \
  --dotnet /tmp/sts2-tools/issue-7/dotnet/dotnet

python3 tests/select/run_checks.py \
  --godot /tmp/sts2-tools/issue-8/Godot_v4.5.1-stable_linux.x86_64 \
  --pck mod/build/PopSpireWomen.pck \
  --output /tmp/sts2-tools/issue-8/packed-checks
```

runnerは一時projectへproduction runtimeをコピーし、96×64/24fps/１秒の無音Theora２本と小さいposterをFFmpegで合成する。
原背景のstub・hover・出発ボタンも試験専用。**この一時projectを別の `technical-fixtures.pck` へexportし、元projectのないhostでそのPCKから実再生**する。
fixture、動画、画像、hash、stdout、画面capture、結果JSONは指定outputと一時ディレクトリだけに置き、本番catalogやPCKへ含めない。

2026-10-09の通常検証記録は [issue-8.json](../../mod/validation/issue-8.json)。

- C#実コンパイル: 警告０・エラー０。固定ゲームDLL参照、依存DLLを出力/配布しない。
- Python: 参照pin、配布allowlist、PCK有無/manifest、旧PCKの除外、欠損PCK、exit=0のGodot script error拒否。
- C#: 設定/reduced motion、既存５IDのselect-only登録、空catalog、資源欠損/例外、承認・版・pathの制限。
- Godot: デコード画素の変化、比率、ループの周回、Finished非発火、初回poster、reduced motion、非表示、無効化、A→B→A、再入場、破損/欠損/誤型/停止、旧世代無効化、scene解放、読み込み回収、tree終了。
- 入力: 独立hoverと別の出発ボタンへ実mouse eventを送り、動画再生中に動作することを確認。
- 配布gate: 実際のTheora+Vorbis fixtureを拒否。production PCKは別のheadless hostで５sceneをinstantiateし、test-fixturesがないことを確認。
- 画面captureはtest patternとoverlay/ボタンを目視確認。キャラデザインやゲーム画面の承認ではない。
- validatorは指定どおり０回。ゲーム導入・起動・生成AI API・動画購入は０回。

未確認: 内蔵loaderとRitsuLib完全配布物での実起動、実機UI/ロビー/アンロック、Regentの実星座hover、本番素材のsafe area・色・ループ継ぎ目・CPU/メモリ、Windowsのcodec再生、他MOD、save・マルチプレイ。
standalone試験の成功を、これらの成功や完成した女性化MODとは表現しない。
