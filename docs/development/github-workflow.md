# Issue・PRによる並列開発

対象repo: [Motoki0705/slay_the_spire_2_mods](https://github.com/Motoki0705/slay_the_spire_2_mods)。初期の調査・画像・方針をmainの基準コミットとして保存し、その後はIssueとPRを単位に進める。

## 担当を起動する前

Issueに目的、確定要件、対象/対象外、受入条件、入力資料、依存、担当名、モデル、所有する出力先を記載する。基準commitから専用worktreeとブランチを作る。並列担当の所有ファイルが重ならないよう分ける。

GitHubのassigneeは実在するGitHubアカウントだけなので、エージェント担当名・モデル・branchは本文に明示する。IssueとPRのリンクで進行を追えるようにする。

## fastを使わない起動

現在の親のアプリ設定はfastで、collaborationツールにはtier指定引数がない。新規担当には、ローカルで確認したCodex CLI 0.161.0の設定上書きを使う。グローバルのCodex設定を書き換えず、そのプロセスだけへ指定する。

```bash
codex exec \
  --model gpt-6.1-sol \
  -c 'model_reasoning_effort="max"' \
  -c 'service_tier="default"' \
  -c 'approval_policy="never"' \
  --sandbox danger-full-access \
  --cd "$TASK_WORKTREE" \
  --json \
  --output-last-message "$TASK_REPORT" \
  - < "$TASK_PROMPT_FILE"
```

難しい設計・実装にはモデルを `gpt-6-astra` とする。現在の作業環境が承認不要・filesystem unrestrictedであることに合わせたsandbox指定であり、Issueに書かれた所有範囲や公開・購入・導入の範囲を広げるものではない。他の環境では権限条件を再確認する。

新規execを使い、resume/forkで親の履歴を渡さない。プロンプトは自己完結させ、AGENTS.mdと共通のサブエージェント規則を読ませる。追加の子エージェントは起動させない。モデル・effort・service tierは取得できる実効メタデータと照合し、未確認を隠さない。指定を拒否された場合は別モデルやfastへfallbackしない。

CLIの`--config`上書きと `service_tier` は [公式設定資料](https://learn.chatgpt.com/docs/config-file/config-reference#service_tier) に基づく。`fast`と`priority`が同じFast modeであることは [OpenAI公式資料](https://developers.openai.com/api/docs/guides/fast-mode) を確認した。

## 成果の提出

担当worktreeで必要な検証を行い、commitしてそのbranchだけをpushする。`main`向けPRに、Issueとの関係、変更後の振る舞い、生成物、検証、未確認を記す。完了Issueは`Closes #...`で結ぶ。デザインのユーザーレビュー待ちは、その状態が分かるように提出する。

親はPRを統合してもよい状態かを判断する。生成完了、コンパイル成功、ゲーム起動、実プレイ、デザイン承認は別々の状態として扱う。PR作成だけで未実施の確認を完了扱いにしない。

## 運用を変えるとき

Issueの分割やworktreeの単位は、独立して確認できる成果と変更衝突の範囲から決める。担当数を増やすこと自体を目的にしない。依存が強くなれば統合し、１担当が複数の独立した問題を抱えれば分ける。必要なら命名・ラベル・分類を変更し、旧Issue/PRと新しい単位の関係を残す。
