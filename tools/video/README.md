# H3 / 768P 制作CLI

[Issue #49](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/49) の、親制作担当が実行するローカルツール。[Issue #57](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/57) でcreditsのキー選択に対応した。モデルは **`MiniMax-H3`**、解像度は **`768P`** に固定。依存はPython 3.10以降の標準ライブラリと `ffprobe`。排他・永続化はPOSIXを使うのでWSL/Linuxで実行する。ゲームやPCKの変更は行わない。

公式根拠と未確認事項は [制作仕様メモ](../../docs/research/costs/minimax-h3-production-v02.md)、機械可読の契約は [h3-api-contract.json](h3-api-contract.json) と [creditsコマンド契約](h3-credit-client-contract.json)。以下はリポジトリrootからのコマンド。

## 入力と送信前の確認

UI文字を含まない **16:9** のローカル画像とUTF-8のプロンプトを用意する。先頭・末尾画像の寸法を揃え、末尾を省略すると同じ画像を２つのroleへ送る。APIの `ratio` は `adaptive`。始終フレーム方式では `ratio=16:9` を送っても無視されるので、入力画像で比率を決める。

```bash
python3 tools/video/h3.py submit \
  --billing credits \
  --first-frame /tmp/sts2-motion-v02/inputs/silent.png \
  --prompt-file /tmp/sts2-motion-v02/inputs/silent-motion.txt \
  --state-dir /tmp/sts2-motion-v02/h3-jobs \
  --duration 8 --take-id credits-take-01 --dry-run
```

`--dry-run` は画像を `ffprobe` で調べ、入力hash、request fingerprint、課金方式・キー変数名、USD/credits見積、jobの予定pathをJSONで返す。HTTP送信・job作成・キーやenv-fileの読み取りを行わない。PNG/JPEG/WEBP/HEIC/HEIFを判別し、実際に `ffprobe` が読めるものを使う。画像は256〜5760px、各30,000,000bytes以内、実際のbase64入りbodyは64,000,000bytes以内。入力16:9の許容は幅１px、始終の寸法一致はこの制作CLIの方針。透明画像を16:9へ伸ばさず、親が画角を整える。

## submit / status / download

実送信は **親が** `--dry-run` を外して同じコマンドを実行する。`submit --billing` は次の２方式で、省略時は従来互換の **payg**。

| 方式 | 読み取る変数 | 用途 |
| --- | --- | --- |
| `--billing credits` | **`MINIMAX_SUBSCRIPTION_KEY`** | Subscription KeyによるM Plan枠・対象credits |
| `--billing payg` | **`MINIMAX_API_KEY`** | 従量API Keyによる現金残高 |

選んだ変数だけを既存のプロセス環境から取り、未設定なら任意の `--env-file /path/to/private.env` 内の同じ変数を読む。別方式の変数へfallbackしない。`source`、シェル評価、変数展開、エスケープ解釈を使わず、当該変数の既存環境を優先する。キーはコマンド引数に渡さない。送信先・API本文は共通で、未定義の `billing` fieldは送らない。

jobは `billing: {mode, key_env}` と `estimated_cost.total_credits` を保存する。768Pの出力は80 credits/秒相当、始終２画像の８秒は640 credits、５人の初回は3,200 creditsの見積。USDは公開従量価格による換算値で、実請求・残高の確認ではない。Subscription Keyによる標準H3の実受付はこの担当では未確認。公式FAQとAPI注意書きの違いは [制作仕様メモ](../../docs/research/costs/minimax-h3-production-v02.md#creditsの経路と留保) に残す。

`submit` が返す `job` を以下の `H3_JOB` に指定する。

```bash
H3_JOB='/tmp/sts2-motion-v02/h3-jobs/<request_fingerprint>-credits-take-01.json'

python3 tools/video/h3.py status --job "$H3_JOB"
python3 tools/video/h3.py status --job "$H3_JOB" --wait --interval 10 --max-wait 600

python3 tools/video/h3.py download --job "$H3_JOB" \
  --output /tmp/sts2-motion-v02/source/silent-credits-take-01.mp4
```

`status / download / attach` は保存済みjobの方式を既定にする。`--billing credits|payg` を明示する場合は記録と一致する必要があり、不一致はキーを読む前に `billing_mismatch` で停止する。課金記録がない旧jobはpaygとして扱う。方式や変数名が壊れた記録は `job_billing_invalid` で停止する。確認済み出力のオフライン再利用でも、明示した方式の不一致は拒否する。

- `submit`: 送信前にfingerprintと入力hashを含むjobを原子的に保存し、fsyncしてから **POST１回だけ**。ファイルロックにより同時実行でも同じfingerprint/takeは再送しない。既存jobはその状態を返し、失敗や応答不明でも自動で新規taskを作らない。
- `status`: 既存taskへのGETだけ。`queued / running / succeeded / failed / cancelled` を安全な項目だけ保存する。待機期限やGETの通信エラー後も同じjobで再開できる。`--timeout` は各HTTP接続のtimeout。`--max-wait` はpoll間で判定するので、進行中の１回のGET分は超える場合がある。
- `download`: 毎回GET queryで新しい `task.content.url` を取得し、Bearerを付けずにGET。上限は初期256MiBで `--max-bytes` 変更可。Content-Length・種類・動画stream・全frameの `ffprobe` 読取り・尺・比率を確認し、hash/bytes/日時/stream情報をjobへ保存する。生成尺±0.5秒、出力16:9±1%は制作上の確認基準であり、公式pixel/fps保証ではない。途中ファイルは失敗時に削除し、既存出力を上書きしない。記録済みのhashと一致する出力はキーも通信も使わず再利用する。

queryがH3以外、768P以外、別尺・別taskを返した場合は停止し、別モデルへ変更しない。stdoutは安全な結果JSON、stderrは固定のcodeと必要な数値HTTP/provider codeだけ。終了値は通常成功0、操作エラー・送信状態不明2、`failed / cancelled` 3、poll中の中断130。`submit` の0はtask受付または既存受付記録であり、動画の品質合格ではない。

## 応答不明と明示的な再試行

POST timeout、5xx、JSON不正、task ID欠落、中断の場合は `unknown`、強制終了時は `submitting` の予約が残る。**そのjobを消して再送しない。** 送信直前にプロセスが終了して実際には未送信だった場合も、CLIは区別できないので再送を止める。同じstate-dirを５人と全takeで使い続ける。別ディレクトリ・job削除・明示的に変更した入力やtakeの重複課金までは防げない。

親が送信時刻・アカウントのtask一覧を照合してIDを特定できた場合は、GETで設定を確認し、元の予約へ関連付ける。

```bash
python3 tools/video/h3.py attach --job "$H3_JOB" --task-id '<recovered_task_id>'
```

`attach` はprompt/画像がそのtaskと同一かまではAPIから照合できない。親が対応を確かめる。すでにtask IDがあるjobを別IDへ上書きしない。新しいtakeが必要な場合は `submit ... --take-id take-02` と明示する。これは同一入力でも **新しい有料task** になる。400/401/402/422/429を受けた場合も自動再送は行わない。

fingerprintはAPI本文だけから作り、キーや課金方式を含めない。従量の402等で拒否された同じtakeは、キーだけ変えても予約を再利用し、`--billing credits` へ変えた場合は `billing_mismatch` で止める。creditsで新しく要求する場合は、親が **同じstate-dirで新take-id**（例: `credits-take-01`）を明示する。元の拒否記録を消さない。

## 音声と採用

H3に無音を保証するcreate項目は確認できていない。プロンプトの無音指定だけで納品判断しない。生の生成MP4とhashを保持し、`output.audio_removal_required` がtrueなら加工時に音声を除く。falseの場合もゲーム内の原音・イベント・音量との接続確認は親の担当。

```bash
ffmpeg -i /tmp/sts2-motion-v02/source/silent-credits-take-01.mp4 \
  -map 0:v:0 -an -c:v copy /tmp/sts2-motion-v02/source/silent-credits-take-01-silent.mp4
```

このコマンドは例で、CLIが自動実行する処理ではない。加工出力のhash・変換・採否を別途記録する。同じ始終画像での生成受付、つなぎ目、本人・華奢さ・衣装・表情、動作の質は実APIのtakeで確認する。戦闘・休憩・商人の姿勢やGodot同期、Osty/剣/Orbの制御はこのCLIの対象外。

taskのquery対象は直近７日。署名URLの正確なTTLは公開仕様で未確認なので、成功後は速やかにdownloadする。URL期限切れ後は同じ `download` コマンドでqueryからやり直す。署名URL・生レスポンス・base64・prompt本文・キー・環境ファイル内容はjobにも出力にも書かない。

## 通常検証

```bash
python3 -m unittest discover -s tests/video -v
```

全HTTPをmockし、payload/auth、先行予約、並行submit、timeout・中断・crash後の重複防止、poll再開、ID復旧、失敗code、署名URL失効後の再取得、BearerのCDN不転送、サイズ・尺・比率・probe不正、秘密を出さないenv解釈を確認する。元の32件にcredits・旧job・全再開コマンドの方式保持・fallback拒否・402後の新take・Subscription Keyの非出力を確認する10件を加えた。`ffmpeg/ffprobe` がある環境では、無地のPNGと８秒MP4を使う実probe確認も行う。このsynthetic素材はH3生成物やデザインの証拠ではない。結果は [validation.json](../../tests/video/validation.json)。実送信と５人の動画完成は [Issue #48](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/48) の親担当。

## 実測の768P出力

親の本番５タスクはSubscription Keyで標準H3の受付・生成を確認済みです。実出力は1344×768・24fps・８秒で、AAC音声を含みました。CLIはこの実測native寸法を明示的に許容し、元pixelを保ちます。ゲームの16:9 viewportではaspect-coverで小さく上下をcropし、全frameの見切れを別途確認します。その他の誤比率を広く許す変更ではありません。音声はゲーム投入前に除去してください。
