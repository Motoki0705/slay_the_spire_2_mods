# Pop Spire Women — source bundle v0.2.0

プレイアブル５人の擬人化・女性化と、H3 / 768Pを基にした５選択ループ動画、戦闘・商人・休憩の15姿勢とGodotの動きを収録しています。

必要なものは所有Windows版Slay the Spire 2 **v0.107.1 / 59260271**、Python **3.11以降**、標準Godot **4.5.1 stable**。Spine Professional・追加DLLは使いません。動画は同梱済みで、利用者にAPIキー・動画生成API・H3契約は不要です。

このZIPを展開した場所で、次を実行します。パスは実環境へ置き換えてください。Windowsでは `python3` を `python` とし、Godotのexeを指定できます。

```bash
python3 scripts/build_pck_mod.py build --game-dir '/path/to/game' --godot '/path/to/godot' --output '/path/to/new-local-build'
python3 scripts/build_pck_mod.py verify --game-dir '/path/to/game' --build-dir '/path/to/new-local-build'
# ゲームを終了してから導入
python3 scripts/build_pck_mod.py install --game-dir '/path/to/game' --build-dir '/path/to/new-local-build' --mods-dir '/path/to/game/mods'
# 削除する場合もゲームを終了
python3 scripts/build_pck_mod.py uninstall --mods-dir '/path/to/game/mods'
```

生成結果の `build-receipt.json` で `skipped` が空であることを確認し、ゲーム内のMOD設定で有効にして再起動します。通常のbuildだけではゲームへ導入されません。

既定で５人全員が有効です。選択を静止posterへ切り替えるReducedMotion・一部の無効化は [設定例](mod/settings.example.json) を編集し、buildへ `--settings /path/to/settings.json` を渡して、再生成・再導入・再起動します。

この版では外観MODでもMOD共通の別保存領域を使い、通常の進行は自動移行されません。詳しくは[保存の扱い](mod/README.md#保存と協力プレイについて)を確認してください。

**このsource bundleは公開用、生成したPCKは個人のローカル利用用です。** PCKには所有ゲームのsceneを基に生成した互換データが入るため、完成PCKを再配布しないでください。ゲーム更新後は旧MODを無効化/削除し、対応確認後に再生成します。

[同梱の詳しい生成手順](docs/development/pck-only.md) / [MODの利用案内](mod/README.md) / [最新の制作・検証状況](https://github.com/Motoki0705/slay_the_spire_2_mods)
