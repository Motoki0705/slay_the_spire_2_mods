# Necrobinder — 場面別作画とH3演技 v0.2

[演技設計](../../../docs/design/animation/contextual-motion-v02.md#necrobinder--合図と相棒への信頼) / [Issue #51](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/51)。2026-10-09。**未実行プロンプト。** v02と派生は委任に基づく制作採用で、個別ユーザー承認ではない。画像は親がCodex内蔵imagegen、動画は親がH3で実行する。人の顔/髪/衣装の骨意匠はMODの翻案で、公式に身体を回復したという新設定ではない。

## 入力と保持条件

| 入力 | 役割 |
| --- | --- |
| [1: necrobinder-v02.png](../../../output/imagegen/necrobinder/necrobinder-v02.png) | 本人の成人の顔、紫髪、頬の骨意匠、細い肩/手首、赤紫の長衣と襟、ロケット、鎌、光/画風。Ostyと背景は新本人へ描かない |
| [2: body.png](../../../mod/assets/PopSpireWomen/art/necrobinder/body.png) | 本人と携行鎌の分離素材。現在の左下を見る顔/手は新しい右向き場面へ変更 |
| [3: rest_body.png](../../../mod/assets/PopSpireWomen/art/necrobinder/rest_body.png) | 休憩の局所編集対象。横座り、膝上の手、長衣を保持候補とする |
| S: [production scene](../../../mod/assets/PopSpireWomen/select/production/necrobinder.tscn) のUIなしrender | 選択動画の唯一の始終画像。現在Ostyを含まない構図を保つ。実ファイル/hashは親が記録 |

戦闘/商人は1/2。休憩は3/1/2の順で渡す。本人の鋭さと軽さ、普通の成人比率、細い手首、絞りすぎない胴と衣服の量を保つ。小さい霊光はMODの演出案であり、頭炎の正体とSoulsが同じという設定は加えない。露出・衣装・鎌の全長を変えない。1024×1536は制作目標で、実出力寸法は記録する。

## 戦闘 — 新規透明本人

右の敵/Osty側へ胸と視線と自由手を向ける。鎌は背後側へ置き、顔と手を遮らない。

```text
Use reference 1 for the exact same adult Necrobinder woman's identity, short violet hair, sharp human face with its pale bone-like cheek markings, fine wrists and small shoulders, ordinary adult proportions, magenta traveling robe and pointed collar, dark bone-patterned inner clothes, locket, boots, scythe and painterly finish. Use reference 2 for the separated costume and carried weapon. Create ONE full-body transparent RGBA combat sprite. She stands on the left side of battle and faces an enemy to screen RIGHT in a readable three-quarter side view: chest, pelvis and face turn right, with the near eye, nose and mouth clearly visible. Both boots touch the implied ground, forward foot half a step right, knees easy and weight slightly toward the rear leg. Her scythe hand supports the same intact long scythe on her rear side; keep the blade behind and away from her face. Her free hand reaches slightly right below chest level with poised fingers, ready to signal her off-image independent companion. Her eyes study the enemy, one eyebrow confident, mouth lightly composed. Let the long robe fall in broad planes without tightening the waist or lengthening her legs. Fit every collar point, hair tip, fingertip, scythe blade and shaft end, robe edge and toe inside a 1024x1536 portrait canvas with transparent margins. The woman and carried equipment only, no Osty, skeletal helper, permanent head flame, spell projectile, enemy, scene, ground, text or UI. Replace the reference's leftward gesture with clear rightward combat intent while preserving the same adult face and clothes.
```

## 商人 — 新規透明本人

握りを腰へ下げ石突きを接地し、鎌を後方へ軽く傾ける。長い鎌の刃は背後上方に残るが、右の商品へ持ち上げるguardにはしない。

```text
Create ONE full-body transparent RGBA merchant sprite of the same adult Necrobinder from references 1 and 2. Preserve her short violet hair, recognizable sharp adult human face and pale cheek markings, fine wrists, natural adult proportions, magenta pointed-collar robe, dark inner clothes, locket, boots, unchanged long scythe and painterly finish. She stands upright on the left side of a merchant screen in a relaxed right-facing three-quarter view. Show her near eye, nose and mouth as her eyes look down-right at off-image jewelry or an amulet. Her feet are close and stable, shoulders and elbows lowered. Her scythe hand holds the shaft low at hip height with its butt supported on the implied ground. Let the shaft tilt slightly backward; the large blade remains behind her on the left, never aimed at the goods or merchant. Her free hand lightly touches near her own locket as she compares it with the merchandise, one eyebrow raised in dry, practical interest. Let the robe settle vertically rather than spread into a battle stance. Keep all hair, collar, fingers, robe tips, boots and both scythe ends inside a 1024x1536 portrait canvas with transparent margins. Woman and carried equipment only; no Osty, fire, spell, jewelry in the hand, merchant, furniture, merchandise, coins, scene, floor, text or UI. Keep the same face, clothes and exposure and a calm shopping posture.
```

## 休憩 — 横座りを保持して局所編集

3の座位・本人を保ち、鎌手・肩・目線を休息へ。座席とOstyを生成しない。

```text
Make a small rest-pose edit to reference 3, the current Necrobinder seated sprite. Use references 1 and 2 to preserve the exact adult identity, violet short hair, cheek markings, face, fine wrists, ordinary proportions, magenta collar and robe, dark inner clothes, locket, boots, unchanged scythe, exposure and painterly finish. Keep the existing side-seated silhouette and comfortably folded legs, with her pelvis supported by the game's existing rest seat, which must not be drawn. Lower the scythe-side shoulder and bring the grip closer to hip height. Keep the long shaft intact with its butt resting on implied ground beside the seat and its blade behind her, away from her face. Let her free hand lie loose on her knee with relaxed fingers. Settle the long robe at the seat and around her legs under gravity. Keep the head angle close to the existing sprite, but let her eyes glance gently down-right toward an off-image fire or companion, her mouth becoming quietly composed. Include her whole figure, hair, collar, robe, both boots and both scythe ends within the same 1024x1536 portrait canvas with transparent margins. No chair, log, fire, head-flame graphic, Osty, helper, background, floor or text. This is a local relaxation of the same seated woman, not a redesign of her clothing or body.
```

## 選択 — H3 / 768P / 16:9 / ８秒

実APIモデルID/始終画像の受理は#49で確認する。Sを同じ始終画像に使う。中心約x=.68、接地足y≈.88、左x≤.45を空ける。刃/霊光とUIを実renderで検査する。入力にないOstyを動画へ追加せず、自由手の呼びかけで意図を示す。

```text
Animate the exact supplied full-scene image as one eight-second 16:9 locked-camera shot. Preserve this same adult Necrobinder woman's sharp human face, violet short hair, pale cheek markings, slender natural proportions, magenta pointed collar and robe, dark clothes, locket, boots and intact long scythe. Keep her near 68 percent of frame width, feet near 88 percent of frame height, and the quiet left 45 percent reserved for game UI. From 0 to 1 seconds she holds the supplied pose. From 1 to 2 seconds her eyes focus on her own extended fingers. From 2 to 4 seconds she makes ONE deliberate beckoning curl of the free fingers, then turns that palm upward while the scythe hand stays steady. From 4 to 5.5 seconds a single small thin violet spectral wisp follows a short arc just above her palm; her mouth softens with a private confident response. Keep the wisp below her face and entirely inside her own area. From 5.5 to 7 seconds the wisp fades completely, her wrist and fingers return to their exact original positions, and her gaze returns to the starting direction. From 7 to 8 seconds the robe and hair settle into the supplied first-image pose. The beckoning and guiding gesture is the principal action, not just breathing or wind. Keep the boots and scythe shaft end in place, the weapon rigid, and the face readable. Match final pose, equipment, shadows and background to the first image for a loop. Preserve the original purple ruins and any glow already present in the input; no camera movement, cut, new Osty or helper, extra head flame, large scythe swing, outfit change, text or UI.
```

## 部位と受渡し

- 顔/髪、大襟、自由手+袖、鎌+握り手、前後の裾を分ける。鎌の刃/柄は剛体、顔は衣の大変形から保護する。休憩のlow gripとclosed-eyeは局所差分を作る。
- 新画の `head_fire`、`scythe_grip`、`scythe_tip`（刃先）、`scythe_blade_base`、`scythe_shaft_tip`（石突き）をsourceの絶対pixel座標で測る。現行の握り手は画像右 `hand_r`、新画で再定義。
- 戦闘は鎌の短い送り、castは掌を右へ、mightyは招いてOstyへ明確な指令。merchantはロケットを１回見比べる。restは相棒の側を見て小さく頷き戻る。
- 元OstyのHP/位置/攻撃/死亡/復活、本人の頭炎shader/死亡非表示、鎌FX eventを残す。頭炎は生成bodyへ焼かず、元bindingへ新座標を渡す。相棒がいない入力を固定合成で補わない。
- 左向き/正面の戦闘、顔を刃が隠す、鎌の曲がり/短縮、shopで鎌を右へ構える、Ostyの描き込み、頭炎の二重表示は修正対象。新素材/動画は未生成・未検証。
