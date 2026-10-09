# SilentのGodot用素材

[Issue #28](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/28) / [元デザインのユーザー承認](review-v05.md)。2026-10-09。Spine Editor・動画AIを使わない自律制作の委任に基づき、親が素材を採用した。**派生素材の個別ユーザー承認ではない。ゲーム内確認は未実施。**

## 素材

| 出力 | 内容 |
| --- | --- |
| `mod/assets/PopSpireWomen/art/silent/body.png` | 1024×1536 RGBA。承認絵から人物を分離し、角・外套・手足・短剣まで枠内へ収めた |
| `mod/assets/PopSpireWomen/art/silent/rig.json` | #26のschema 1。足元基準、顔・手・足・髪・外套のpixel座標。実ゲームで大きさと変形を調整する |
| `mod/assets/PopSpireWomen/art/silent/layers/eyes_closed.png` | 同canvasの瞬き用レイヤー。APIで閉眼にした領域だけをmaskに沿って残した |
| `mod/assets/PopSpireWomen/art/silent/select_background.png` | 2048×1152。人物・装備を含まない森と足場。選択画面で人物とは別に描く |

画像は全て `gpt-image-2 / high`、スキル付属CLIのImage API editで制作。ライブ呼出しは人物分離・瞬き・背景の３回。CLIの引数検査で `edit --max-attempts` が拒否された１回はAPIへ送信されていない。モデル変更や動画生成はしていない。キーは指定dotenvからそのプロセスへ渡し、表示・保存しない。CLIは課金usageを返していないため実請求額を推定で記録しない。

## 本人と描画の確認

可愛い人の顔、白髪と緑の瞳、緑の外套、頭蓋骨・角・背面の骨、短剣・毒瓶、短パンと巻き布を維持した。背景分離時に余白を確保し、元画像で画面外だった外套の端を補った。APIによる描き直しを含む派生なので、承認画像との画素一致は主張しない。元の承認済みPNGは変更していない。

単色マゼンタの指定に対し、実際の背景色にはわずかな変動があった。付属 `remove_chroma_key.py` のcorners自動採色（代表値 `#f703ee`）、soft matte閾値24/96、spill cleanupでalphaへ変換した。alpha bboxは `(32,25)-(968,1344)`、透明画素1,030,480、部分透明14,374。大きい背景残りや人物の欠落がないことを目視。細い髪の縁と最終背景上での見え方は描画検証で確認する。

瞬きは両目のmask内をAPIで編集し、closed-eye出力の該当領域だけを抽出した。maskを3px拡張・1.3pxぼかし、元bodyのalphaとの共通範囲に限定。手描きで目を加筆していない。背景や身体などmask外の再生成結果はレイヤーへ使っていない。

`hand_l`/`hand_r`と`foot_l`/`foot_r`は画像の左/右。短剣を持つ手は`hand_l`。`display_height=300`は暫定。元の骨格や武器の付着点との対応、攻撃・被弾・死亡等の変形、選択画面での構図は#26との統合後に検証する。全身の一枚meshでは大きな関節回転の隠れた部分を復元できないため、必要なら追加層へ分割する。

## 再現と来歴

- [人物分離の指示](../../../../art/prompts/silent/body-v01.txt) / [API記録](../../../../output/imagegen/silent/silent-body-v01-key.provenance.json) / [alpha変換・採用記録](../../../../output/imagegen/silent/silent-body-v01.provenance.json)
- [瞬きの指示](../../../../art/prompts/silent/blink-v01.txt) / [mask](../../../../art/prompts/silent/blink-v01-mask.png) / [API・レイヤー抽出記録](../../../../output/imagegen/silent/silent-blink-v01.provenance.json)
- [背景の指示](../../../../art/prompts/silent/select-background-v01.txt) / [API・採用記録](../../../../output/imagegen/silent/silent-select-background-v01.provenance.json)

各記録に入力・prompt・出力・変換のhash、寸法、API成否、採用範囲を残す。配布用body/backgroundは対応する出力PNGと同一bytes。PNGデコード・alpha・hash・入力不変・相対リンク・git diffを確認し、runtimeのProductionReadyとユーザー承認は別に扱う。
