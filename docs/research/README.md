# 調査管理

[文書全体の案内](../README.md)

サブエージェント起動前に、モデル・effort・具体的な問い・担当範囲・除外範囲・出力先・終了条件を渡す。履歴は引き継がず、依頼は自己完結させる。同じ資料の調査を重複させず、必要な索引や根拠を担当間で共有する。

調査を拡張するときは、まず既存の結論で答えられない問いを分け、独立して答えられる範囲だけを委任する。調査の都合で共有構造を増やす前に、[文書の拡張の考え方](../README.md#拡張を判断する考え方)と[参照資料の拡張の考え方](../../art/references/README.md#拡張を判断する考え方)に照らす。既存分類の変更が必要なら、稼働中の担当と新しい所有範囲・出力先を再合意してから移行する。下の担当表を将来の固定組織とは扱わない。

## 担当と専用出力先

| 担当 | 指定モデル / effort | 対象 | 文書・証拠の出力先 | 状態 |
| --- | --- | --- | --- | --- |
| `ironclad_silent_canon` | GPT-6.1 sol / xhigh | アイアンクラッド、サイレント | [characters/ironclad-silent.md](characters/ironclad-silent.md)、`art/references/ironclad/`、`art/references/silent/` | 完了 |
| `regent_necrobinder_canon` | GPT-6.1 sol / xhigh | リージェント、ネクロバインダー、オスティ | [characters/regent-necrobinder.md](characters/regent-necrobinder.md)、`art/references/regent/`、`art/references/necrobinder/` | 完了 |
| `defect_world_canon` | GPT-6.1 sol / xhigh | ディフェクト、世界観、公式美術方針 | [characters/defect-world.md](characters/defect-world.md)、`art/references/defect/`、`art/references/world/` | 完了 |
| `motion_inventory` | GPT-6.1 sol / xhigh | 動く画面・状態・キャラ固有動作、動画AI使用候補 | [motion/inventory.md](motion/inventory.md)、`motion/evidence/` | 完了 |
| `implementation_architecture` | GPT-6 astra / max | MODフレームワーク、描画、アニメ同期、骨格・モーション再利用の方式選定 | `implementation/options.md`、`implementation/rig-reuse.md`、`implementation/evidence/` | 完了 |
| `video_cost_model` | GPT-6.1 sol / max | 動作別の尺・解像度とMiniMax H3 / Seedance 2.5の生成費用 | [costs/video-generation.md](costs/video-generation.md)、`costs/evidence/` | 完了 |
| `prompt-api-research` | GPT-6.1 sol / max / default指定 | 画像API公式のプロンプト・参照・編集指針 | 親が [art-direction/non-generic-characters.md](art-direction/non-generic-characters.md) へ統合 | 調査完了・親が統合、Issue #24 |
| `character-art-research` | GPT-6 astra / max / default指定 | 絵作りの一次資料、旧４案の誘導と華奢さの設計 | 上記調査と [改訂案](../design/characters/slender-revision-brief.md) へ親が統合 | 調査完了・親が統合、Issue #24 |

文書階層の変更指示に合わせ、稼働中の二担当には上記の新しい専用出力先を通知し、双方の了承を得た。各担当は自分の出力だけを移動・編集し、共有索引は親が更新する。

## 調査の基準

公開リポジトリには、制作物、調査の結論、出典・ハッシュ、再現用スクリプトを置く。ゲームから抽出した `motion/evidence/resources/` と逆コンパイルしたIL等はローカルの証拠として保持し、Gitの対象から外す。文書中のそのようなリンクはローカル生成物を指す。取得元の版とmanifestを手掛かりに、利用者が所有するゲームから再現する。

- 一次本文、公式原画、ゲーム内資料を照合する。公式サイトに掲載されたファンアートやSteam内の報道転載を公式設定と取り違えない。
- StS1 / StS2、開発中 / 現行、公式事実 / 視覚的観察 / 制作上の提案を分ける。
- ローカルゲーム資料は **v0.107.1 / commit 59260271 / 2026-06-18** の版。2026-10時点の広報と同じ版とはしない。
- ゲーム原本は変更せず、必要な範囲だけを読み取る。抽出した一次リソースと派生画像には出典・版・変換・ハッシュを記録する。
- 未確認事項と実プレイ未検証を明示する。調査と設計を、実装済み・動作確認済みと称さない。

## ユーザーの調査指定

> あらゆる参照画像や設定のリサーチはサブエージェントを用いて深く行いましょう。サブエージェントはgpt 6.1 sol xhighを用いて並列的に行ってください。世界観をよく理解できるようにしてください。
>
> 動画生成AIの使用箇所も洗い出しもサブエージェントを使用すること。gpt 6.1 solにさせること。
>
> 実装方法も考えてください。サブエージェントはgpt 6 astra maxを使用すること。どのようなフレームワーク等があるかの調査や今回適切な方法を調べさせます。
>
> docs/について体系化して下さい。現在のままでは直下が膨らんでしまいます。サブエージェントを使用する場合もあらかじめ出力先を設定してください。
>
> 並列して、必要なアニメーション個所がわかったので、これを各キャラのアニメーションとして動画生成するコストをサブに調べさせましょう。gpt 6.1 sol maxを使用してください。また、そのためには各アニメーションの秒数や必要な解像度を具体的に特定する必要があります。
>
> そもそも、現在のオリジナルのゲームエンジンはアニメーションを動画クリップではなく、物理エンジン的なもので表現している可能性はある？その場合、単純な動画の置き換えでは済まない可能性がある？関節などを設定してモーションは使いまわすのがよさそう。このような方針の選定等もさせること。
