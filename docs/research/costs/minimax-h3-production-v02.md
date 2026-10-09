# MiniMax H3 768Pの制作仕様 v0.2

確認日: **JST 2026-10-09**。対象は [Issue #49](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/49)。最新ユーザー指示「MiniMax H3 768pで生成しましょう」を、以前の動画AI見送り方針より優先する。５人の選択画面を各８秒で生成する初回を想定する。Spine Professionalを使わず、戦闘・商人・休憩は場面別姿勢とGodot同期、独立Osty/剣/Orb、ゲーム音・イベントを維持する。

この担当が完成させるのは公式仕様の確認とCLI。実API送信、アカウント確認、画像制作、ゲーム導入は行っていない。Silent v05はユーザー承認済み、他４人v02や新しい派生は親の委任に基づく制作採用であり、個別ユーザー承認へ読み替えない。[以前の費用比較](video-generation.md)は当時の仮定として残す。

## API契約

| 項目 | 今回使う値・確認結果 |
| --- | --- |
| create | `POST https://api.minimax.io/v2/video_generation` |
| model / resolution | **`MiniMax-H3` / `768P`**。大文字小文字をこの通り送る。H3 MaxやHailuoへの代替なし |
| duration | 整数4〜15秒。初回は **8** |
| 認証 | `Authorization: Bearer <MINIMAX_API_KEY>`。URLやpayloadにはキーを入れない |
| 入力 | 非空のtextと、`image_url: {url: ...}` の `first_frame` / `last_frame` |
| 16:9 | 始終フレーム方式は入力画像の比率を採用し `ratio=adaptive`。固定ratioを渡しても無視される。親が16:9画像を用意する |
| 画像location | 公開URL、`data:image/<小文字format>;base64,...`、`mm_file://{file_id}`。CLIはローカル画像からdata URIを作る |
| 画像・body | JPG/JPEG/PNG/WEBP/HEIC/HEIF、１枚30MB以内、各辺256〜5760px、w/h 0.4〜2.5。request全体64MB以内。prompt最大7000文字 |
| 始終と参照 | first/last各１枚まで。reference image/video/audio方式と混在不可 |

根拠: [公式create](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)、[生成ガイド](https://platform.minimax.io/docs/guides/video-generation)、[公式OpenAPIのContentItem詳細](https://platform.minimax.io/docs/api-reference/video/generation/api/v2-video-generation.json)。画像を同じ内容で両roleへ渡すことの禁止は見つからなかったが、同画像の実受付とシームレスloopは未検証。公開create schemaには `loop`、`seed`、出力fps、無音を保証する指定がなく、未定義の項目を追加しない。exactな768Pのpixel寸法・fpsも、今回読んだAPI契約では確定しない。

機械可読の [契約・placeholder request](../../../tools/video/h3-api-contract.json) を実装と一緒に保存した。親への早期共有は `/tmp/sts2-motion-v02/h3-api-contract.json`。同じ画像を開始・終端として渡し、プロンプトで戻る演技を指示する制作仮説と、APIで保証された仕様を区別して記載している。

## 状態・download・返却期限

createの返却は `task_id`。`GET https://api.minimax.io/v2/query/video_generation/{task_id}` が `task` を返し、状態は `queued / running / succeeded / failed / cancelled`。成功時の動画は `task.content.url` をGETする。旧v1のfile_idをfile-managementへ渡す手順に置き換えない。`task.usage` の秒・入力枚数等は返された分だけ記録し、課金usageを推測で埋めない。[公式query](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)、[生成手順](https://platform.minimax.io/docs/guides/video-generation)。

queryと [task一覧](https://platform.minimax.io/docs/api-reference/video-generation-v2-list) の対象は **直近７日**。download URLは期限付きで、切れたらqueryし直して新しいURLを取得する。正確なURLの有効秒数は未確認。７日を署名URLのTTLと呼ばない。受け取ったURLはメモリ内だけで使い、認証headerをCDNへ転送せず、成功後は速やかにローカル保存する。[公式queryのVideoTaskContent](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)。

H3は音も含む映像制作に対応するが、今回のschemaで `generate_audio=false` 等は確認できない。無音のプロンプトは保証ではないので、download後のstream確認と、必要な音声除去を納品工程へ含める。音なしの料金割引、native stereoの必須channel数、透過alpha動画は保証しない。[公式H3機能](https://platform.minimax.io/docs/guides/video-prompt)、[create schema](https://platform.minimax.io/docs/api-reference/video/generation/api/v2-video-generation.json)。

## 初回の費用と再試行

| 仮定 | 公開従量料金からの見積 |
| --- | ---: |
| H3 768P 出力 | **$0.08/秒** |
| １人８秒、始終画像２枚、動画参照なし | **$0.64** |
| ５人×８秒の初回 | **$3.20** |
| 同条件で１人を追加１take | +$0.64 |
| 同条件で５人を追加１takeずつ | +$3.20 |

画像は最初の５枚が無料、追加１枚$0.04。動画参照は768Pでは入力秒にも$0.08、音声参照は無料。今回の２画像・動画参照なし・Context-IRなしなら、上表に追加入力料金を見込まない。税、通信・加工・レビュー、再生成や2K化を含まず、請求の実測ではない。[公式料金](https://platform.minimax.io/docs/pricing/overview)。

H3はVideo Packagesの対象外で、従量APIを使う。料金ページの「生成失敗やsecurity reviewはvideo pointsを引かない」はPackagesの規則であり、H3従量APIの返金保証へ流用しない。今回読んだ公式create/query/pricing/guideからH3失敗時の返金・非課金規則は確認できなかった。再試行の追加taskは親が採否・課金を判断する。[公式料金とpackage対象](https://platform.minimax.io/docs/pricing/overview)。

createの公開仕様に冪等キーはない。CLIは送信前のローカル予約、fingerprint、take ID、ファイルロックで重複POSTを防ぐ。timeout、5xx、応答不正、task ID不明を自動で再送せず、既知taskのpollを再開する。ID不明は親が送信時刻とtask一覧から照合して `attach` できる。別state-dir・予約削除・新take指定をまたぐ重複防止や、外部APIでの冪等性を保証するものではない。

## CLIと検証の範囲

[実行方法](../../../tools/video/README.md) と [実装](../../../tools/video/h3.py)。`submit / status / download` を分離し、`attach` はID復旧のGETだけ。request fingerprint、入力hash、要求model/768P/尺、task IDと日時、返却された安全な状態・数値usage、出力hashと `ffprobe` 情報を保存する。prompt本文、base64、キー、生レスポンス、失敗message、署名URLは保存・表示しない。env-fileは任意で、当該キーをliteralとして読む。

通常検証は [tests/video](../../../tests/video/test_h3.py)。mockでpayload/auth、並行submit、POST前の永続化、timeout・強制終了予約・中断からの重複防止、poll再開、失敗、taskの不一致、URL失効後のdownload再開、出力検証と秘密の非出力を確認した。無地のsynthetic PNGと８秒MP4で実際の `ffprobe`、全frame読取り、音声stream記録も確認する。素材はテスト用で、H3生成・５人の外観・ゲーム表示の実証ではない。通常検証記録は [validation.json](../../../tests/video/validation.json)。validatorは指定通り０回。

未確認は、親のアカウントでのH3利用・残高、同画像始終のAPI受付、実動画の寸法/fps/音声、loop接続と本人の維持、失敗時の課金、ゲームでの表示と場面別の同期。ツール完成と５人の動画完成を混同しない。

## 一次資料の固定

HTMLの上記ページと、公式が提供するMarkdown/OpenAPI本文を実読した。以下は2026-10-09 UTC 07:20〜07:37取得の本文SHA-256で、完全URL・取得日時・bytesは [契約のsource_reads](../../../tools/video/h3-api-contract.json) にある。未公開APIや第三者の料金を事実の根拠にしていない。

| 公式本文 | SHA-256 |
| --- | --- |
| [create.md](https://platform.minimax.io/docs/api-reference/video-generation-v2-create.md) | `9f68fada266f3d1c929ff96fe4fa92741eba5d0fd29b8647eb5e4e07daf507f9` |
| [query.md](https://platform.minimax.io/docs/api-reference/video-generation-v2-query.md) | `bc91317855006307ddfc104d777736fa805c0a5d7df91f95ebfb4f9435e0b270` |
| [pricing.md](https://platform.minimax.io/docs/pricing/overview.md) | `6e7854afb844dee860a2d19d02cee415d3f2d78b1be9e1c6a840520cda83e909` |
| [guide.md](https://platform.minimax.io/docs/guides/video-generation.md) | `d7144e082b69e4397b5aa4ec345d8f96cf71ed4f3d04b45dae426701f9f77f96` |
| [OpenAPI JSON](https://platform.minimax.io/docs/api-reference/video/generation/api/v2-video-generation.json) | `6066ba7f7afb02360ab54463b3c95a00967d203376527406fa13d90b227ba038` |
| [H3機能.md](https://platform.minimax.io/docs/guides/video-prompt.md) | `8e1d30cec9f4b6e1fa6b9e0594b713e1677c98bccafa66b8dc3b8472a4514b35` |
| [list.md](https://platform.minimax.io/docs/api-reference/video-generation-v2-list.md) | `a71ef1865c592347407e621ee8d1cc305ded5a93e5d904df97f70c44cf6b0f8f` |
