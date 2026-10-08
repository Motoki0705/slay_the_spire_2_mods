# Slay the Spire 2 — 全キャラ女性化 MOD

プレイアブル全５キャラの女性化と、魅力的なキャラ選択アニメーションを制作するプロジェクト。

現在は **Spine Professional・動画生成AIを使わず、完成に向けて自律制作する段階**。[完成工程](docs/development/autonomous-delivery.md)に従い、Godot側のアニメーションと画像API素材を並行して制作します。Silent v0.5はユーザー承認済み、他４人は[華奢さを軸に改訂](docs/design/characters/slender-revision-brief.md)します。現時点でゲーム用素材のcatalogは空、ゲーム内表示は未確認です。

開発・制作の意図と作業ルールは [AGENTS.md](AGENTS.md)。基準コミット以後の変更はGitHub Issueごとに担当とworktreeを分け、PRで管理します。

- [ドキュメント案内](docs/README.md)
- [５人のレビュー候補を比較する](docs/design/characters/review-gallery.md)
- [開発の進行状況とIssue地図](docs/development/issue-map.md)
- [現行のキャラクター方針 v0.3](docs/design/characters/review-v03.md)
- [公式のキャラクター設定・視覚資料](docs/research/characters/README.md)
- [動画生成AIの制作方針と動作調査 — MiniMax H3 / Seedance 2.5](docs/design/animation/video-production-v01.md)
- [キャラ・世界観の並列調査](docs/research/README.md)
- [技術調査・未確認事項](docs/research/implementation/initial-discovery.md)
- [C#基盤のビルド](docs/development/build.md) / [選択背景の再生・PCK・検証](docs/development/select-playback.md)

画像制作は `OPENAI_API_KEY` を使うAPI経由。[実行方法](docs/design/characters/image-api-workflow.md)。元の色・装備・人物像を人型女性へ翻案し、５人の特徴を描き分けます。キャラ選択画面の動きもGodot側で制作し、動画生成AIは使用しません。

v0.1 は単調さと「魅力」の捉え違い、v0.2 は女性化・擬人化の不足で不採用です。履歴として残していますが、現行の制作見本には使いません。

文書や資料を増やす際の判断の順序、分類を見直す考え方、互換性を崩す再編の扱いは、[docsの案内](docs/README.md#拡張を判断する考え方)と[参照資料の案内](art/references/README.md#拡張を判断する考え方)に記載しています。現在の構造は今後の目的や根拠に応じて見直せます。
