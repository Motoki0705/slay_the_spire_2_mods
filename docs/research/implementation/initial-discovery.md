# 初期技術調査

調査日: 2026-10-08。読み取りのみ。MODの実装・導入・ゲーム起動試験は未実施。

## ローカルで確認できたもの

- Steam App ID: `2868840`。
- ゲーム: `/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2`。
- Steam manifest の build ID: `23811903`。
- `data_sts2_windows_x86_64` 内に `sts2.dll`、`GodotSharp.dll`、`0Harmony.dll`、`sts2.xml` がある。
- BaseLib DLL は、ゲーム本体・対象Workshop領域・SlayTheSpire2のRoaming設定領域を調べた範囲では未検出。
- `dotnet`、`godot`、`ilspycmd` は PATH にない。環境全体で不在とは断定していない。
- 対象５キャラ: `ironclad`、`silent`、`regent`、`necrobinder`、`defect`。

## 候補となる実装方式

manifest JSON、C# DLL、アセット PCK を使う通常のMODを検討する。

[BaseLib](https://github.com/Alchyr/BaseLib-StS2) は `NCreatureVisuals`、`NRestSiteCharacter`、`NMerchantCharacter` のシーン変換を提供する。

[`CustomCharacterModel`](https://github.com/Alchyr/BaseLib-StS2/blob/master/Abstracts/CustomCharacterModel.cs) の `CustomCharacterSelectBg` はキャラ選択の背景シーン、`CustomCharacterSelectTransitionPath` は遷移マテリアルであり、別の経路。

ただし **CustomCharacterModel は追加キャラ用のAPI**。これを既存５キャラのスキン差し替えAPIと同一視しない。既存キャラへ接続するフックは、インストール済みゲームのAPIと対応バージョンを確認してから決める。

[参照MOD](https://steamcommunity.com/sharedfiles/filedetails/?id=3786286239) の説明ではC#とGDScript、BaseLibのfactoryを利用しており、公開版とbeta版でアニメーションAPIに差があるとされる。説明だけでは、この環境での互換性は確認できない。

## 追加確認が必要な事項

- インストール済みゲームの正確なAPI、既存キャラの選択シーンと戦闘外観を置換するフック。
- 使用するBaseLib・Godot・.NETのバージョン固定。
- 選択画面の入力・アンロック状態・文字領域を保つシーン構造。
- 戦闘のattack、hit、death等のアニメーションとゲームイベントの接続。
- キャラデザインのユーザーレビュー後に正式制作へ進む。

## 一次資料

- [Mega Crit: 発売日告知・５キャラ](https://www.megacrit.com/news/2026-02-19-release-date-trailer/)
- [BaseLib source](https://github.com/Alchyr/BaseLib-StS2)
- [BaseLib: Creature Visuals](https://alchyr.github.io/BaseLib-Wiki/docs/scenes/creature-visuals.html)
- [ModTemplate: Modding Basics](https://github.com/Alchyr/ModTemplate-StS2/wiki/Modding-Basics)
