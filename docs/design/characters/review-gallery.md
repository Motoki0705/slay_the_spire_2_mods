# ５人の現行デザインと制作素材

[開発の案内](../../development/README.md) / [Issue地図](../../development/issue-map.md) / [制作素材 v0.1](production-assets.md) / [全体Issue #1](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/1)

確認日: **2026-10-09（JST）**。**Silent v05は基準デザインのユーザー承認済み。他４人v02は完成までの自律制作の委任に基づく制作採用。** デザインPR #12 / #13 / #15 / #17 / #16と、実装用素材の [PR #35](https://github.com/Motoki0705/slay_the_spire_2_mods/pull/35) はmain統合済み。旧４人v01を現在のレビュー待ちとして案内しない。

ユーザー承認は [Silent v05の対象画像・hash・承認範囲](silent/review-v05.md#ユーザー承認2026-10-09) に限る。他４人や背景分離・閉じ目・休憩姿・UI・rigを個別ユーザー承認済みとは記録しない。人物像はMOD用の翻案であり、公式設定を追加するものではない。[キャラ方針](review-v03.md) / [４人の改訂案](slender-revision-brief.md)。

## 現行５人を比較する

クリックで原寸PNGを開く。レビュー場面の画像は**制作commitの完全SHA**で固定し、実装用RGBA body・分割層とは区別する。単独キャラv02と、不採用の５人集合案 `lineup-v02.png` は別の版。

| Ironclad v02 | Silent v05 | Regent v02 | Necrobinder v02 | Defect v02 |
| --- | --- | --- | --- | --- |
| [![Ironclad v02 委任に基づく制作採用][ironclad-current-image]][ironclad-current-image] | [![Silent v05 基準デザインのユーザー承認済み][silent-image]][silent-image] | [![Regent v02 委任に基づく制作採用][regent-current-image]][regent-current-image] | [![Necrobinder v02 委任に基づく制作採用][necrobinder-current-image]][necrobinder-current-image] | [![Defect v02 委任に基づく制作採用][defect-current-image]][defect-current-image] |
| [PR #12][ironclad-pr] / [v02記録](ironclad/review-v02.md) / [制作](ironclad/production.md) | [PR #13][silent-pr] / [v05承認](silent/review-v05.md) / [制作](silent/production.md) | [PR #15][regent-pr] / [v02記録](regent/review-v02.md) / [制作](regent/production.md) | [PR #17][necrobinder-pr] / [v02記録](necrobinder/review-v02.md) / [制作](necrobinder/production.md) | [PR #16][defect-pr] / [v02記録](defect/review-v02.md) / [制作](defect/production.md) |

| キャラ | 現行画像を固定した制作commit | プロンプト・来歴 |
| --- | --- | --- |
| Ironclad | [`fbfda83fd5e5ef144bd6c60340d43af9aeb75df8`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/fbfda83fd5e5ef144bd6c60340d43af9aeb75df8) | [v02編集指示](../../../art/prompts/ironclad/ironclad-v02-edit.txt) / [v02来歴](../../../output/imagegen/ironclad/ironclad-v02.provenance.json) |
| Silent | [`6cbe67515274a24cb46761ae16aae9eed28cc4ac`][silent-commit] | [編集指示][silent-prompt-1] / [最終版来歴][silent-provenance] |
| Regent | [`a3dcbc88cc7344a7a2289071fd1fed7d3ac55d3b`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/a3dcbc88cc7344a7a2289071fd1fed7d3ac55d3b) | [v02編集指示](../../../art/prompts/regent/regent-v02-edit.txt) / [v02来歴](../../../output/imagegen/regent/regent-v02.provenance.json) |
| Necrobinder | [`9fc85a45dffbcf902220b490f192d2d014f290af`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/9fc85a45dffbcf902220b490f192d2d014f290af) | [v02編集指示](../../../art/prompts/necrobinder/necrobinder-v02-edit.txt) / [v02来歴](../../../output/imagegen/necrobinder/necrobinder-v02.provenance.json) |
| Defect | [`54de2ea8d76082df8af9d548e2e5d3b2e2a335c8`](https://github.com/Motoki0705/slay_the_spire_2_mods/commit/54de2ea8d76082df8af9d548e2e5d3b2e2a335c8) | [v02編集指示](../../../art/prompts/defect/defect-v02-edit.txt) / [v02来歴](../../../output/imagegen/defect/defect-v02.provenance.json) |

## 採用理由と人物の区別

ユーザーの「サイレントはOKです。その他のキャラはスタイルが良すぎます」「華奢な感じが魅力的」を反映した。Silentの顔・体型・衣装を４人へ複製せず、身体と装備、本人の行動の関係を改訂した。採否・統合は委任範囲で親が判断し、各画像への追加回答待ちを必須にしていない。

| キャラ | 現行の制作判断 | 残す差分・限界 |
| --- | --- | --- |
| Ironclad | 短く薄い装甲、細い胴・腕、剣を支えて掌の炎を抑えようとする顔と指。身体の厚みではなく装備の荷重と本人の意志で兵士を描く | 胸腰のフィットと脚の縦比率は一部残る。呼吸・炎制御の成功は静止画では証明できない |
| Silent | 可愛い人の顔、狩りに集中する視線、白髪・緑の瞳・衣服の澄んだ光を保つ | v05の膝下の革バンド省略は承認時にも残った差分。休憩画の足元の衣装差分は [制作素材](production-assets.md#検証と限界) に記録 |
| Regent | 小さい成人の身体と余る王衣、指図する手、玉座と運び手の対比。本人と玉座/運び手を実装用には分離 | 運び手への視線や揺れへの慌てた応答は静止画では控えめ。hoverは人物・衣装を交換しない独立層 |
| Necrobinder | さらに細くするより、強い腰の絞りと巻き布を緩め、長衣を直線的に落とす。相棒への合図・小さな笑みと眉の緊張を保持 | 概念画のOstyが解剖学的な左手かは未確定。実装bodyへOstyを焼き込まず、元の独立制御を使う |
| Defect | 細い腕・手首・分節した足と、補修中の前腕だけの量感を対比。非対称の座位、工具を止める好奇心を保持 | 驚きの表情、細かい工具/留め具、大きな関節回転は追加確認事項。bodyと休憩は同じ座位を利用 |

華奢さの評価は目視による制作判断で、身体寸法や「露出15%」を厳密に測定した結果ではない。Silentの露出はv04の調整を保持する指定で、v05からさらに15%増やす要求ではない。「透明感」は肌・髪・瞳・布の光と色を指し、背景alpha透過とは別。

## 実装用素材と確認範囲

[制作素材 v0.1](production-assets.md) が現在の入力・再組立・来歴の入口。５人の本体・背景・まばたき・休憩姿、20用途別rig、５選択scene、25UI PNGと５icon sceneをPCK接続へ渡している。Regentの本人・玉座/運び手と [７星座hover](../../development/regent-overlay.md) を分け、Osty・Sovereign Blade・Orbは独立制御を保つ。

v02と初期surfaceのAPI制作は過去の実行記録を保持。API課金エラー後に不足した４背景・４閉じ目は、ユーザー指定のCodex内蔵画像生成で制作した。これらのprompt・参照crop・実出力・hashと採用範囲は制作素材文書へ戻って確認する。取得できない生成モデル・画質設定・課金量を推測で補わない。Spine Professional・動画生成AIは今回使用しない。

親のQA共有（2026-10-09）では元mainの通常PCKロード、５人分の選択アイコンと選択背景の表示、Ironcladのtop portraitとSTRIKE使用（敵HP **43→37**、overlay **idle_loop→attack→idle_loop**）を確認。選択人物の見切れはproduction descriptorで修正済み。**全５人の実戦・商人・休憩・状態遷移、保存/co-op・競合・性能・通しプレイの合格を意味しない。** 実機QAは [#11](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/11)、利用・設定・削除は [PCK手順](../../development/pck-only.md)。本案内の更新で画像生成やゲーム起動は行っていない。

## 旧候補と固定した初回制作記録

旧４人v01は「スタイルが良すぎる」とのレビューで要修正となった編集元。下記の画像・PR headは**初回制作時の版**で、現在のPR headや採用画像へ自動では切り替わらない。PRはその後v02を追加して統合された。旧レビュー本文の未承認・draft・未制作は当時の状態として読む。

| 旧候補 | 当時の人物像・観察 | 旧記録 |
| --- | --- | --- |
| [Ironclad v01][ironclad-image] | 剣を支え掌の炎を抑える女性兵士。装甲の量感と体型の誇張をv02で改訂 | [初回レビュー][ironclad-review] |
| Silent v05（現行基準） | 最終版の承認は上記の対象・hashに限る。`attempt1`や編集元v04へ広げない。革バンドの差分を保持 | [固定制作記録][silent-review] |
| [Regent v01][regent-image] | 指図する星の継承者と運び手。体型、従者への視線と慌てる表情が比較事項だった | [初回レビュー][regent-review] |
| [Necrobinder v01 corrected][necrobinder-image] | Ostyへの合図と信頼。５指が読める修正版だが、掌面/手背・左手条件は未確認だった | [初回レビュー][necrobinder-review] |
| [Defect v01][defect-image] | 修繕を止めオーブを見る。オーブが縦にまとまり、表情は納得より驚きが強いという観察 | [初回レビュー][defect-review] |

初回記録の画像APIは **`gpt-image-2 / high / 1024×1536 / RGB PNG`**。制作エージェントのmodel/effort/tierとは別の情報。API成否・入力の役割・hash・目視・承認状態を原記録から確認する。

| キャラ | 制作担当 | 固定した初回PR head commit | プロンプト・来歴 |
| --- | --- | --- | --- |
| Ironclad | `art-ironclad` | [`87ce8c21536fac2c2d1ce360e513fddb7e4e296d`][ironclad-commit] | [初回プロンプト][ironclad-prompt-0] / [来歴・hash][ironclad-provenance] |
| Silent | `art-silent` | [`6cbe67515274a24cb46761ae16aae9eed28cc4ac`][silent-commit] | [初回プロンプト][silent-prompt-0] / [修正プロンプト][silent-prompt-1] / [来歴・hash][silent-provenance] |
| Regent | `art-regent` | [`4f97a7a700cfb42e9b1435b6f8049d9b48fb75af`][regent-commit] | [初回プロンプト][regent-prompt-0] / [来歴・hash][regent-provenance] |
| Necrobinder | `art-necrobinder` | [`060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31`][necrobinder-commit] | [初回プロンプト][necrobinder-prompt-0] / [修正プロンプト][necrobinder-prompt-1] / [来歴・hash][necrobinder-provenance] |
| Defect | `art-defect` | [`f033dd6b8f7cb0de6c6d0b1db43ab42cdd9036a8`][defect-commit] | [初回プロンプト][defect-prompt-0] / [来歴・hash][defect-provenance] |

初回案に相棒・武器・Orbを含む静止場面があっても、ゲームでの独立制御を確認した素材ではない。Defectの代表３種のOrbを原作の全種類の網羅とは扱わない。Silentの来歴に残る「未承認」は生成当時の履歴で、現在の承認は上の承認節を参照する。

５人集合案 [v0.1の不採用記録](archive/rejected-v01.md) / [v0.2の不採用記録](archive/rejected-v02.md) は履歴として保ち、現行の制作見本にしない。Silent v04は編集元で、旧版・編集元・明示的な不採用を同じ意味にしない。原作の根拠は [キャラ調査](../../research/characters/README.md) / [参照画像索引](../../../art/references/README.md)。

## 更新するとき

比較画像・完全commit SHA・レビュー・全文prompt・来歴/hash・承認/制作採用・未確認範囲を一緒に更新し、[Issue地図](../../development/issue-map.md) と照合する。新しい生成成功やPR mergeをユーザー承認へ読み替えない。委任による採用はその判断者・理由を残し、個別承認を求める新しい指示がなければ制作を継続する。

[文書の拡張の考え方](../../README.md#拡張を判断する考え方) に沿い、初回v01比較から現行v02/制作素材へ入口を切り替えた理由と旧リンクを保つ。

[ironclad-current-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/fbfda83fd5e5ef144bd6c60340d43af9aeb75df8/output/imagegen/ironclad/ironclad-v02.png
[regent-current-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/a3dcbc88cc7344a7a2289071fd1fed7d3ac55d3b/output/imagegen/regent/regent-v02.png
[necrobinder-current-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/9fc85a45dffbcf902220b490f192d2d014f290af/output/imagegen/necrobinder/necrobinder-v02.png
[defect-current-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/54de2ea8d76082df8af9d548e2e5d3b2e2a335c8/output/imagegen/defect/defect-v02.png

[ironclad-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/87ce8c21536fac2c2d1ce360e513fddb7e4e296d/output/imagegen/ironclad/ironclad-v01.png
[ironclad-pr]: https://github.com/Motoki0705/slay_the_spire_2_mods/pull/12
[ironclad-issue]: https://github.com/Motoki0705/slay_the_spire_2_mods/issues/3
[ironclad-review]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/87ce8c21536fac2c2d1ce360e513fddb7e4e296d/docs/design/characters/ironclad/review-v01.md
[ironclad-commit]: https://github.com/Motoki0705/slay_the_spire_2_mods/commit/87ce8c21536fac2c2d1ce360e513fddb7e4e296d
[ironclad-prompt-0]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/87ce8c21536fac2c2d1ce360e513fddb7e4e296d/art/prompts/ironclad-v01.txt
[ironclad-provenance]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/87ce8c21536fac2c2d1ce360e513fddb7e4e296d/output/imagegen/ironclad/ironclad-v01.provenance.json

[silent-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/6cbe67515274a24cb46761ae16aae9eed28cc4ac/output/imagegen/silent/silent-v05.png
[silent-pr]: https://github.com/Motoki0705/slay_the_spire_2_mods/pull/13
[silent-issue]: https://github.com/Motoki0705/slay_the_spire_2_mods/issues/2
[silent-review]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/6cbe67515274a24cb46761ae16aae9eed28cc4ac/docs/design/characters/silent/review-v05.md
[silent-commit]: https://github.com/Motoki0705/slay_the_spire_2_mods/commit/6cbe67515274a24cb46761ae16aae9eed28cc4ac
[silent-prompt-0]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/6cbe67515274a24cb46761ae16aae9eed28cc4ac/output/imagegen/silent/silent-v05.attempt1.prompt.txt
[silent-prompt-1]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/6cbe67515274a24cb46761ae16aae9eed28cc4ac/art/prompts/silent-v05-edit.txt
[silent-provenance]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/6cbe67515274a24cb46761ae16aae9eed28cc4ac/output/imagegen/silent/silent-v05.provenance.json

[regent-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/4f97a7a700cfb42e9b1435b6f8049d9b48fb75af/output/imagegen/regent/regent-v01.png
[regent-pr]: https://github.com/Motoki0705/slay_the_spire_2_mods/pull/15
[regent-issue]: https://github.com/Motoki0705/slay_the_spire_2_mods/issues/4
[regent-review]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/4f97a7a700cfb42e9b1435b6f8049d9b48fb75af/docs/design/characters/regent/review-v01.md
[regent-commit]: https://github.com/Motoki0705/slay_the_spire_2_mods/commit/4f97a7a700cfb42e9b1435b6f8049d9b48fb75af
[regent-prompt-0]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/4f97a7a700cfb42e9b1435b6f8049d9b48fb75af/art/prompts/regent-v01.txt
[regent-provenance]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/4f97a7a700cfb42e9b1435b6f8049d9b48fb75af/output/imagegen/regent/regent-v01.provenance.json

[necrobinder-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31/output/imagegen/necrobinder/necrobinder-v01.corrected.png
[necrobinder-pr]: https://github.com/Motoki0705/slay_the_spire_2_mods/pull/17
[necrobinder-issue]: https://github.com/Motoki0705/slay_the_spire_2_mods/issues/5
[necrobinder-review]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31/docs/design/characters/necrobinder/review-v01.md
[necrobinder-commit]: https://github.com/Motoki0705/slay_the_spire_2_mods/commit/060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31
[necrobinder-prompt-0]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31/art/prompts/necrobinder-v01.txt
[necrobinder-prompt-1]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31/output/imagegen/necrobinder/necrobinder-v01.correction.txt
[necrobinder-provenance]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31/output/imagegen/necrobinder/necrobinder-v01.provenance.json

[defect-image]: https://raw.githubusercontent.com/Motoki0705/slay_the_spire_2_mods/f033dd6b8f7cb0de6c6d0b1db43ab42cdd9036a8/output/imagegen/defect/defect-v01.png
[defect-pr]: https://github.com/Motoki0705/slay_the_spire_2_mods/pull/16
[defect-issue]: https://github.com/Motoki0705/slay_the_spire_2_mods/issues/6
[defect-review]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/f033dd6b8f7cb0de6c6d0b1db43ab42cdd9036a8/docs/design/characters/defect/review-v01.md
[defect-commit]: https://github.com/Motoki0705/slay_the_spire_2_mods/commit/f033dd6b8f7cb0de6c6d0b1db43ab42cdd9036a8
[defect-prompt-0]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/f033dd6b8f7cb0de6c6d0b1db43ab42cdd9036a8/art/prompts/defect-v01.txt
[defect-provenance]: https://github.com/Motoki0705/slay_the_spire_2_mods/blob/f033dd6b8f7cb0de6c6d0b1db43ab42cdd9036a8/output/imagegen/defect/defect-v01.provenance.json
