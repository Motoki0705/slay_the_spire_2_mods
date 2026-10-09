# Regent — 場面別作画とH3演技 v0.2

[演技設計](../../../docs/design/animation/contextual-motion-v02.md#regent--指図する自負と取り繕い) / [Issue #51](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/51)。2026-10-09。**未実行プロンプト。** v02と派生は委任に基づく制作採用で、個別ユーザー承認ではない。画像は親がCodex内蔵imagegen、動画は親がH3で実行する。公式の立場は星の王位継承者であり、即位済みの女王という設定は加えない。

## 入力と保持条件

| 入力 | 役割 |
| --- | --- |
| [1: regent-v02.png](../../../output/imagegen/regent/regent-v02.png) | 小さい成人の本人、顔、橙髪/星飾り、大きい青金の王衣、手首、同じブーツ、画風。独立剣と背景は新規本人へ写さない |
| [2: body.png](../../../mod/assets/PopSpireWomen/art/regent/body.png) | 本人の分離位置/仕上げ。左の指図姿勢を右向きの戦闘/商人へ変更する |
| [3: throne.png](../../../mod/assets/PopSpireWomen/art/regent/layers/throne.png) | 戦闘/商人の**配置だけ**の支持参照。新画像の出力に玉座/従者を含めない |
| [R: rest_body.png](../../../mod/assets/PopSpireWomen/art/regent/rest_body.png) | bodyと同じbytesの旧休憩。別の休息演技を持つ基準とは扱わない |
| S: [production scene](../../../mod/assets/PopSpireWomen/select/production/regent.tscn) のUIなしrender | 選択の唯一の始終画像。玉座と従者を含む。７星座hover図形/UIを焼かない。実ファイル/hashは親が記録 |

戦闘/商人は1/2/3、休憩は1/2だけを使う。橙髪・成人の顔・細い手首と小さい肩を保ち、大きい王衣の形で自負を見せる。冠や顔を元の星形の非人間頭へ戻さない。衣装/露出/装備を変更せず、膨らませた胸腰や幼い顔にしない。1024×1536は制作目標で、実出力寸法を記録する。

## 戦闘 — 玉座に合う右向きの透明本人

本人だけを描き、玉座との座面/肘の重なりは合成時に検査する。必要な支持層補修は親が別画像として行う。

```text
Use reference 1 for the exact adult female Regent's identity, orange short hair and star-shaped head ornament, expressive human face, small adult frame and fine wrists, oversized cobalt robe with its gold trim and chain, existing boots and painterly finish. Use reference 2 for the separated figure and reference 3 ONLY to locate the existing throne seat and armrests. Create ONE full-body transparent RGBA combat sprite of the woman ALONE. She remains seated on the invisible existing throne, with her pelvis naturally supported at the seat. On the left side of the battle she faces enemies to screen RIGHT in a readable three-quarter side view: chest, pelvis, knees and face are oriented right, and her near eye, nose and mouth are visible. Her chin is proudly raised but her eyes attend to the enemy. She sits a little forward rather than reclining. Her near hand points decisively to the right below face level, her far hand braces the existing off-image armrest. Her lower legs and boots hang naturally from the seat. Keep the small woman inside the broad robe; let the sleeve and hem folds follow her right-facing pose without enlarging her body. Fit the full star ornament, hair, fingers, sleeves, robe and both boots within a 1024x1536 portrait canvas with transparent margins. Woman and worn clothing only: do not draw the throne, bearers, floating sword, weapon effects, scenery, ground, text or UI. Do not put a sword in either hand. Replace the reference's leftward pointing pose with a clear rightward combat command while retaining her facial identity and costume.
```

## 商人 — 玉座で値踏みする透明本人

右の商品へ向くが背を預け、指示の指ではなく掌で価格を問う。独立剣の「武器を下げる」は本人の命令姿勢を解除して表す。剣nodeの挙動を勝手に変更しない。

```text
Create ONE full-body transparent RGBA merchant sprite of the same adult female Regent from references 1 and 2. Preserve her distinctive orange hair, star ornament, adult face, small shoulders and fine wrists, oversized blue robe, gold trim and chain, boots, proportions, exposure and painterly finish. Reference 3 supplies only the unchanged seat and armrest positions and must not appear in the output. She sits on the invisible existing throne on the left side of the merchant screen in a right-facing three-quarter view. Her back is comfortably supported, shoulders lower, and her eyes look down-right at off-image goods. Keep her near eye, nose and mouth readable. One eyebrow rises with proud curiosity. Her near hand is palm-up below the chest as if asking the price, fingers loose rather than pointing a combat order. Her far hand rests quietly on the off-image armrest. The legs and boots hang naturally with no braced attack posture. Broad royal cloth folds settle over her small frame. Fit her complete head ornament, hair, hands, sleeves, robe and both boots inside a 1024x1536 portrait canvas with transparent margins. The woman alone; no throne, bearer, floating sword, merchandise, coin, merchant, background, ground, text or UI. Keep her attention on the goods at screen right and preserve the same adult identity and clothes.
```

## 休憩 — 元の休憩座席に座る本人を新規作画

旧指図/玉座姿勢を再利用しない。自作throne層はこのrest rigから外す。本人の衣装と性格は保つ。

```text
Use references 1 and 2 for the exact adult female Regent's identity, orange short hair, star head ornament, expressive human face, small natural adult frame, fine wrists, oversized cobalt royal robe, gold trim and chain, boots and painterly illustrated finish. Create ONE new full-body transparent RGBA rest sprite of her sitting on the game's existing low rest seat, which must NOT be drawn. Her pelvis and thighs are naturally supported by the invisible seat; her knees sit comfortably close and the boots drop naturally toward the implied ground. Show a readable right-facing three-quarter human face. She lets her small shoulders sink into the large robe, her eyelids soften and her chin remains slightly proud. One hand rests on a knee, the other lies loose on the robe across her lap. No pointing command or raised arm. Let the heavy blue sleeves and robe settle at the hips and hang from the seat under gravity, preserving their existing construction and colors. Show all hair, star points, fingers, robe ends and both boots inside a 1024x1536 portrait canvas with transparent margins. The woman and worn clothes only: no throne, bearers, floating sword, stool, log, fire, background, ground plane, text or UI. Preserve her adult facial proportions, natural body and existing exposure.
```

## 選択 — H3 / 768P / 16:9 / ８秒

実APIモデルID/始終画像の受理は#49で確認する。Sを同じ始終画像に使う。中心約x=.68、**支持する従者の接地足**y≈.88、本人の下がる靴は元位置、左x≤.45は空ける。顔/指/袖と７hover領域が重ならないか実renderで確認する。主動作は「命じる→小さな揺れを取り繕う」１回。

```text
Animate the exact supplied full-scene image as one eight-second 16:9 locked-camera shot. Preserve the same adult female Regent, her human face, orange hair and star ornament, small frame, oversized blue and gold robe, stone throne and the two existing orange bearers. Keep the group near 68 percent of frame width, its supporting feet near 88 percent of frame height, both of her own boots visible in their supplied positions, and the quiet left 45 percent reserved for game UI. From 0 to 1 seconds she holds the supplied proud pointing pose. From 1 to 2.5 seconds her eyes align with her existing pointing hand and she sits a little more upright. From 2.5 to 4 seconds she delivers ONE grand command with a precise small movement of her index finger and wrist, entirely in the character's own area. From 4 to 5 seconds the existing throne and bearers dip and wobble only slightly without stepping or travelling. From 5 to 6 seconds her other hand briefly tightens on the armrest, her eyes widen for an instant, then she immediately recovers her proud composure. From 6 to 7 seconds she restores the pointing hand, torso and expression to the exact starting pose. From 7 to 8 seconds the throne and clothing settle to the supplied starting image. This commanding gesture and brief recovery are the principal action, not just idle wind. Keep her hips on the seat, bearers under the throne and all equipment intact. Match the final composition, posture, shadows and background to the first image for a loop. Preserve the original cosmic ruins, no camera move, cut, new bearer, generated sword, costume change, constellation diagram, text or UI.
```

## 部位と受渡し

- 本人の顔+髪/星飾り、指図手+大袖、肘掛け側手+袖、膝/ブーツ、前裾を別層/meshへ。玉座+従者は既存の別層を保つ。新本人と支持層の肘・腰・靴の隠れ境界を見て、足りなければ支持層の隠れ面だけ補修する。
- `hand_l/r` は実画の左右、指示手を併記。剣を持たない本人に `weapon_hand=none` を入れない。専用clipsでcommand手を指定し、generic武器手を意味として流用しない。
- 戦闘は右へ１回命じて戻る。merchantは掌と片眉で条件を問う。restは１度袖口を整え、手を膝へ戻す。新restのseat/腰を測り、throne層を除く。
- 独立Sovereign Blade/通常武器の元event・Forge/対象/周回、死亡粒子、７星座hover入力を保持。選択Sにない剣を動画へ加えない。
- 正面pinup、左向きの命令を戦闘へ流用、支持面から浮く本人、玉座をrest seatへ二重配置、幼い顔、生成された剣/星座UIは修正対象。新素材/動画は未生成・未検証。
