# Slay the Spire 2 — 全キャラ女性化 MOD

プレイアブル全５キャラの女性化と、魅力的なキャラ選択アニメーションを制作するプロジェクト。

現在は **キャラクター方針のユーザーレビュー段階**。C#基盤と選択背景の動画・poster描画/PCK工程を実装し、合成fixtureで検証済み。承認済み素材のcatalogは空で、ゲーム内表示は未確認です。

開発・制作の意図と作業ルールは [AGENTS.md](AGENTS.md)。基準コミット以後の変更はGitHub Issueごとに担当とworktreeを分け、PRで管理します。

- [ドキュメント案内](docs/README.md)
- [現行のキャラクター方針 v0.3](docs/design/characters/review-v03.md)
- [公式のキャラクター設定・視覚資料](docs/research/characters/README.md)
- [動画生成AIの制作方針と動作調査 — MiniMax H3 / Seedance 2.5](docs/design/animation/video-production-v01.md)
- [キャラ・世界観の並列調査](docs/research/README.md)
- [技術調査・未確認事項](docs/research/implementation/initial-discovery.md)
- [C#基盤のビルド](docs/development/build.md) / [選択背景の再生・PCK・検証](docs/development/select-playback.md)

画像制作: ユーザー指定により、今後は `OPENAI_API_KEY` を使うAPI経由。[実行方法](docs/design/characters/image-api-workflow.md)。元の色・装備・人物像を人型女性へ翻案し、５人の特徴を描き分けます。キャラ選択画面のアニメーションは、レビュー後に動画生成AIで制作します。

v0.1 は単調さと「魅力」の捉え違い、v0.2 は女性化・擬人化の不足で不採用です。履歴として残していますが、現行の制作見本には使いません。

文書や資料を増やす際の判断の順序、分類を見直す考え方、互換性を崩す再編の扱いは、[docsの案内](docs/README.md#拡張を判断する考え方)と[参照資料の案内](art/references/README.md#拡張を判断する考え方)に記載しています。現在の構造は今後の目的や根拠に応じて見直せます。
