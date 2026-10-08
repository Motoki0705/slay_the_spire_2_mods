# ドキュメント案内

現在は **公式調査を反映したキャラクター方針の再レビュー段階**。正式な画像・動画・MODは未実装。

リポジトリでの作業方法と、会話で確定した意図は [AGENTS.md](../AGENTS.md) にまとめる。今後の開発はGitHub Issue単位のworktreeとPRで進める。

## 最初に読むもの

| 目的 | 文書 |
| --- | --- |
| キャラの改訂方針をレビューする | [キャラクター方針 v0.3](design/characters/review-v03.md) |
| 画像をAPI経由で生成・編集する | [画像APIの運用](design/characters/image-api-workflow.md) |
| 動画生成AIの制作方針を見る | [動画制作方針](design/animation/video-production-v01.md) |
| 設定と世界観の根拠を確認する | [キャラ調査の入口](research/characters/README.md) |
| 動く箇所を確認する | [動作の棚卸し](research/motion/inventory.md) |
| フレームワークと実装方法を比較する | [実装方式](research/implementation/options.md) |
| 元の骨格・モーションを再利用できるか調べる | [骨格とモーションの再利用](research/implementation/rig-reuse.md) |
| 尺・解像度・動画生成費用を確認する | [動画素材仕様と費用](research/costs/video-generation.md) |
| 調査担当と出力先を確認する | [調査管理](research/README.md) |
| Issue・worktree・PRとfastを使わない担当起動 | [並列開発の運用](development/github-workflow.md) |
| 原作の参照画像を探す | [キャラ別参照フォルダー](../art/references/README.md) |

## 配置

```text
docs/
  README.md
  design/
    characters/
      review-v03.md
      archive/rejected-v01.md
      archive/rejected-v02.md
    animation/
      video-production-v01.md
  research/
    README.md
    characters/
      README.md
      ironclad-silent.md
      regent-necrobinder.md
      defect-world.md
    motion/
      inventory.md
      evidence/
    implementation/
      initial-discovery.md
      options.md
      rig-reuse.md
      evidence/
    costs/
      video-generation.md
      evidence/
```

## 現在の保存の原則

- `design/` は今回作るものの方針、`research/` はその判断に使う事実・比較・証拠。
- 現在は `docs/` 直下をこの案内だけにし、詳細は目的別の階層へ置く。
- 不採用のデザインは `design/characters/archive/` に残し、現行の見本と区別する。
- サブエージェント起動前に、担当範囲と文書・証拠の出力先を [調査管理](research/README.md) に設定する。
- 画像・動画の参照元は `art/references/<character>/`、生成画像は `art/concepts/`、生成指示は `art/prompts/` に置く。調査資料と完成MOD素材を混ぜない。
- フォルダー移動時は相対リンクを更新する。稼働中のエージェントが所有する出力は、担当と調整してから移動する。

## 拡張を判断する考え方

この構造は、現在の問いと成果物に合わせた出発点である。将来の拡張では、既存のフォルダー名よりも、読む人が判断の根拠と現在の結論へ到達できることを優先する。

1. **追加の目的を言葉にする。** 誰が、何を知り、どの判断をするための情報かを先に考える。新しい文書を置くこと自体を目的にしない。
2. **既存の区分で説明できるかを見る。** 既存文書への追記、節の分割、新しい分類のいずれが、その問いを最も自然に表すかを選ぶ。例外の説明や同じ内容の重複が増える場合は、分類そのものを見直す。
3. **変更の小ささと、理解しやすさを比べる。** 現在のパスを維持する利益と、構造を改める利益を比較する。過去の配置を守るために意味の異なる情報を同居させる必要はない。
4. **根拠・判断・状態が追えるかを確かめる。** 調査事実と提案、現行と旧案、確定と未確認が読み手に区別できるかを確認する。必要な履歴の量も、その判断を再検討できる範囲から決める。
5. **移行後の利用者の経路を確かめる。** 初めて来る人と既存リンクから来る人の両方が、現行の入口へ辿り着けるかを見る。追加のたびに、案内・相互参照・担当の出力先も更新する。

### 互換性を崩す再編を選ぶとき

名前、階層、文書の分割単位、メタデータの形は変更できる。既存の概念が新しい対象を誤って説明する場合や、二重管理が判断を曖昧にする場合は、改名・統合・分割・旧形式の廃止を検討する。すべての旧パスや形式を永久に維持することは前提にしない。

変更前に、捨てる前提と残す意味、影響する文書・スクリプト・エージェント出力を洗い出す。変更の際は「なぜ変えたか」「何が対応するか／対応しなくなるか」「移行をどう確かめたか」を残す。旧版保存、対応表、一時的な案内のどれが必要かは影響に応じて選ぶ。代替できない根拠の消失を伴う変更は、単なる整理と区別して判断する。

最後に、この案内が実際の構造と次の拡張を説明できるかを読み直す。ルールが繰り返し例外を生むなら、ルール自体も改める。
