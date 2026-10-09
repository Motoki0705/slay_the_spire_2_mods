# Silent — 場面別作画とH3演技 v0.2

[演技設計](../../../docs/design/animation/contextual-motion-v02.md#silent--気配に先に反応する狩人) / [Issue #51](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/51)。2026-10-09。**未実行プロンプト。** v05の基準デザインのみユーザー承認済み。場面派生・動画は親の委任に基づく制作判断で、個別ユーザー承認ではない。画像は親がCodex内蔵imagegen、動画は親がH3で実行する。

## 入力と保持条件

| 入力 | 役割 |
| --- | --- |
| [1: silent-v05.png](../../../output/imagegen/silent/silent-v05.png) | ユーザー承認の本人、かわいい成人の顔、透明感、白髪・緑の瞳、体型・露出・衣装・画風。背景と大きい踏み込み姿勢は新場面へ写さない |
| [2: body.png](../../../mod/assets/PopSpireWomen/art/silent/body.png) | 分離後の角・外套・背面骨・短剣・装備の形。足が浮く歩幅は戦闘へ保持しない |
| [3: rest_body.png](../../../mod/assets/PopSpireWomen/art/silent/rest_body.png) | 休憩の局所編集対象。本人の座位・脚配置を保つ。足の開いた巻き布は既存派生の差分 |
| S: [production scene](../../../mod/assets/PopSpireWomen/select/production/silent.tscn) のUIなしrender | 選択動画の同一始終フレーム、実ファイル/hashは親が記録 |

1/2は新しい戦闘/商人、3/1/2は休憩編集の順で渡す。可愛さ・澄んだ肌/髪/瞳、同じ衣装・露出、細い手足と自然な成人比率を保持する。頭蓋骨は顔を隠し切らない装具として、背の骨は白い三つ編みと別に保つ。膝下の革バンドの省略や休憩靴の違いを、修復したと記録しない。新しい露出を足さない。1024×1536は制作目標で、実出力寸法は記録する。

## 戦闘 — 新規透明本人

両足接地、胸/腰/顔を右へ。近い短剣手と自由手の役割を分け、刃を胸より下へ。

```text
Use reference 1, the approved Silent v05 design, for this exact adult woman's identity, face, clear pale skin, white braided hair, green eyes, delicate natural proportions, costume, exposure and painting style. Use reference 2 for the separated equipment. Create ONE full-body transparent RGBA sprite for combat. She stands on the LEFT side of the game facing enemies to screen RIGHT in a readable three-quarter side view: chest, pelvis and face point right, her near green eye, nose and mouth remain visible, and her gaze is fixed on an enemy to her right. Both feet are planted. The forward foot is half a step right, knees softly bent, weight slightly on the rear leg. Her near hand holds her one recognizable wavy dagger in front of her lower torso, blade pointing diagonally up-right below chest level. Her free hand is open below her chest for balance. Show natural fingers, a continuous grip and a clear wrist. Fold the green cloak behind her to screen left and keep both knees, feet and blade readable. Preserve the horned skull on the green hood with the human face open, separate back bones, gray-green inner garment, dark shorts, wraps, belts and poison vial. Fit the whole figure, both horns, every cloak tip, blade and toe inside a 1024x1536 portrait canvas with transparent margins. Character and carried equipment only; no scene, floor, shadow plate, enemy, permanent poison effect, text, UI or additional dagger. Preserve her focused cute adult face and gentle clear highlights. Replace the reference's long stepping pose with this compact planted huntress stance.
```

## 商人 — 新規透明本人

足幅を狭め肩を下げる。近い手の短剣は腿の脇で下へ、自由手の掌で右の商品を尋ねる。

```text
Create ONE full-body transparent RGBA merchant sprite of the same approved adult Silent from references 1 and 2. Preserve her facial identity, clear skin and white hair highlights, green eyes, delicate natural adult proportions, green hood and cloak, open-faced horned skull, back bones, gray-green inner garment, dark shorts, wraps, belts, vial, one wavy dagger and existing exposure. She stands upright on the left of the merchant screen in a relaxed right-facing three-quarter side view. Her readable face and eyes look slightly down toward off-image goods on screen RIGHT with quiet practical curiosity. Both feet rest on the ground in a narrow comfortable stance, one knee unlocked, shoulders lowered. Her near hand holds the dagger loosely but securely down beside her thigh; the blade points downward and away from her feet. Her free hand is palm-up just below her chest, ready to ask about one item. Let the green cloak hang calmly along her body. Show the entire woman, horns, cloak, toes and blade within a 1024x1536 portrait canvas with transparent margins. Character only; no merchant, merchandise, coin, furniture, ground, background, poison cloud, text or UI. Keep the reference's painterly anime finish and focused cute adult identity. Give her a calm upright shopping posture rather than a combat crouch or lunge.
```

## 休憩 — 現行座位の局所編集

3の本人・座位を保持し、手/前腕/刃だけ緩める。全面の衣装描き直しは不要。

```text
Make a small pose-only edit to reference 3, the current Silent rest sprite. Use references 1 and 2 to keep the approved adult identity, face, costume, colors, delicate natural proportions and existing exposure. Preserve the seated silhouette and folded-leg arrangement: one knee raised, the other leg comfortably folded, pelvis supported on the game's existing seat, which must not be drawn. Let the forearm on the raised knee rest under gravity with loose fingers and a lowered shoulder. Relax the hand carrying her one wavy dagger while maintaining a secure natural grip; lower the blade beside the outer lower leg, away from her own body rather than crossing her thigh. Settle the green cloak around her hips and let its lower folds hang from the implied seat. Her green eyes look gently down-right toward an off-image campfire, expression composed and quietly watchful. Preserve her human face, white braid, open-faced skull and horns, separate back bones, wraps, shorts, belts, vial, toes and every cloak tip. Transparent RGBA, entire figure in the same 1024x1536 portrait canvas with margins. No log, chair, fire, background, floor or text. Preserve the clear painterly finish and current seated costume details, without increasing exposure or lengthening the legs.
```

## 選択 — H3 / 768P / 16:9 / ８秒

実APIモデルID/始終画像の受理は#49で確認する。Sを同じ始終画像へ。中心約x=.68、実足y≈.88、左x≤.45を空ける。`figure_position=.68,.883` はpivotで足そのものではなく、親がrenderを目視して配置を合わせる。主動作は「気配を捉えて短剣を構え直す」。

```text
Animate the exact supplied full-scene image as a single eight-second locked-camera 16:9 shot. Preserve this adult Silent's face, clear skin, white braided hair, green eyes, open-faced horned skull, green cloak, back bones, wraps, shorts, vial and one wavy dagger without redesign. Keep her near 68 percent of the frame width, with all feet near 88 percent of frame height, and preserve the quiet empty left 45 percent for the game interface. From 0 to 1 seconds she holds the supplied huntress pose. From 1 to 2.5 seconds she notices a presence to screen right: her eyes focus first and her free fingers become still. From 2.5 to 4.5 seconds she shifts a little weight onto her rear foot and deliberately brings her existing dagger into a compact ready position directed to screen right below her face, while the free hand balances the move. From 4.5 to 6 seconds she studies that direction in a brief intent pause. From 6 to 7 seconds she lowers the wrist and restores the exact starting weight and posture. From 7 to 8 seconds the cloak settles and she holds the starting pose again. This one clear preparation gesture is the main action; subtle hair and breathing support it. Keep both feet in their original places, the blade and face readable, all equipment intact, and the blade entirely on the character side of the frame. Match the final image to the supplied first image for a loop. Maintain the original forest and lighting; no camera pan, zoom, cut, large step, new costume, poison cloud, text or UI.
```

## 部位と受渡し

- 顔/頭、白髪、短剣+握り手、自由前腕/手、前後の外套、背面骨の基部を分ける。休憩も専用のclosed-eye/手首差分を作り、立位の目レイヤーを流用しない。
- 現行短剣手は画像左 `hand_l`。新しいguardで画像右になるなら `weapon_hand=hand_r` に取り直す。新画の柄中心/刃先、９markerを実測する。旧markerや単純flipでは新ポーズへ合わせない。
- 戦闘は短剣手が先に走り外套が遅れて戻る。Shivは自由手の短い送り、投射物はゲーム側。商人は１点を小さく指して戻る。休憩は火を一度見て目を伏せて戻る。
- 元event・毒/刃の独立VFX・被弾割込み・死亡終端/復帰を保持。大きい回頭/腕振りには隠れ面の作画を足す。
- 正面顔/背面主体、長い歩幅で浮く足、同じbattle guardの商人、腿を横切る休憩刃、露出増、顔の変形は修正対象。新素材/動画は未生成・未検証。
