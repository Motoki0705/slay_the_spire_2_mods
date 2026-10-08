# 画像生成のAPI運用

ユーザー指定（2026-10-09）: **画像生成はAPI経由で行う。認証は `OPENAI_API_KEY` を使用する。** 以後、組み込み画像生成ツールへ無断で戻さない。これ以前の画像は、来歴上は組み込み `image_gen` のまま記録する。

## 現在の実行方法

`imagegen` スキルに付属する `scripts/image_gen.py` を直接使う。独自のSDK呼び出しコードで生成器を作り直さない。参照画像や既存画像の編集は `edit`、新規生成は `generate` を使う。

現在のCLI既定モデルは `gpt-image-2`。今回のサイレント編集は、質感と本人の保持を優先して `quality=high`、`1024x1536`、PNG、既存絵と参照MOD画像の２入力を使う。具体的な生成指示は [silent-v04-edit.txt](../../../art/prompts/silent-v04-edit.txt)。出力先は `output/imagegen/silent/silent-v04.png`。

実行例（キーは環境変数で渡し、コマンドやファイルへ埋め込まない）:

```bash
uv run --with openai --with pillow python \
  /mnt/c/Users/kamim/.codex/skills/.system/imagegen/scripts/image_gen.py edit \
  --model gpt-image-2 \
  --image art/concepts/silent/silent-v03.png \
  --image art/references/silent/mod-reference/kaguya-silent-raven/user-provided-selection.png \
  --prompt-file art/prompts/silent-v04-edit.txt \
  --no-augment \
  --size 1024x1536 \
  --quality high \
  --output-format png \
  --out output/imagegen/silent/silent-v04.png
```

このスキルのパスは現在の環境のもの。別環境へ移す際は、利用可能なスキルの位置とCLI仕様を確認して読み替える。

## 記録と確認

- 実行モデル、画質、解像度、生成指示、入力画像の役割とハッシュ、出力とハッシュを残す。
- キー本体を表示・ログ保存・リポジトリへ保存しない。実行環境からキーが見えるかだけを確認する。
- 元のレビュー画像は上書きせず、別の版として出力する。
- 出力後に、指定した変更と保持すべき部分を画像で確かめる。API成功だけをデザインの承認とはしない。
- 「露出15%」は見た目の調整目安として扱い、厳密な面積測定を行ったとは報告しない。

## 現在の接続状態

2026-10-09、ユーザーから指定された `C:\Users\kamim\.codex\openai.env`（WSL側 `/mnt/c/Users/kamim/.codex/openai.env`）でキーを確認した。キーの内容を表示せず、その実行プロセスの `OPENAI_API_KEY` へ読み込んで、付属CLIを起動する。永続的なシェル設定やリポジトリにはコピーしない。

環境ファイルはdotenvとして読み、`OPENAI_API_KEY` だけをプロセス環境へ渡す。環境ファイルをシェルスクリプトとして実行しない。上記の実行例はキーがプロセス環境に設定された後のコマンドである。

最初のv0.4編集リクエストは `401 invalid_api_key` で認証を拒否された。読み込み形式に問題がないことを確認後、ユーザーが同じ環境ファイルのキーを更新し、２回目の実行で成功した。出力は [silent-v04.png](../../../output/imagegen/silent/silent-v04.png)、[生成記録](../../../output/imagegen/silent/silent-v04.provenance.json)。CLIが報告した編集時間は92.4秒。

[認証失敗の記録](../../../output/imagegen/silent/silent-v04.request.json)にはモデル・入力・出力予定・エラーコードだけを残し、キーやAPIの生エラーメッセージを保存していない。エラーの意味は [OpenAI公式のエラーコード資料](https://developers.openai.com/api/docs/guides/error-codes) を参照。組み込み生成や別モデルへ切り替えて回避しない。
