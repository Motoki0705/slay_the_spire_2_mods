# MiniMax H3 768Pの制作仕様 v0.2

確認日: **JST 2026-10-09**。対象は [Issue #49](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/49) のH3 CLIと、[Issue #57](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/57) のcredits調査・client対応。最新ユーザー指示「MiniMax H3 768pで生成しましょう」を、以前の動画AI見送り方針より優先する。５人の選択画面を各８秒で生成する初回を想定する。Spine Professionalを使わず、戦闘・商人・休憩は場面別姿勢とGodot同期、独立Osty/剣/Orb、ゲーム音・イベントを維持する。本番受付・動画生成の完了は [Issue #48](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/48) で追跡する。

この担当が完成させるのは公式仕様の確認とCLI。実API送信、キー・既存envファイルの参照、アカウント確認、画像制作、ゲーム導入は行っていない。テストだけで用いる偽のキー・dotenv・無地の素材は本番資源と分ける。Silent v05はユーザー承認済み、他４人v02や新しい派生は親の委任に基づく制作採用であり、個別ユーザー承認へ読み替えない。[以前の費用比較](video-generation.md)は当時の仮定として残す。

## API契約

| 項目 | 今回使う値・確認結果 |
| --- | --- |
| create | `POST https://api.minimax.io/v2/video_generation` |
| model / resolution | **`MiniMax-H3` / `768P`**。大文字小文字をこの通り送る。H3 MaxやHailuoへの代替なし |
| duration | 整数4〜15秒。初回は **8** |
| 認証 | 選択したキーを `Authorization: Bearer <token>` に設定。paygは `MINIMAX_API_KEY`、creditsは `MINIMAX_SUBSCRIPTION_KEY`。URLやpayloadにはキーを入れない |
| 入力 | 非空のtextと、`image_url: {url: ...}` の `first_frame` / `last_frame` |
| 16:9 | 始終フレーム方式は入力画像の比率を採用し `ratio=adaptive`。固定ratioを渡しても無視される。親が16:9画像を用意する |
| 画像location | 公開URL、`data:image/<小文字format>;base64,...`、`mm_file://{file_id}`。CLIはローカル画像からdata URIを作る |
| 画像・body | JPG/JPEG/PNG/WEBP/HEIC/HEIF、１枚30MB以内、各辺256〜5760px、w/h 0.4〜2.5。request全体64MB以内。prompt最大7000文字 |
| 始終と参照 | first/last各１枚まで。reference image/video/audio方式と混在不可 |

根拠: [公式create](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)、[生成ガイド](https://platform.minimax.io/docs/guides/video-generation)、[公式OpenAPIのContentItem詳細](https://platform.minimax.io/docs/api-reference/video/generation/api/v2-video-generation.json)。画像を同じ内容で両roleへ渡すことの禁止は見つからなかったが、同画像の実受付とシームレスloopは未検証。公開create schemaには `loop`、`seed`、出力fps、無音を保証する指定がなく、未定義の項目を追加しない。exactな768Pのpixel寸法・fpsも、今回読んだAPI契約では確定しない。

機械可読の [契約・placeholder request](../../../tools/video/h3-api-contract.json) と [creditsコマンド契約](../../../tools/video/h3-credit-client-contract.json) を実装と一緒に保存した。credits対応の親への早期共有は `/tmp/sts2-motion-v02/h3-credit-client-contract.json`。同じ画像を開始・終端として渡し、プロンプトで戻る演技を指示する制作仮説と、APIで保証された仕様を区別して記載している。

## 状態・download・返却期限

createの返却は `task_id`。`GET https://api.minimax.io/v2/query/video_generation/{task_id}` が `task` を返し、状態は `queued / running / succeeded / failed / cancelled`。成功時の動画は `task.content.url` をGETする。旧v1のfile_idをfile-managementへ渡す手順に置き換えない。`task.usage` の秒・入力枚数等は返された分だけ記録し、課金usageを推測で埋めない。[公式query](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)、[生成手順](https://platform.minimax.io/docs/guides/video-generation)。

queryと [task一覧](https://platform.minimax.io/docs/api-reference/video-generation-v2-list) の対象は **直近７日**。download URLは期限付きで、切れたらqueryし直して新しいURLを取得する。正確なURLの有効秒数は未確認。７日を署名URLのTTLと呼ばない。受け取ったURLはメモリ内だけで使い、認証headerをCDNへ転送せず、成功後は速やかにローカル保存する。[公式queryのVideoTaskContent](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)。

H3は音も含む映像制作に対応するが、今回のschemaで `generate_audio=false` 等は確認できない。無音のプロンプトは保証ではないので、download後のstream確認と、必要な音声除去を納品工程へ含める。音なしの料金割引、native stereoの必須channel数、透過alpha動画は保証しない。[公式H3機能](https://platform.minimax.io/docs/guides/video-prompt)、[create schema](https://platform.minimax.io/docs/api-reference/video/generation/api/v2-video-generation.json)。

## 初回の費用と再試行

| 仮定 | 公開従量価格 | 対象creditsの換算見積 |
| --- | ---: | ---: |
| H3 768P 出力 | **$0.08/秒** | **80 credits/秒** |
| １人８秒、始終画像２枚、動画参照なし | **$0.64** | **640 credits** |
| ５人×８秒の初回 | **$3.20** | **3,200 credits** |
| 同条件で１人を追加１take | +$0.64 | +640 credits |
| 同条件で５人を追加１takeずつ | +$3.20 | +3,200 credits |

画像は最初の５枚が無料、追加１枚$0.04（40 credits相当）。動画参照は768Pでは入力秒にも$0.08（80 credits相当）、音声参照は無料。今回の２画像・動画参照なし・Context-IRなしなら、上表に追加入力料金を見込まない。換算は **1,000 credits=$1**。税、通信・加工・レビュー、再生成や2K化を含まず、請求や残高の実測ではない。[公式料金](https://platform.minimax.io/docs/pricing/overview)、[credits換算のFAQ](https://platform.minimax.io/docs/m-plan/faq)。

H3はHailuo用Video Packagesの対象外。PackagesのpointsとM Planのcreditsは別であり、H3がPackages対象外でもcredits対象外とは限らない。料金ページの「生成失敗やsecurity reviewはvideo pointsを引かない」はPackagesの規則であり、H3の従量・creditsでの返金保証へ流用しない。今回確認した資料からH3失敗時の返金・非課金規則は確定できなかった。再試行の追加taskは親が採否・課金を判断する。[公式料金とpackage対象](https://platform.minimax.io/docs/pricing/overview)。

## Creditsの経路と留保

現行 [M Plan FAQ](https://platform.minimax.io/docs/m-plan/faq) はcredit packの対象に **H3** を含め、M Plan契約がなくてもcredit pack単独で利用できると説明する。Subscription Keyは契約枠と対象creditsを使い、通常の従量API Keyは現金残高を使う。両キーは互換ではない。契約枠とcreditsの双方が対象なら契約枠が先に使われ、購入creditsの有効期限は１年。これは公式の一般仕様で、この担当は個別アカウント・保有credits・実課金を確認していない。

[API Overview](https://platform.minimax.io/docs/api-reference/api-overview) も購入credits用のSubscription Keyを通常のAPI Keyと区別する。公式SDKの [動画処理](https://github.com/MiniMax-AI/cli/blob/main/src/sdk/video/index.ts) はV2 requestを [共通endpoint](https://github.com/MiniMax-AI/cli/blob/main/src/client/endpoints.ts) へ渡し、[HTTP認証](https://github.com/MiniMax-AI/cli/blob/main/src/client/http.ts) は選択済みcredentialをBearer headerへ設定する。このコードとFAQから、**同じH3 V2 endpointへSubscription Keyを設定する利用経路と推定した**。CLIは `--billing credits` で `MINIMAX_SUBSCRIPTION_KEY` だけを使い、API本文に課金fieldを追加しない。

留保として、[動画createページ](https://platform.minimax.io/docs/api-reference/video-generation-v2-create) はH3利用時に「Pay-as-you-go API」を選ぶ注意書きを残している。FAQのH3 credits対応と完全には整合せず、Subscription Keyでの **標準H3 / 768Pの実受付は未確認**。CLI・mock検証が通っても生成成功とはしない。同ページのHTTP402/provider1008は残高不足を表すが、従量キーでの拒否をcredits方式の利用不可の証拠へ読み替えない。H3-Maxへの無断切替もしない。

createの公開仕様に冪等キーはない。CLIは送信前のローカル予約、fingerprint、take ID、ファイルロックで重複POSTを防ぐ。timeout、5xx、応答不正、task ID不明を自動で再送せず、既知taskのpollを再開する。ID不明は親が送信時刻とtask一覧から照合して `attach` できる。fingerprintは課金方式・キーを含めず、拒否済みtakeをキー変更だけで再POSTしない。同じtakeで方式を変えると `billing_mismatch` で停止するので、creditsでの新要求は親が同じstate-dirで `--take-id credits-take-01` 等を明示する。別state-dir・予約削除・新take指定をまたぐ重複防止や、外部APIでの冪等性を保証するものではない。

## CLIと検証の範囲

[実行方法](../../../tools/video/README.md) と [実装](../../../tools/video/h3.py)。`submit / status / download` を分離し、`attach` はID復旧のGETだけ。`submit --billing credits|payg` の既定はpayg。新jobには `billing: {mode, key_env}` と80 credits/秒・総creditsの換算見積を保存し、APIへ未定義fieldを送らない。`status / download / attach` はjobの方式を既定とし、明示した別方式はキー読取・HTTPより前に拒否する。旧jobで課金記録がない場合はpaygと解釈し、壊れた方式や不一致の変数名は拒否する。選択した変数の既存環境を優先し、未設定なら任意のenv-fileから同じ変数だけをliteralとして読む。別方式へfallbackしない。dry-runはキー・env-fileを読まない。

request fingerprint、入力hash、要求model/768P/尺、task IDと日時、返却された安全な状態・数値usage、出力hashと `ffprobe` 情報を保存する。prompt本文、base64、キー、生レスポンス、失敗message、署名URLは保存・表示しない。使用変数名と課金方式の記録は非秘密の固定値だけに限る。

通常検証は [tests/video](../../../tests/video/test_h3.py)。元の32件を維持し、credits用の10件を加えた **42件が合格**。mockでpayload/auth、並行submit、POST前の永続化、timeout・強制終了予約・中断からの重複防止、poll再開、失敗、taskの不一致、URL失効後のdownload再開、出力検証と秘密の非出力を確認した。追加分はSubscription Key選択、方式別dotenv、fallback拒否、全再開コマンドでの方式保持・不一致拒否、旧job互換、壊れた課金記録の拒否、402後の新take、poll中の方式変更拒否、Subscription Keyを含むエラーの非出力を確認する。無地のsynthetic PNGと８秒MP4で実際の `ffprobe`、全frame読取り、音声stream記録も確認した。素材はテスト用で、H3生成・５人の外観・ゲーム表示の実証ではない。通常検証記録は [validation.json](../../../tests/video/validation.json)。validatorは指定通り０回。

未確認は、Subscription Keyでの標準H3/768P受付、同画像始終のAPI受付、実動画の寸法/fps/音声、loop接続と本人の維持、失敗時の課金、ゲームでの表示と場面別の同期。ツール完成と５人の動画完成を混同しない。

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

Issue #57では提示済みの調査を引き継ぎ、上記create/pricing、[M Plan FAQ](https://platform.minimax.io/docs/m-plan/faq)、[API Overview](https://platform.minimax.io/docs/api-reference/api-overview)、公式SDKの動画・endpoint・HTTP認証のURLと本文を再確認した。追加の取得日時・本文hashは同じ [source_reads](../../../tools/video/h3-api-contract.json) に追記し、前回の取得記録を残す。個人の画面・請求履歴・アカウント情報は参照・掲載していない。
