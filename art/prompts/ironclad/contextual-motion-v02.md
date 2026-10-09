# Ironclad — 場面別作画とH3演技 v0.2

[演技設計](../../../docs/design/animation/contextual-motion-v02.md#ironclad--力を抑えながら戦う兵士) / [Issue #51](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/51)。2026-10-09。**未実行プロンプト。** v02と派生は委任に基づく制作採用で、個別ユーザー承認ではない。画像は親がCodex内蔵imagegen、動画は親がH3で実行する。

## 入力と保持条件

| 入力 | 役割 |
| --- | --- |
| [1: ironclad-v02.png](../../../output/imagegen/ironclad/ironclad-v02.png) | 本人の顔、銀灰髪、細い成人体型、銅/赤褐/暗色の鎧と服、長剣、腰の仮面、光と画風。背景・現在の立ち方は新ポーズに写さない |
| [2: body.png](../../../mod/assets/PopSpireWomen/art/ironclad/body.png) | 分離済み装備の形と仕上がり。掌の炎を見る立位は戦闘/商人へ流用しない |
| [3: rest_body.png](../../../mod/assets/PopSpireWomen/art/ironclad/rest_body.png) | 休憩編集だけの顔・衣・装備参照。高い剣腕と床へ畳んだ脚は新しい座席対応へ変更 |
| S: [production scene](../../../mod/assets/PopSpireWomen/select/production/ironclad.tscn) のUIなしrender | 選択動画の唯一の始終フレーム。同じ画像を始終へ指定、実ファイル/hashは親が記録 |

入力1/2を使って新しい場面全身を描く。休憩は3も渡す。保持するものは本人・衣装・成人の自然な比率・露出・装備・画風で、変更するものは向き・視線・支持・手の役割。顔の疲れと炎を抑える意志を保ち、筋肉/胸腰/長い脚で強さを足さない。描画の1024×1536は制作目標で、実出力寸法は記録する。

## 戦闘 — 新規透明本人

近い手=鍔側、遠い手=柄頭側の２手握り。刃は右、顔は敵へ。恒常炎は本人へ合成しない。

```text
Use reference 1 for this same adult Ironclad woman's face, short silver-gray hair, delicate natural proportions, bronze practical armor, dark torso, red-brown sleeves and trousers, long sword, carried bronze mask at the hip, and painterly illustrated finish. Use reference 2 for the separated equipment shapes. Create ONE full-body transparent RGBA combat sprite. She occupies the left side of a battle and faces enemies to screen RIGHT in a readable three-quarter side view: chest, pelvis and face turn right, and her near eye, nose and mouth remain clearly visible. Her gaze is fixed on an enemy, calm and burdened but determined. Both boots are firmly planted. The forward foot is half a step to the right, knees softly bent, weight mostly through the rear heel. Keep narrow shoulders and fine wrists beneath the existing thin practical plates. Both hands grip the SAME sword hilt in front of her lower torso: near hand beside the guard, far hand near the pommel. The intact straight blade points diagonally up-right below her face. Make the grips, guard, blade, elbows and feet clear, with no cloth covering them. Preserve her existing clothes, mask and exposure; do not enlarge the armor or change the sword design. Keep all hair, plate tips, the entire blade and both toes inside a 1024x1536 portrait canvas with transparent margins. The woman and carried equipment only; no permanent palm flame, slash trail, enemy, scene, ground, shadow plate, text or UI. Replace the reference's flame-watching standing pose with this supported right-facing sword stance.
```

## 商人 — 新規透明本人

剣先は自分の後ろ側で接地、自由手は前腕の留めへ。右の商品を実用目線で点検する。

```text
Create ONE full-body transparent RGBA merchant sprite of the same adult Ironclad woman from references 1 and 2. Preserve her recognizable face, short silver-gray hair, small shoulders and fine wrists, ordinary adult proportions, bronze armor, red-brown clothes, dark torso, carried hip mask, sword design and illustrated material finish. She stands upright on the left of a merchant screen in a relaxed right-facing three-quarter view. Her near eye, nose and mouth are readable as she looks down-right at off-image practical equipment, with a tired appraising expression. Her feet are a comfortable narrow distance apart and her shoulders are lowered. One hand rests on the sword hilt at waist height. The full blade stands almost upright beside her rear side, its tip touching an implied ground that must not be drawn; it does not point toward the merchant. Her free hand gently touches the fastening on her own forearm armor, as if comparing it with the goods. Her torso and elbows are relaxed rather than braced for attack. Preserve all clothing and exposure. Fit her complete figure, sword tip, hair, armor and toes within a 1024x1536 portrait canvas with transparent margins. Character and her carried equipment only, no flame, merchant, merchandise, coin, furniture, background, floor, text or UI. Keep her gaze on the right-hand goods and her face turned right rather than displaying herself frontally.
```

## 休憩 — 座席用に姿勢を描き直す

元のseatを描かず骨盤/腿の支持を作る。長剣を垂直のまま腿高まで下げると全長と接地が両立しないため、**剣先を外へ斜めに下げて**地面へ預ける。

```text
Use references 1 and 2 to preserve this same adult Ironclad woman's identity, short silver-gray hair, delicate adult proportions, existing bronze armor, red-brown clothes, dark torso, hip mask, intact long sword and painterly finish. Reference 3 supplies seated costume details, but redesign its tense raised sword arm and floor-folded leg arrangement for the game's existing rest seat. Create ONE full-body transparent RGBA rest sprite. She sits with her pelvis and thighs naturally supported by an invisible low seat; do not draw the seat. Show a right-facing three-quarter view with a readable human face. Her shoulders and torso lean slightly forward, knees comfortably forward, both boots supported by the implied ground with one foot a little closer. One forearm lies on her knee with relaxed fingers. Her sword hand rests low beside her thigh with an easy secure grip. The unchanged long blade angles downward and outward to her rear side, away from an off-image campfire to her right, with the tip supported on the implied ground. Keep the real sword length and its rigid shape rather than shortening or bending it to fit. Her gaze falls down-right and her brow and lips soften with fatigue. Let fabric fold at the hips and settle under gravity. Include the whole woman, mask, blade and feet inside a 1024x1536 portrait canvas with transparent margins. No chair, log, fire, flame, background, ground plane, text or UI. Preserve the original clothing and exposure.
```

## 選択 — H3 / 768P / 16:9 / ８秒

実APIモデルID/始終画像の受理は#49で確認する。Sを同じ始終画像に使用し、８秒を戦闘の長さへ流用しない。UIはrenderに含めない。人物中心約x=.68、実接地足y≈.88、左x≤.45を空ける。足とUIはpivot値だけでなく実renderで確認する。主動作は「炎を一度抑える」。

```text
Animate the exact supplied full-scene image as one eight-second 16:9 locked-camera shot. Keep this same adult Ironclad woman's face, short silver-gray hair, delicate build, bronze armor, red-brown clothes, carried hip mask and intact long sword. Preserve the supplied composition with her near 68 percent of frame width, feet near 88 percent of frame height, and the quiet left 45 percent reserved for game UI. From 0 to 1 seconds she holds the supplied pose, watching the flame in her open palm while supporting the planted sword. From 1 to 2.5 seconds she notices the flame rise and deliberately draws her fingers inward. From 2.5 to 4 seconds she closes that hand once, containing the flame to a small ember; her expression shows restraint, not pleasure. From 4 to 5.5 seconds she steadies herself and briefly raises her eyes toward screen right. From 5.5 to 7 seconds she slowly reopens the palm to the exact original angle, restores the original flame size, and lowers her gaze to its original focus. From 7 to 8 seconds she settles into the supplied starting pose. This single act of containing the fire is the main action; breathing and small hair motion support it. Keep both boots and the sword tip fixed in place, the sword perfectly rigid, and the flame below her face and entirely on the character side of the frame. Match the final posture, equipment, lighting and composition to the supplied first image for a loop. Preserve the original ruins; no camera movement, cut, large step, outfit change, new weapon, text or UI.
```

## 部位と受渡し

- 戦闘/休憩の近/遠前腕、２つの握り手、刀身+柄+鍔、短髪、顔、膝plateを分ける。castで柄を離す遠い手の裏面/戻り差分を足す。
- 両握り点は同じ剣の柄上。刃先・鍔・柄頭を実画で測定し剣を剛体で動かす。`hand_l/r` は画像の左右、新画で取り直す。顔を手/鎧の大変形へ巻き込まない。
- 戦闘は膝と柄の引き→右へ一振り→guardへ。商人は装具の留めを１回確かめ→右の商品へ目を戻す。休憩は肩/指が緩み→火を見て目を伏せ→穏やかな座位へ。
- 元のattack/heavy slash event・ダメージ待ち・速度・音・死亡/復帰を保持。生成した恒常炎やslashで元VFXを二重にしない。
- 顔/剣の変形、２手が別々の柄を握る、座位で剣を短縮する、足/刀身の見切れ、商人で右へ刃を構える結果は修正対象。新素材と動作は未生成・未検証。
