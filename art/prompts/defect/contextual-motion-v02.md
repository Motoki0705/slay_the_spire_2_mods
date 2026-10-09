# Defect — 場面別作画とH3演技 v0.2

[演技設計](../../../docs/design/animation/contextual-motion-v02.md#defect--確かめてから動く機械) / [Issue #51](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/51)。2026-10-09。**未実行プロンプト。** v02と派生は委任に基づく制作採用で、個別ユーザー承認ではない。画像は親がCodex内蔵imagegen、動画は親がH3で実行する。人の顔/金髪/女性の身体はMODの翻案で、公式の性別や生物種を変更したという事実ではない。

## 入力と保持条件

| 入力 | 役割 |
| --- | --- |
| [1: defect-v02.png](../../../output/imagegen/defect/defect-v02.png) | 本人の成人の顔と金髪、青い瞳、大小レンズの装具、青金の細い機構、補修前腕、布と光/画風。背景・座面・３Orbは新本人へ写さない |
| [2: body.png](../../../mod/assets/PopSpireWomen/art/defect/body.png) | 分離済み本人、工具/手/補修部の形。座った修理姿は戦闘/商人へ変更 |
| [3: rest_body.png](../../../mod/assets/PopSpireWomen/art/defect/rest_body.png) | bodyと同じbytes。休憩編集対象として座位と脚を保ち、工具手/前腕を休ませる |
| S: [production scene](../../../mod/assets/PopSpireWomen/select/production/defect.tscn) のUIなしrender | 選択の唯一の始終画像。現在Orbを含まない構図を保つ。実ファイル/hashは親が記録 |

戦闘/商人は1/2。休憩は3/1の順で渡す。本人の顔・好奇心、細い上腕/手首と普通の成人比率、１つの補修plateの量感、青金の機構と青い布を保持する。全身を分厚い新品の左右対称鎧へ整えない。衣装・露出・頭部装具の位置は維持。1024×1536は制作目標で、実出力寸法は記録する。

## 戦闘 — 立った右向きの透明本人を新規作画

工具は腰へ置き、近い補修前腕は打撃/放出を支える手にする。独立Orbは本人へ生成しない。

```text
Use reference 1 for this exact adult female Defect's human facial identity, tousled golden hair, blue eyes, the unequal blue lens components on her head, fine articulated adult frame, blue and gold mechanical body, dark joints, one larger salvaged forearm plate, cyan torso core, blue scarf and cloth, existing feet, and painterly finish. Use reference 2 for the separated mechanical and tool details. Create ONE full-body transparent RGBA combat sprite. She STANDS on the left side of battle facing enemies to screen RIGHT in a readable three-quarter side view: chest, pelvis and face turn right, and her near blue eye, nose and mouth remain visible. Both mechanical feet are firmly planted, forward foot half a step right, knees softly unlocked, pelvis stable. Her gaze reads the enemy with curious but focused resolve. Her nearer larger repaired forearm is held forward below chest level with its articulated palm half open. Her other hand gathers near the torso core, ready to act. Her existing repair tool is stowed securely at the belt and is not held in either combat hand. Fold the scarf behind her, reveal wrists, elbow joints, knees and feet, and preserve the characteristic asymmetry of the salvaged plate. Keep delicate upper arms and natural adult proportions instead of enlarged armor or exaggerated body curves. Fit the entire hair, cloth, fingers and both feet inside a 1024x1536 portrait canvas with transparent margins. The woman and worn/carried equipment only; no orb, permanent electricity, projectile, seat, enemy, scenery, floor, shadow plate, text or UI. Replace the reference's seated repair pose with this clear supported right-facing battle stance.
```

## 商人 — 右の部品を吟味する透明本人

立位は戦闘と分け、肩を落として前腕を腹下へ支える。小さい指間隔で部品寸法を考える。

```text
Create ONE full-body transparent RGBA merchant sprite of the same adult female Defect from references 1 and 2. Preserve her recognizable adult human face, golden tousled hair, blue eyes and unequal blue head lenses, fine blue-and-gold articulated body, dark joints, one larger salvaged forearm plate, torso core, blue scarf and cloth, tool, feet and illustrated finish. She stands on the left of a merchant screen in a relaxed right-facing three-quarter view, chest and pelvis gently right. Her near eye, nose and mouth are visible as she looks down-right toward off-image small mechanical parts with practical curiosity. Both feet rest at a narrow comfortable stance; knees unlocked, shoulders lowered, torso inclines only slightly toward the goods. Support the larger forearm quietly across her lower abdomen. Her free thumb and index finger hold a small empty gap as if estimating a component's width, not gripping an item. The existing repair tool stays at her belt. Let the scarf and cloth hang calmly, with clear hands and wrists. Fit her complete head, fingers, cloth, tool and both feet inside a 1024x1536 portrait canvas with transparent margins. Woman and her worn/carried equipment only, no product in her hand, orb, merchant, merchandise, coin, furniture, background, ground, text or UI. Preserve the same adult proportions and exposure, with neither a braced combat palm nor a seated repair pose.
```

## 休憩 — 現行座位を保って工具/前腕を休ませる

3を局所編集。腰・膝・足・布は再利用し、工具を腕に当てる緊張を緩める。

```text
Make a small pose-only edit to reference 3, the current seated Defect sprite. Reference 1 preserves her exact adult human face, golden hair, blue eyes, unequal blue head lenses, fine blue-and-gold mechanical body, dark joints, larger repaired forearm plate, torso core, scarf, clothes, proportions, exposure and painterly finish. Keep the existing seated silhouette, supported pelvis, knees and naturally lowered feet, fitted to the game's existing rest seat without drawing that seat. Lower her shoulders and let the larger forearm lie with its weight across her lap. Her repair-tool hand also rests on her lap with a relaxed secure grip. Point the intact tool away from her own body, no longer inserted into the forearm adjustment. Her articulated fingers loosen naturally. Her head stays close to its original angle while her eyes gently lower toward her lap or an off-image fire on the right, mouth quiet and composed. Let the blue cloth settle over the thighs and fall from the invisible seat under gravity. Fit every hair tip, finger, scarf end, tool end and toe within the same 1024x1536 portrait canvas with transparent margins. No seat, log, fire, orb, electrical effect, background, floor or text. This is a local pause from maintenance, preserving the same adult woman and mechanical asymmetry.
```

## 選択 — H3 / 768P / 16:9 / ８秒

実APIモデルID/始終画像の受理は#49で確認する。Sを同じ始終画像へ。中心約x=.68、実足y≈.88、左x≤.45は空間を保つ。座位/座面/足は実renderで合わせ、上右を見ている入力の顔へ終端を戻す。主動作は「前腕を一度調整して機能を確かめる」。

```text
Animate the exact supplied full-scene image as one eight-second 16:9 locked-camera shot. Preserve this same adult female Defect's human face, golden hair, blue eyes, unequal blue head lenses, fine blue-and-gold mechanical body, dark joints, larger salvaged forearm plate, torso core, blue scarf and cloth, seated posture, existing feet and repair tool. Keep her near 68 percent of frame width, all feet near 88 percent of frame height, her hips supported by the supplied seat, and the quiet left 45 percent reserved for game UI. From 0 to 1 seconds she holds the supplied curious pose with the tool tip at the forearm adjustment. From 1 to 2.5 seconds her eyes lower to that adjustment and her expression becomes attentive. From 2.5 to 4.5 seconds she makes ONE slow small controlled turn of the tool to adjust the mechanism. From 4.5 to 5.5 seconds the fingers of the repaired hand close and open once to test the result, and she briefly shows small satisfied understanding. From 5.5 to 7 seconds she returns the tool to its exact initial angle without pulling the tip out of its contact point, restores the resting fingers, and raises her gaze and mouth to the original curious expression. From 7 to 8 seconds she holds the exact starting posture while the scarf settles. The single adjustment and function check is the principal action, not merely breathing or wind. Keep metal plates rigid, joints coherent, both feet and the seat contact fixed, finger count stable, and the tool tip connected throughout. Match final equipment, face, lighting and background to the supplied first image for a loop. Preserve the original mechanical ruins, no camera movement, cut, standing up, generated orb, new gadget, outfit change, text or UI.
```

## 部位と受渡し

- 顔+レンズ装具、金髪、各上腕/前腕、分節の手、首布、膝/すね/足を別mesh/層へ。金属plateは剛体、暗い関節の隠れ面を追加。工具は選択/休憩の別層として保持。
- `tool_tip` は工具先と修理箇所の接点、`torso_core` は胸コア/VFX中心。戦闘では工具先を打撃アンカーへ流用せず、打撃手/掌中心を測る。`hand_l/r` は画像の左右、補修腕と自由手を併記して取り直す。
- 戦闘は補修前腕の短い打撃、castは掌を右へ、processはコアを確かめて開く。merchantは指の空いた間隔で１回寸法を比べる。restは工具を置いて指を緩め、目を伏せて戻る。
- 元Orbの数/配置/channel/evoke、独立VFX、attack/cast/process時刻とゲーム速度を保持。工具なし戦闘の手は場面専用clipsへ明示し、旧 `weapon_hand=hand_l` をそのまま打撃手とみなさない。
- 座ったまま修理するcombat、Orbの描き込み、レンズ/顔の別人化、曲がる金属板、指/工具の増殖、seat接触と足の見切れは修正対象。新素材/動画は未生成・未検証。
