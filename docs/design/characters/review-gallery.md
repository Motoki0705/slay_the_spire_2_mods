# ５人のレビュー候補ギャラリー

[開発の案内](../../development/README.md) / [Issue地図](../../development/issue-map.md) / [全体Issue #1](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/1)

確認日: **2026-10-09（JST）**。[Issue #19](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/19) の案内として、既存PR本文と、そのhead commitの制作記録を整理した。５人とも**デザイン未承認・ユーザーレビュー待ち**で、各PRはmain未統合のdraft。人物像は各PRのMOD用の提案、残課題は制作担当が記した内容である。本案内で外見の採点・独立評価・承認は行っていない。

目標は、人の顔・髪・表情を持つ女性への翻案。[キャラクター方針 v0.3](review-v03.md) は翻案の意図を読む入口で、今回の候補画像と制作結果は下記の固定記録を参照する。

## ５人を比較する

画像をクリックすると原寸PNGを開く。画像URLは、下表に記した**PR headの完全なcommit SHA**を含むGitHub raw URLで固定している。PRへ後から変更が追加されても、この比較対象は自動では切り替わらない。

| Ironclad v0.1 | Silent v0.5（修正後） | Regent v0.1 | Necrobinder v0.1（corrected） | Defect v01 |
| --- | --- | --- | --- | --- |
| [![Ironclad v0.1 未承認レビュー候補][ironclad-image]][ironclad-image] | [![Silent v0.5（修正後） 未承認レビュー候補][silent-image]][silent-image] | [![Regent v0.1 未承認レビュー候補][regent-image]][regent-image] | [![Necrobinder v0.1（corrected） 未承認レビュー候補][necrobinder-image]][necrobinder-image] | [![Defect v01 未承認レビュー候補][defect-image]][defect-image] |
| [PR #12][ironclad-pr] / [Issue #3][ironclad-issue] | [PR #13][silent-pr] / [Issue #2][silent-issue] | [PR #15][regent-pr] / [Issue #4][regent-issue] | [PR #17][necrobinder-pr] / [Issue #5][necrobinder-issue] | [PR #16][defect-pr] / [Issue #6][defect-issue] |

Silentは `silent-v05.png`、Necrobinderは `necrobinder-v01.corrected.png` が比較対象。両者の初回出力は各レビュー記録で追跡する。他３人は各 `v01.png` を使う。単独キャラのv0.1/v01と、不採用の５人集合案 `lineup-v01.png` は別の版である。

## 提案された人物像と、担当が残した課題

表題は固定commitのレビュー文書から転記した。各行の人物像も、その文書とPRの提案の要約であり、公式設定の追加を示すものではない。

| レビュー記録の表題 | 人物像・場面の提案 | 担当記録の残課題（全員未承認） |
| --- | --- | --- |
| [Ironclad 初回レビュー v0.1][ironclad-review] | 剣を支えに掌の炎を抑えようとする女性兵士。銀灰色の髪と素顔、腰に携行する仮面で、力と本人の意志の緊張を表す提案。 | 鎧の重量、炎の量、ポップさ、他４人との比較はレビュー待ち。呼吸や炎制御の成否は静止画では確定できない。 |
| [Silent v0.5 — 透明感と繊細さの部分編集][silent-review] | v0.4の可愛い人の顔、狩りに集中する視線と短剣、衣装・露出を基準に、肌・白髪・緑の瞳・布の光と質感を整える部分編集。 | すねの肌の隙間は修正されたが、前脚の膝直下の濃色の革バンドが省略され、装備の完全保持は未完了。尖った外套輪郭も残り、透明感・繊細さと野性味の低減が十分かはレビュー待ち。 |
| [Regent v0.1 — 女性の星の継承者・画像レビュー候補][regent-review] | 短い銅橙の髪と人の表情を持つ女性の継承者。揺れる玉座で従者へ指図しながら威厳を保つ提案。青い王衣、橙の従者、離れて浮く剣を引き継ぐ。 | 従者へ向ける視線と、一瞬慌てて取り繕う表情は控えめ。滑稽さは運び手の苦労に強く表れているという担当記録。従者との応答の読みやすさはレビュー待ち。 |
| [Necrobinder v0.1 — 相棒への合図に表情が緩む死霊術師][necrobinder-review] | 人の顔と短い暗紫の髪を持つ死霊術師が、Ostyへ合図して口元を緩める提案。赤紫の長衣・鎌と、独立した相棒への信頼・復讐の意志を同じ場面に置く。 | 修正後は５指が読めるという担当記録。ただし掌面と手背の描き分けが弱く、Ostyが左手という受入条件の確認は未完了。許可された１回の修正枠は使用済み。 |
| [Defect v01 — 自己修繕の途中でオーブへ気を取られる女性型オートマトン][defect-review] | 人の顔・髪・表情を持つ女性型オートマトンが、前腕の修繕を止めてオーブを見る提案。青と金の機械身体、交換部材、工具で生存の手入れと好奇心を表す。 | オーブは広い弧より縦にまとまり、表情は小さな納得より驚きが強いという担当記録。配置・表情はレビュー待ち。工具寸法、留め具、動作の前後は未検証。 |

Silentの露出はv0.4の調整を保持する指定で、今回さらに15%増やす指定ではない。「透明感」は肌・髪・瞳・布の光と色を指し、背景alpha透過ではない。Necrobinderの修正画像を掲載することは、Ostyの左右未確認を解消したという扱いにはしない。

全員について、正式な部位素材・動画・rig適合・実ゲーム表示・実プレイは未確認。Regentの従者とSovereign Blade、NecrobinderのOsty、Defectのオーブを含む静止画はレビュー用の一場面で、ゲームでの独立制御を確認した素材ではない。Defectの雷・氷・闇は描画した代表３種で、原作のオーブ全種類を網羅する案ではない。

## 制作条件・担当・固定した出典

画像APIモデルは、各制作記録の **`gpt-image-2 / high / 1024×1536 / RGB PNG`**。制作エージェントに指定された **`gpt-6.1-sol / max / service_tier=default`** とは別の情報である。実効設定の確認範囲、生成回数、入力の役割、入力・出力のSHA-256、API成否、担当の目視結果は原記録へ戻って確認する。

| キャラ | 制作担当 | 固定したPR head commit | プロンプト・来歴 |
| --- | --- | --- | --- |
| Ironclad | `art-ironclad` | [`87ce8c21536fac2c2d1ce360e513fddb7e4e296d`][ironclad-commit] | [初回プロンプト][ironclad-prompt-0] / [来歴・hash][ironclad-provenance] |
| Silent | `art-silent` | [`6cbe67515274a24cb46761ae16aae9eed28cc4ac`][silent-commit] | [初回プロンプト][silent-prompt-0] / [修正プロンプト][silent-prompt-1] / [来歴・hash][silent-provenance] |
| Regent | `art-regent` | [`4f97a7a700cfb42e9b1435b6f8049d9b48fb75af`][regent-commit] | [初回プロンプト][regent-prompt-0] / [来歴・hash][regent-provenance] |
| Necrobinder | `art-necrobinder` | [`060f6c3cfc7ad56420f1ab6f6d21d378e2b35b31`][necrobinder-commit] | [初回プロンプト][necrobinder-prompt-0] / [修正プロンプト][necrobinder-prompt-1] / [来歴・hash][necrobinder-provenance] |
| Defect | `art-defect` | [`f033dd6b8f7cb0de6c6d0b1db43ab42cdd9036a8`][defect-commit] | [初回プロンプト][defect-prompt-0] / [来歴・hash][defect-provenance] |

Silentの来歴は初回と修正の履歴を、Necrobinderの来歴は初回とcorrected版の出力を区別している。正式デザインの承認と、生成・担当目視・通常検証・PR提出の各記録は別々に読む。原作の根拠は [キャラ調査](../../research/characters/README.md) と [参照画像索引](../../../art/references/README.md) にある。ローカル設定の調査版はv0.107.1 / 59260271で、最新版との一致は未確認。

## 旧案と、次の案を追加するとき

５人集合案 [v0.1の不採用記録](archive/rejected-v01.md) と [v0.2の不採用記録](archive/rejected-v02.md) は履歴として参照する。これらの画像を現行の制作見本として掲載しない。Silent v0.4は今回の編集元であり、編集元・旧版・明示的な不採用を同じ意味にまとめない。

更新では、まず「何を比較し、どの判断をする入口か」を決め、[文書の拡張の考え方](../../README.md#拡張を判断する考え方) に沿って区分を見直す。

- `current`を「今比較する候補」として切り替えるなら、選定を指示したIssue・ユーザーコメントと対象の画像名を根拠にする。新版やPR mergeだけで正式承認へ進めない。`pending`の承認待ちや未完了条件は併記し、承認時には誰のどのコメントがどの画像を対象にしたかを残す。
- `rejected`への切替は明示的な不採用判断を根拠にし、理由と対象版を残す。後続案への置換だけなら、旧版・編集元としての役割を確認する。
- 画像、PR head SHA、レビュー文書、全文プロンプト、来歴の選択出力とhash、承認状態を一緒に照合して更新する。修正版がある場合は、初回と最終候補を区別し、残課題・確認日・Issue地図も更新する。
- 区分が比較対象と承認状態を混同させるなら、欄の分離・統合、改名、文書の分割や旧形式の廃止も選べる。変更理由と新旧の対応を残し、画像から原記録へ戻れること、旧リンクから意味を追えることを確かめる。現在の表やパスの維持を目的にしない。

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
