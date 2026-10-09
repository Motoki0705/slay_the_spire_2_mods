# DLL不要のPCK接続・配布 (#33)

対象は所有Windows版 **v0.107.1 / 59260271**、ゲーム内エンジン **MegaDot 4.5.1-m.12**。通常Godot **4.5.1 stable** とPython **3.11以降**で自作PNGをimportし、ローカル互換PCKを生成する。Spine Editor、動画AI、RitsuLib、Harmony、自作/第三者DLLは使わない。

この経路の入口は `scripts/build_pck_mod.py`。旧 `scripts/build_mod.py` のbuild/exportは停止し、旧C#実装と検証は履歴・参考として残す。manifestは `has_dll=false / has_pck=true / dependencies=[] / affects_gameplay=false`。name/description/versionは入力manifestを保持する。

## 自作素材の公開とローカル生成の境界

| 成果物 | 内容 | 扱い |
| --- | --- | --- |
| source bundle ZIP | 自作画像・rig・scene・GDScript・Python生成器・hash pin・本手順 | 公開配布用。ゲームから読んだ資源、原DLL、生成済compat、原UID cache、project設定を含めない |
| local build directory | `PopSpireWomen/PopSpireWomen.pck` とmanifest、`LOCAL_ONLY.txt`、receipt/検証ログ | 所有ゲームから生成。**元scene scaffoldを含むため再配布しない** |
| installed mod directory | 上記PCK/manifest/noticeと所有receiptだけ | 明示install。元PCK/exe/DLL・ユーザー進行・他MODを変更しない |

原作のSpine skeleton/atlas/texture/DLLは抽出・格納しない。必要な15sceneの小さいテキストscaffoldと5選択scene aliasだけをローカル生成する。外部リソースは元ゲームの `res://` を参照する。UIの元 `.import` 25件はパス/UIDを読む入力で、元textureのバイトは取り込まない。書き込む `.ctex` は標準Godotでimportした自作PNGのみ。

`bundle` はゲームを入力に取らない。`build` はローカル出力、`install` は明示先のmods配下、`uninstall` は所有receiptが完全一致するMODディレクトリだけを扱う。未知のファイル・編集済みファイル・symlink・既存の未管理MODは拒否する。所有receiptは `psw-install.receipt` とし、ゲームがmods内の全 `.json` をmanifestとして走査する処理へ混入させない。通常buildでSteamへcopyしない。DLLのある旧配布フォルダを自動採用/削除しない。

## 入力とコマンド

`--assets` は `mod/assets` に相当するディレクトリ。次のパスが `res://` に対応する。親のproduction素材を別worktreeから読み取り専用で指定できる。ビルドは一時stageへsnapshotし、入力は編集しない。接続用の共通 `driver_overlay.gd` / `select_background.gd` / `config/*.gd` は、生成器と同じ版の同梱runtimeを使う。

```text
PopSpireWomen/rigs/<id>/{combat,merchant,rest,select}.json
PopSpireWomen/select/production/<id>.tscn
PopSpireWomen/ui/<id>/{top,outline,portrait,locked,map}.png
PopSpireWomen/ui/<id>/icon.tscn
PopSpireWomen/art/...                # 自作画像と分割層
PopSpireWomen/animation/...          # free-animationの既存renderer
PopSpireWomen/select/...             # Regent 7 hoverも維持
```

idは `ironclad / silent / regent / necrobinder / defect`。rigは [free-animation.md](free-animation.md) のschema 1。production selectionは `character_entry` と対応する `rigs/<id>/select.json` を指定したControl。iconはscript/子nodeを持たないTextureRect。UI寸法はtop/outline=85×85、portrait/locked=132×195、map=49×64。

Linux/WSLの例（WindowsでもPythonと通常Godot 4.5.1のパスを指定する）:

```bash
# 配布者: 素材が揃ったsource bundleを作る。outputは未使用パス。
python3 scripts/build_pck_mod.py bundle \
  --assets mod/assets --manifest mod/PopSpireWomen.json \
  --output /tmp/PopSpireWomen-source.zip

# 利用者: ZIPを展開したルートで、所有ゲームからローカルPCKを生成。
python3 scripts/build_pck_mod.py build \
  --game-dir '/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2' \
  --godot /path/to/Godot_v4.5.1-stable_linux.x86_64 \
  --output /tmp/psw-local-build

python3 scripts/build_pck_mod.py verify \
  --game-dir '/path/to/owned/game' --build-dir /tmp/psw-local-build

# ゲーム終了後、実際に導入するmodsディレクトリを明示する。
python3 scripts/build_pck_mod.py install \
  --game-dir '/path/to/owned/game' --build-dir /tmp/psw-local-build \
  --mods-dir '/path/to/owned/game/mods'

python3 scripts/build_pck_mod.py uninstall --mods-dir '/path/to/owned/game/mods'
```

ゲームの既存MOD管理画面で有効化し、再起動する。既存のmod許可設定を生成器が変更することはない。`--mods-dir` は既存ディレクトリ、または既存の親直下に作る新しいmodsディレクトリを指定する。旧Ritsu依存MODが残る場合は、その旧MODの手順で停止/退避する。このinstallerは他MODを変更しない。

## 設定とfallback

設定ファイルを省略すると５人全員有効。`build --settings /path/to/settings.json` で下記を指定できる。fieldの省略も下記の値を既定とする。

```json
{
  "SchemaVersion": 1,
  "Enabled": true,
  "EnabledCharacters": ["IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT"],
  "ReducedMotion": false
}
```

`Enabled:false`、対象を含まない `EnabledCharacters` では、そのキャラの**元pathのoverrideを一切生成しない**。JSON破損・型不一致・未知field/ID・異なるschemaでは警告を出し全無効として生成する。設定はPCKへ封入するため、変更には **再build → 再install → ゲーム再起動** が必要。user://や原ゲームの設定ファイルを作らない。

Godot preflightは20rigのschema/texture/canvasと５選択descriptor、25UI textureの型/寸法、５iconの構造を検査する。欠損/不正なsurfaceは対応overrideを省略し、元表示を残す。共通scriptのparseエラーやpin不一致ではbuildを失敗させる。receiptの `skipped` が空かを必ず確認する。欠損があるbuildを「５人完成」と扱わない。

実行時もoverlayが設定無効・rig欠損・未対応animation・mesh対応不明・VFX binding不備を検出したら、元mesh visibility/位置へ戻す。選択は自作poster、またはローカル生成した `res://PopSpireWomen/compat/original_select/<id>.tscn` へ戻る。aliasは**元sceneのroot UIDを除去**し、外部の元資源参照は保つ。PCK markerがある場合、alias欠損で `res://scenes/screens/char_select/...` を再ロードしない。このpathは自分のrouterに置換済みなので、再帰になるためである。原aliasそのものの物理破損や他MODとの競合を無条件に復旧できるとはしない。

## 接続とcache

戦闘 `scenes/creature_visuals/<id>.tscn`、商人 `scenes/merchant/characters/<id>_merchant.tscn`、休憩 `scenes/rest_site/characters/<id>_rest_site.tscn` をローカル変換する。元headerのload_stepsと新しい外部overlay参照を追加し、**末尾child**としてoverlayを追加する。元C# script、node順、子0、Bounds/CenterPos/IntentPos、rest controls、Spine resource参照を変更しない。

driverはcombat=`Visuals`、merchant=`SpineSprite`、restはRegent=`SpineSprite2` / Necrobinder=`Necro` / その他=`SpineSprite`。元のOsty、Regent `Weapons/WeaponAnim1/2`、Orb制御を残す。driver_overlayが直下SpineMesh2Dだけを抑止し、元SpineSpriteのvisibility/process/animationを変更しない。元driver/event/音/待ちの設計契約はfree-animationに従う。C#の３postfixは配布物から外れ、sceneの末尾child接続が代わりになる。

対象DLLの静的確認では `NCreatureVisuals._Ready` は既存の名前付きnodeを取得し、`NMerchantCharacter._Ready/PlayAnimation` は子0を取得する。`NRestSiteCharacter` の子列挙はclass名が `SpineSprite` のnodeだけを返す。PCK接続ではoverlayが親の `_Ready` 前から存在するため、この差も確認した。overlay自身の開始はdeferredのままにする。

UIは元PNG pathの `.import` を自作 `.ctex` に向け直し、元UIDを保持する。元importのfeature別 `path.bptc` 等を含むすべての元 `.ctex` pathにも自作ctexを置く。PNGを同名で置くだけの置換ではない。Select/Locked/Mapを含め、元pathと元UIDから **CompressedTexture2D** が返ることをnative helperで検査した。

既にロード済みの資源はGodot cacheに残るためhot reloadには対応しない。既存インスタンスを強制置換するコードは入れない。native helperで「mount前にロードしたtextureはcacheから元のまま返る」「新規読込みでは自作pixelsになる」を確認する。元ゲームの通常起動時のpreload順と他MODとの競合は親の実機QAで確認する。[Godotのpack仕様](https://docs.godotengine.org/en/4.5/tutorials/export/exporting_pcks.html)と[ResourceLoader cache仕様](https://docs.godotengine.org/en/4.5/classes/class_resourceloader.html)も参照。

## 対象版・更新・削除

`tools/pck_mod/game-version.json` にrelease_info、元exe、元PCK全体、sts2.dllのSHA-256を固定した。生成時とinstall/verify時に照合する。選択した45資源はPCK indexのMD5と個別SHA-256もreceiptへ記録し、出力PCKの全288資源を読戻してhash照合する（候補05のproduction入力での個数）。原本はread-onlyで開く。

ゲーム更新後は古いPCKを無効化/削除する。installerは版不一致を拒否するが、ゲーム起動前に常駐して自動検出する機能はない。ローカルscaffoldは元版のnode/型に依存するため、pinだけを書換えて継続しない。新しい版のC#/scene/UID/importを再調査し、適合した生成器で再buildする。uninstallは更新後も原gameを参照せず所有receiptだけで削除できる。削除後に再起動すると元PCKの表示へ戻る。

Windows App Control、Defender、許可ポリシー、証明書信頼、ADSを変更する操作は生成器/installerに含まない。ブロックされたDLLを別名/信頼path/メモリロードで動かさない。

## 通常検証と未確認

```bash
python3 -m unittest discover -s tests/pck_mod -p 'test_*.py' -v
python3 -m unittest discover -s tests/build -p 'test_*.py' -v
python3 tests/animation/run_checks.py --godot /path/to/Godot4.5.1 --output /tmp/psw-animation-checks
```

native用 `tests/pck_mod/native_probe.gd` は原mainを起動しないSceneTree helper。独立コピーの元game exe/PCK/DLLだけを使い、コピー側override.cfgで `config/use_custom_user_dir=true` とtask専用 `config/custom_user_dir_name` を設定する。`--force-steam=off` と別 `--log-file` を必ず付ける。`--` 後へ渡すJSONは `pck`（生成物）、`output`（レポート）、`user_dir`（期待するuser://実値）の絶対path。実値一致とtask固有名を確認できなければ資源検証を始めない。exeを直接起動し、セキュリティ設定の変更を伴うlauncherを使わない。

上記テストコマンドは開発repository用（public bundleにはテストsuiteを同梱しない）。資源検証の記録はrepositoryの `tests/pck_mod/validation.json`、その後の元main・実カード操作・商人・休憩・導入の結果はrepositoryの [実ゲームQA](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/main/docs/validation/runtime-v01.md)。native helperは元C#付き15sceneをtree外でinstantiateして型/子nodeを確認する。driver検査では元SpineSkeletonDataResourceを独立した素のSpineSpriteで動かす。**このhelper成功だけを、実戦の攻撃event/音/死亡待ち、Orb数・剣・Osty、入力全体、マルチプレイの成功とは扱わない。** validatorは指定・試行・完了とも0回。
