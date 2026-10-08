# C# MOD基盤のビルドと書き出し

[Issue #7](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/7) の `engine-bootstrap` 担当成果。
**ローカルゲームDLLを参照した実ビルドは成功**。これは５人の外観MODの入口であり、女性化素材・動画・Spineを表示する完成MODではない。ゲーム導入・起動は行っていない。

設計入力は [方式比較](../research/implementation/options.md)、[骨格再利用](../research/implementation/rig-reuse.md)、[動作一覧](../research/motion/inventory.md)。RitsuLib案を実際のコンパイルまで進め、ゲーム起動での正式採用判断は残す。

## 固定した対象

| 項目 | 値・管理場所 |
| --- | --- |
| ゲーム | Windows x64 `v0.107.1 / 59260271`。最新版対応とはしない |
| .NET SDK | **9.0.318**、[global.json](../../mod/global.json)。roll-forward禁止 |
| TargetFramework | `net9.0`。ゲーム同梱runtimeは調査版の `9.0.7` |
| Godot SDK | **Godot.NET.Sdk/4.5.1**、[csproj](../../mod/PopSpireWomen.csproj) |
| Godot / ゲーム / Harmony API | ゲーム内の `GodotSharp.dll / sts2.dll / 0Harmony.dll` のローカル参照。すべて `Private=false` |
| RitsuLib compile package | **STS2.RitsuLib.Compat.0.107.1 0.6.7**。NuGetの完全一致範囲 `[0.6.7]` と [lock file](../../mod/packages.lock.json) |
| RitsuLib runtime | 作者の **0.6.7完全配布物** を別途使う。今回は導入・再配布しない |
| MOD ID / assembly / manifest | `PopSpireWomen` / `PopSpireWomen.dll` / `PopSpireWomen.json`、version `0.1.0` |

[GameReferences.props](../../mod/GameReferences.props) は `release_info.json` と参照DLL３本のSHA-256を固定する。Python入口とMSBuild直接実行の両方で、未指定・欠損・hash不一致をエラーにする。ゲームDLLのassembly version `0.1.0.0` だけでは版を判別しない。

RitsuLibは`IncludeAssets=compile`に限定し、runtime・content・build hookを取り込まない。transitiveのNuGet `GodotSharp 4.5.1` も版固定してassetを除外し、**ゲームのGodotSharpをコンパイルに使う**。現在はGodot Node scriptがないため、暗黙source generatorも無効にしている。

## 必要な環境

- Python **3.11以上**（標準ライブラリのみ）。
- .NET SDK **9.0.318**。初回restoreはNuGetへのネットワーク接続が必要。
- 上記版のローカルゲーム。Steamのrootディレクトリを指定し、`data_sts2_windows_x86_64`の方を渡さない。

SDKがない場合はtask用ディレクトリへ展開する。この作業で使ったLinux x64 SDKはMicrosoftの[公式release metadata](https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/9.0/releases.json)にある以下のもの。グローバルインストールは不要。

```bash
set -e
mkdir -p /tmp/sts2-tools/issue-7/dotnet
curl --fail --location \
  https://builds.dotnet.microsoft.com/dotnet/Sdk/9.0.318/dotnet-sdk-9.0.318-linux-x64.tar.gz \
  --output /tmp/sts2-tools/issue-7/dotnet-sdk-9.0.318-linux-x64.tar.gz
sha512sum --check <<'CHECKSUM'
e8685293a3512178e0de1bb3c1663e31fdf9d761af705094bf833cc1ff6b9a18c543aa4141f0216503c98039c719585a6d32905b0bbb3279e93b7e7616e047c3  /tmp/sts2-tools/issue-7/dotnet-sdk-9.0.318-linux-x64.tar.gz
CHECKSUM
tar -xzf /tmp/sts2-tools/issue-7/dotnet-sdk-9.0.318-linux-x64.tar.gz \
  -C /tmp/sts2-tools/issue-7/dotnet
```

別OSのSDKを使う場合もversionは揃える。今回検証した開発ホストはLinux/WSL、参照対象はWindows x64ゲーム版である。

## ビルド・通常検証・書き出し

リポジトリrootで実行する。`--dotnet`を省略すると`DOTNET`環境変数、次にPATH上の`dotnet`を使う。

```bash
export STS2_GAME_DIR='/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2'

python3 scripts/build_mod.py build \
  --dotnet /tmp/sts2-tools/issue-7/dotnet/dotnet

python3 scripts/build_mod.py test \
  --dotnet /tmp/sts2-tools/issue-7/dotnet/dotnet

python3 scripts/build_mod.py export \
  --dotnet /tmp/sts2-tools/issue-7/dotnet/dotnet
```

`--game-dir '/path with spaces/Slay the Spire 2'` は `STS2_GAME_DIR` より優先する。Pythonはshellを介さず引数配列でMSBuildを呼ぶ。

| コマンド | 動作と出力 |
| --- | --- |
| `build` | hash照合 → locked restore → `ExportRelease`実コンパイル。DLLは `mod/.godot/mono/temp/bin/ExportRelease/`。参照hash・lock hash・生成DLL hashは `mod/build/build-receipt.json` |
| `test` | Pythonのビルド／書き出し検査と、C#の設定／外観登録ポリシー検査。ゲームDLL・Godot nativeをロードしない。ゲーム場所の設定は不要 |
| `export` | `build`成功後、`dist/PopSpireWomen/` と `dist/PopSpireWomen-0.1.0.zip` を作る。ゲームのmodsへコピーする処理はない |

CLI home・NuGet package/cacheは既定で `/tmp/sts2-tools/issue-7/` に置く。`--tools-dir`でtask用保存先を変更できる。テレメトリー・開発用証明書生成を無効にする。SDK自体の自動ダウンロードはしない。

MSBuildを直接使う場合は、SDK選択のため **`mod/`へ移動してから** 実行する。

```bash
cd mod
/path/to/dotnet restore --locked-mode -p:Sts2GameDir='/local/game/root'
/path/to/dotnet build --no-restore -c ExportRelease -p:Sts2GameDir='/local/game/root'
```

依存更新を意図したIssueでのみ、版指定を編集して `dotnet restore -p:RestoreLockedMode=false -p:Sts2GameDir=...` でlockを更新する。通常buildでは依存版を勝手に更新しない。ローカルゲームの更新によるhash不一致も、単にpinを書き換えずAPI互換の確認を先に行う。

診断は `PSW001`（場所未指定）、`PSW002`（ファイル欠損）、`PSW003`（版/hash不一致）。SDK不一致なら必要な固定版と`--dotnet`の案内を表示する。

## 書き出すもの

```text
dist/
  PopSpireWomen/
    PopSpireWomen.dll
    PopSpireWomen.json
    README.md
  PopSpireWomen-0.1.0.zip
```

３ファイルだけを明示的に選び、buildディレクトリ全体をコピーしない。ゲームDLL・RitsuLib・runtime・SDK・PDB・生成画像はZIPに入らない。旧出力に不明ファイルがあればエラーにして保存する。`dist`がsymlinkの場合も拒否する。

**素材なしのbootstrapなので `has_pck=false`**。現在は`project.godot`・asset exporter・PCKを作る必要がない。後続の承認済み素材接続では、Godot 4.5.1のproject/export preset、headless import、専用PCK exportを別工程として追加し、実際にPCKを生成できた段階でmanifestを変更する。生のPNGを独自PCK writerで詰めただけのものを正式pipelineにしない。

ビルド成果物・cache・SDK・ゲームDLLはgit管理外。今回のZIPもローカル検証用であり、ゲーム導入やWorkshop公開を行うコマンドは提供していない。

## 入口と無効時の動作

[Bootstrap.cs](../../mod/code/Bootstrap.cs) は実ゲームの `ModInitializerAttribute` を使うpublic static入口。初期化は１回のみで、Harmony patch、新規キャラ登録、カード、保存model、RNG、戦闘triggerの変更はしない。

`user://PopSpireWomen/settings.json` を読み取る。[例](../../mod/settings.example.json)はデフォルト無効で、欠損・不正JSON・未知schemaも無効。設定ファイルやgame saveを作成／書換えしない。設定の反映は起動時のみ。

外観登録は次の順に絞る。

1. `Enabled=true`かつ`EnabledCharacters`に既存IDが明示されていること。
2. 対象ゲームversion/commitが一致すること。
3. コンパイルに含めたカタログに、該当IDの承認済み定義が一意にあること。
4. scene pathが `res://PopSpireWomen/` 配下の`.tscn`で、要求された全sceneが存在すること。
5. RitsuLibの実assembly versionが `0.6.7.0`であること。

現在の [ApprovedSkinCatalog](../../mod/code/Routing/SkinDefinition.cs) は空なので、５人全部を設定で有効にしても **ResourceLoader／Ritsu登録への呼出しは０**。これは純粋なC#ポリシー検査で確認済みであり、ゲーム画面で確認したという意味ではない。設定の読み取り・依存接続の例外も起動処理へ伝播させない。

[RitsuSkinRegistrar](../../mod/code/Routing/RitsuSkinRegistrar.cs) の次のAPIを、固定NuGetパッケージと実ゲームDLLに対してコンパイルした。

- `RitsuLibFramework.CreateContentPack(ModId)`
- `CharacterSceneAssetSet(VisualsPath: ...)` / `CharacterUiAssetSet(CharacterSelectBgPath: ...)`
- `CharacterAssetProfile(Scenes: ..., Ui: ...)`
- `CharacterAssetReplacement(existingCharacterEntry, profile)` → `Apply()`

このadapterは変更するfieldだけを渡す。`CharacterModel`の派生クラスは登録しない。RitsuLibの`Apply()`はframeworkのdiscovery windowへ処理を予約するAPIなので、コンパイル成功や戻り値を画面切替成功の証拠にはしない。依存ロード／deferred登録／描画は今後のruntime確認対象。

## 通常検証の結果

2026-10-09、[固定した検証記録](../../mod/validation/issue-7.json)。

- **実ビルド成功**: .NET SDK 9.0.318、Godot.NET.Sdk 4.5.1、RitsuLib compat 0.6.7、ゲームDLLの固定hashを使用。警告０／エラー０。
- **C# 10ケース**: 未指定・不正設定、空カタログ、未知版、未承認／未知ID／重複定義、外部／不正path、資源欠損／例外、選択したIDだけの登録、複数surfaceの一部欠損を検査。
- **Python 7ケース**: 未指定／欠損／変更された参照、配布allowlist、同入力の再書き出し、旧出力の不明ファイル保持、symlink拒否を検査。
- **実コマンドの負例６件**: Python入口と直接MSBuildの両方で、未指定・欠損・hash不一致が非zero終了し、それぞれ`PSW001/002/003`を出した。
- **実ZIP書き出し**: DLL＋JSON＋READMEだけを確認。build出力にもゲーム・Ritsu依存DLLはない。
- validatorは指定どおり **０回**。上記は実装担当の通常検証。

## 次のruntime接点と未確認

正式素材と導入許可が揃った後、以下を別Issueで行う。

- 内蔵ローダーでmanifest／RitsuLib完全配布物／initializerが実際にロードされること。まず無効状態の起動ログと元表示を確認する。
- 承認済み１キャラについて、runtimeの `CharacterModel.Id.Entry` と登録IDを照合し、MOD固有path・UIDのsceneを専用PCKへ収録する。カタログの承認flagは画像案の生成成功だけで立てない。
- 最初の接点は `CharacterSelectBg` と `VisualsPath / CreateVisuals`。`ResourceLoader.Exists`は型・scene内node・Spine契約まで保証しないため、実load／instantiate、欠損時復帰、登録解除も検査する。
- 戦闘は既存骨格への再skin/reweightを第一PoCとし、trigger、event、攻撃時刻、死亡待ち、復活、割込み、速度、VFX付着点を保つ。Osty／Sovereign Blade／Orbの独立制御を変えない。
- Node scriptを追加する段階で、必要なGodot source generatorと`ScriptManagerBridge.LookupScriptsInAssembly`を有効にし、PCK内script参照を実機確認する。
- 起動・実プレイ、save再開、片側のみ導入するco-op、他skinとの競合、性能は未検証。`affects_gameplay=false`だけで互換性を保証しない。

RitsuLib側の一次資料は、調査入力と同じ [commit 2332d9d](https://github.com/BAKAOLC/STS2-RitsuLib/tree/2332d9d054f431887aaeffef9aa634959f148889)。取得した [NuGet 0.6.7](https://www.nuget.org/packages/STS2.RitsuLib.Compat.0.107.1/0.6.7) のrepository metadataも同commit。今回、比較調査や別frameworkへのfallbackは行っていない。
