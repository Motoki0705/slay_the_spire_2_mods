# Pop Spire Women — development 0.1.0

Issue #7のC#基盤とIssue #8の選択背景runtime。既存５人の外観用で、新規キャラ・カード・ゲームルールは追加しない。
承認済みruntime素材は **０件**。未設定・無効設定・有効設定のいずれでも、現版は外観を登録せず元表示を保つ。

- 対象: Windows x64 **v0.107.1 / 59260271 / Godot 4.5.1 / .NET 9**。
- コンパイル依存: `STS2.RitsuLib.Compat.0.107.1` **0.6.7**。
- runtimeには作者の **RitsuLib 0.6.7完全配布物** が別途必要。NuGet内のDLL１枚を導入物の代わりにしない。
- 既定の配布物は `PopSpireWomen.dll`、`PopSpireWomen.json`、本書だけ。`--with-pck` 書き出しでは専用 `PopSpireWomen.pck` と `has_pck=true` のmanifestを作る。PCKはGDScriptと５人分の空の背景定義のみで、承認済み画像・動画は含まない。
- ゲームDLL、Godot、Spine、RitsuLib、レビュー画像、技術fixtureは配布物に含めない。
- 設定は `user://PopSpireWomen/settings.json` を起動時に読む（作成・書換えはしない）。省略時は無効。
  `{"SchemaVersion":1,"Enabled":false,"EnabledCharacters":[],"ReducedMotion":false}` が既定。
  `ReducedMotion=true` は承認済み背景を接続した際に動画を止めてposterを使う設定。設定ファイルの反映は再起動時。
  後続の素材接続で用いる既存IDは `IRONCLAD / SILENT / REGENT / NECROBINDER / DEFECT`。

ビルド、ローカルZIP/PCK、standalone Godotでの合成動画の切替・解放・fallbackを検証。
**ゲーム導入・起動・表示・save・マルチプレイの互換性は未検証**。Regentの７星座hoverの実装・実機配置も未完了（独立overlayの接点のみ）。
`affects_gameplay=false` は互換性の検証結果ではない。

手順: [C#基盤](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/main/docs/development/build.md) / [選択背景とPCK](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/main/docs/development/select-playback.md)。
RitsuLibの配布説明: [固定sourceのPackage Choices](https://github.com/BAKAOLC/STS2-RitsuLib/blob/2332d9d054f431887aaeffef9aa634959f148889/README.md#package-choices)。
