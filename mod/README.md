# Pop Spire Women — bootstrap 0.1.0

Issue #7のC#基盤。既存５人の外観用で、新規キャラ・カード・ゲームルールは追加しない。
承認済みruntime素材は **０件**。未設定・無効設定・有効設定のいずれでも、現版は外観を登録せず元表示を保つ。

- 対象: Windows x64 **v0.107.1 / 59260271 / Godot 4.5.1 / .NET 9**。
- コンパイル依存: `STS2.RitsuLib.Compat.0.107.1` **0.6.7**。
- runtimeには作者の **RitsuLib 0.6.7完全配布物** が別途必要。NuGet内のDLL１枚を導入物の代わりにしない。
- この配布物は `PopSpireWomen.dll`、`PopSpireWomen.json`、本書だけ。ゲームDLL、Godot、Spine、RitsuLib、生成画像は含まない。PCKはないのでmanifestは`has_pck=false`。
- 設定は `user://PopSpireWomen/settings.json` を起動時に読む（作成・書換えはしない）。省略時は無効。
  `{"SchemaVersion":1,"Enabled":false,"EnabledCharacters":[]}` が既定。
  後続の素材接続で用いる既存IDは `IRONCLAD / SILENT / REGENT / NECROBINDER / DEFECT`。

ビルドとローカルZIP書き出しは確認対象。**ゲーム導入・起動・表示・save・マルチプレイの互換性は未検証**。
`affects_gameplay=false` は互換性の検証結果ではない。

リポジトリ内の手順: [docs/development/build.md](https://github.com/Motoki0705/slay_the_spire_2_mods/blob/issue-7-mod-bootstrap/docs/development/build.md)。
RitsuLibの配布説明: [固定sourceのPackage Choices](https://github.com/BAKAOLC/STS2-RitsuLib/blob/2332d9d054f431887aaeffef9aa634959f148889/README.md#package-choices)。
