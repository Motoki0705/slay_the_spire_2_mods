# Pop Spire Women — v0.1.0

Ironclad / Silent / Regent / Necrobinder / Defectの５人を、人の顔・髪・表情を持つ女性へ翻案する外観MOD。５人分の本体・選択背景・まばたき・休憩姿・UIとGodotの動きを収録している。元のキャラID・カード・能力を使い、相棒Osty、Sovereign Blade、Orbは元ゲームの独立制御を維持する設計。

**配布・導入の入口は [DLL不要のPCK生成・導入](../docs/development/pck-only.md)。** 自作・第三者DLL、RitsuLib、Harmony、Spine Professional、動画生成AIは必要ない。旧C#版のbuild/exportは停止している。

2026-10-09（JST）の対象は所有Windows x64版 **v0.107.1 / 59260271**。ゲーム内エンジンはMegaDot 4.5.1-m.12（Godot 4.5.1系）、.NET 9、Spine 4.2系。ローカル生成には **Python 3.11以降と通常Godot 4.5.1 stable** を使う。最新版や別ビルドへの対応は未確認で、生成器は元exe/PCK/DLL等の固定SHA-256と照合する。

## 配布物と導入物

| 成果物 | 用途 |
| --- | --- |
| 公開source bundle ZIP | 自作画像・rig・scene・GDScriptと生成器・版のpin・手順。ゲーム資源や完成PCKを含まない。利用者が展開して所有ゲームから生成する |
| ローカルbuild | `PopSpireWomen/PopSpireWomen.pck`、`PopSpireWomen.json`、`LOCAL_ONLY.txt`とbuild側のreceipt・検証ログ。元scene scaffoldを含むため**再配布しない** |
| インストール先 `mods/PopSpireWomen/` | PCK・manifest・notice・所有receipt `psw-install.receipt`。DLLや元ゲーム資源をコピーしない |

manifestは `has_dll=false / has_pck=true / dependencies=[]`。通常buildとinstallは別の操作で、buildだけではSteamのmodsへコピーしない。既存MODやユーザーの進行を変更しない。

## 生成・導入・削除

source bundleを展開したルート、またはrepositoryルートで実行する。以下はLinux/WSLの例。ゲーム・Godot・modsのパスを実際の場所に置き換える。Windowsで直接実行する場合も同じ引数を使い、PythonとGodotのWindows版パスを指定する。

```bash
# １. 所有ゲームからPCKを生成。outputは入力・ゲームと別の未使用パス。
python3 scripts/build_pck_mod.py build \
  --game-dir '/path/to/owned/game' \
  --godot /path/to/Godot_v4.5.1-stable_linux.x86_64 \
  --output /tmp/psw-local-build-v01

# ２. PCK・manifest・対象ゲームの一致を確認。
python3 scripts/build_pck_mod.py verify \
  --game-dir '/path/to/owned/game' --build-dir /tmp/psw-local-build-v01

# ３. ゲーム終了後、既存のmodsディレクトリへ明示導入。
python3 scripts/build_pck_mod.py install \
  --game-dir '/path/to/owned/game' --build-dir /tmp/psw-local-build-v01 \
  --mods-dir '/path/to/owned/game/mods'

# 削除もゲーム終了後に実行。
python3 scripts/build_pck_mod.py uninstall --mods-dir '/path/to/owned/game/mods'
```

導入後はゲームの既存MOD管理画面で有効化し、再起動する。build出力の `build-receipt.json` にある `skipped` が空であることを確認する。欠損・不正なsurfaceは元表示を残すため、生成成功だけで５人分が全て有効とは判断できない。

installerは所有receiptと内容hashを確認し、未知・編集済みファイル、symlink、未管理の同名フォルダを拒否する。旧DLL版が同じ場所にある場合は、旧版の手順で停止・退避してから導入する。receiptを削除・改名して拒否を回避しない。削除後に再起動すると元PCKの表示へ戻る。

ゲームが更新されたら、このMODを無効化または上記uninstallで削除する。uninstallには元ゲームの版照合が不要。更新版への対応が確認されるまで旧PCKを使わず、pinだけを書き換えて継続しない。起動時の自動更新検知機能はない。

## 設定変更は再生成する

設定を省略したbuildは５人全員有効。設定を変える場合はJSONを用意し、`build --settings /path/to/settings.json` を追加する（repositoryでは [settings.example.json](settings.example.json) を参考にする）。

```json
{
  "SchemaVersion": 1,
  "Enabled": true,
  "EnabledCharacters": ["IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT"],
  "ReducedMotion": false
}
```

`Enabled:false` または `EnabledCharacters` から除いたキャラは元表示。`ReducedMotion:true` は周期的な動きを抑える。破損JSON・型不一致・未知field/ID・異なるschemaでは警告を出し、全無効で生成する。

設定はPCKへ封入するため、変更のたびに **新しい未使用outputへ再build → verify → 再install → ゲーム再起動** が必要。古い `user://PopSpireWomen/settings.json` は現行経路の設定入口ではない。起動中の差し替えはGodotの資源cacheに残るため反映を保証しない。

## デザインと確認範囲

Silent v05の基準デザインは**ユーザー承認済み**。他４人のv02と、背景分離・まばたき・休憩姿・UI等の派生は**自律制作の委任に基づく制作採用**で、個別のユーザー承認ではない。[現行ギャラリー](../docs/design/characters/review-gallery.md) / [制作素材と来歴](../docs/design/characters/production-assets.md)。以前のAPI制作記録は保持し、課金系エラー後の不足画像はユーザー指定のCodex内蔵生成で補っている。

親のQA共有（2026-10-09）では、元ゲームmainの通常起動でPCKをロードし、５人分の選択アイコンと選択背景の表示、Ironcladの新しいtop portraitを確認。Ironcladは元ID・カードを保ち、native UIでSTRIKEを使用して敵HP **43→37**、overlayの **idle_loop→attack→idle_loop** を確認した。選択人物の見切れはproduction descriptorで修正済み。

全５人の実戦・商人・休憩・死亡/復活・割込み/速度・音/VFX・相棒/武器/Orb、保存/再開、co-op、他MODとの競合、性能比較、通しプレイは引き続き [Issue #11](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/11) の確認対象。`affects_gameplay=false` は互換性の保証ではない。本書の更新ではゲーム起動や実装テストを再実行していない。

開発・既存検証の入口: [開発の案内](../docs/development/README.md) / [Issue地図](../docs/development/issue-map.md)。
