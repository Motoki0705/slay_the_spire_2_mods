# 動画費用モデルの証拠と再計算

調査日: JST 2026-10-09。ゲーム入力は既存のv0.107.1 / 59260271の[動作棚卸し](../../motion/inventory.md)。生成API呼出し・課金・素材upload・ゲーム起動は0。

| ファイル | 用途 |
| --- | --- |
| `provider-specs.json` | 確認した公式モデルID・料金・解像度・制限。根拠URL付き |
| `source-reads.json` | 公開一次資料9件の取得日時・HTTP status・本文hash。BytePlusは文書の更新日時とbody hashも固定 |
| `read_official_docs.py` | 公式ドキュメントのGETのみ。料金行が変化した場合はassertで停止。全文記事は保存しない |
| `h3-public-sample-probe.json` | MiniMax公式API資料の公開sampleのffprobe結果。自分の生成結果や全API profileの保証とはしない |
| `production-policy.json` | 1920×1080基準、前後余白、試行倍率、sprite canvas、シナリオ範囲 |
| `assets.json` | 84候補のexact animation名・元秒数・元scene・素材単位 |
| `asset-costs.csv` | 84候補×2モデル。元尺、生成尺/分割本数、納品canvas、生成frame、単価計算を別列で保存 |
| `scenario-totals.csv / .json` | A/B/C × モデル × 1/3/5試行の本数・秒・token・USD |
| `character-totals.csv` | キャラ別の本数・生成task・秒・金額。Osty/剣/orbはowner集計に含み、詳細CSVでは別entity |
| `variant-totals.csv` | 選択を6秒loopへ再設計する案とIronclad4動作の比較案 |
| `static-size-evidence.json` | 元setup/export boundsとVisuals scaleの計算、scene行番号。実測pixelや全pose範囲ではない |
| `input-hashes.json` | 計算に使った棚卸し・scene・設定・スクリプトのSHA-256 |
| `validation.json` | 算術・対象数の照合。ゲーム互換性や生成品質の評価ではない |

作業dir `/home/kamimura/projects/slay_the_spire_2`。オフライン再計算:

```bash
python3 docs/research/costs/evidence/build_cost_model.py
```

公式資料を再確認する場合のみ、別に実行する:

```bash
python3 docs/research/costs/evidence/read_official_docs.py
```

BytePlusの一般的なweb readerには本文が出ない。公開HTMLの `window._ROUTER_DATA` → `curDoc.MDContent` を読む。これは公開文書の読み取りであり、ログイン/API keyや生成APIを使わない。英語版の料金文書は更新日時2026-10-08T13:17:02Z、仕様文書は2026-09-28T06:48:10Z。検索cacheに古い別モデルの料金や720p制限が混ざるため、最新の同じサービス・モデルの行を優先する。

金額は画像2枚・動画参照0秒の標準ケース。試行1/3/5は制作計画上の仮定で、成功率の実測ではない。Seedance金額は公式のtoken推定式に基づき、実請求では `usage.completion_tokens` を使う。H3の768P exact pixel profileは未確認で、CSVの768×1024等は構図を準備するための名目値。実生成後にframe寸法・fps・尺・audioを検査する。

最大clip尺による分割を含むため、H3はBで35素材/36task、Cで84素材/88taskになる。分割の境界や透明化が成功することを確認したモデルではない。色/照明/部位絵/rig/整音/合成/手作業費、Spine Editor license、税、保存・通信費はこの動画費用へ混ぜていない。
