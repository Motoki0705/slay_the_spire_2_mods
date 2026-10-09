# Spine Editor・動画不要の描画runtime (#26)

2026-10-09。対象は **v0.107.1 / 59260271 / Godot 4.5.1 / .NET 9.0.318 / RitsuLib 0.6.7**。担当 `free-animation-runtime`、作業基準 `b2763f844b0a345793ac8567f7a1996db3480fb2`。Issue本文に残る古い基準commitより、担当依頼のこの版を使用した。

**実装とstandalone検証まで。ゲーム導入・ゲーム起動・正式画像の登録は行っていない。** 親が素材を統合して実機確認する。合成fixtureを正式素材にしたり、未検証のゲーム接続を成功と扱ったりしない。validatorは指定どおり0回。

## 採用した方式

自作のPNGを **Godot Polygon2D + JSONの関節・UV・重み・キー** で描く。戦闘・商人・休憩は、ゲームが生成する元scene・元SpineSpriteを動作driverとして保持し、その現在trackを読み取って自作の描画に反映する。ゲームのSpineデータを書き出したり、差し替えたりしない。

| 比較した経路 | 判断 |
| --- | --- |
| 全面non-Spine、Skeleton2D/AnimationPlayer等へ置換 | 無料で描画は可能。しかし元 `HasSpineAnimation` 分岐を外すと、既存５人の死亡長・音・復活・固有VFXの補完が必要。単にRitsuLibへscene登録してもそれらは揃わない |
| 元Spineの不可視driver + 自作Godot mesh | 採用。元の状態遷移、乱数を使うidleずらし、track速度、event、死亡待ちをそのまま通せる。既存の顔や体格に自作rigを合わせる制約はない |
| Spine Editorで再skin/export | 今回のライセンス・制作指示に合わず採用しない |
| 動画・全身一枚の移動 | 今回は使用しない。bodyだけでも頂点を関節別に変形し、分割層・表情を追加できる |

CPUで関節変換と重み付き頂点位置を計算し、Godotが三角形を描く。元Spineの骨座標を人の顔へ直接転写しない。標準rigは画像の座標markerから作る軽いスターターで、部位の重なりを変える大きな関節動作には分割絵・明示mesh・調整したキーを使う。元の軌道を完全複製したと称するものではない。

## ゲームAPIとの接続

[RitsuLib profile](https://github.com/BAKAOLC/STS2-RitsuLib/blob/2332d9d054f431887aaeffef9aa634959f148889/src/Scaffolding/Characters/CharacterAssetProfile.cs) の `CharacterSceneAssetSet.VisualsPath` と `CharacterUiAssetSet.CharacterSelectBgPath` は別の面を扱う。既存の `CombatScene` は通常scene置換用として残すが、この実装では **CombatRigを指定し、VisualsPathを変更しない**。同時指定は登録時に拒否する。選択背景は引き続きRitsuLibの既存ID profileを使う。

`OriginalVisualBridge` の限定したHarmony postfixは次の３つ。prefixによる元処理のskip、transpiler、カード/command/保存/RNG/死亡処理へのpatchはない。

| 接点 | 実装 |
| --- | --- |
| `CharacterModel.CreateVisuals()` | 原 `NCreatureVisuals` が返った後にoverlayを追加。`res://scenes/creature_visuals/<id>.tscn` との一致を確認。driverは`Visuals` |
| `NMerchantCharacter._Ready()` | 原merchant sceneだけに追加。元コードが `GetChild(0)` を使うため子0を変更しない。`PlayAnimation("relaxed_loop"/"die")` は元のまま |
| `NRestSiteCharacter._Ready()` | `Player.Character.Id.Entry` と原scene pathの両方を確認。driverは通常`SpineSprite`、Regentは`SpineSprite2`、Necrobinderは`Necro`。別`Osty`には触れない |

sceneの型、`Bounds / CenterPos / IntentPos / OrbPos / TalkPos`、休憩の`ControlRoot / Hitbox / SelectionReticle / ThoughtBubble*`を作り直さず残す。別MODが別sceneを返す場合は対象にしない。C#のGodot Node subclassや独自script登録も追加していない。

ゲームの実型名はこの版では `CreatureAnimator`（依頼の「CharacterAnimator」に相当）。`GenerateAnimator` は `MegaSprite` に依存し、初期idle・ランダム位相・loop速度、`SetTrigger`、queued idle、mix、bounds変更を制御する。元driverを残すので、これらをもう一度自前で実行しない。

### 観測と描画の分離

`driver_reader.gd` は `get_animation_state().get_current(0)`、`get_animation_time()`、animation duration、mixing-from/time/duration、skeleton timeとdraw orderを読む。正規化した位相とmix比を新しいrigへ渡す。wall clockから別の攻撃時計を作らず、再生・seek・loop・速度設定・event送信はしない。生のnative track referenceは毎回の読取り内だけに保持する。

`driver_overlay.gd` は元SpineSpriteの **直下のSpineMesh2Dだけ** を抑止する。draw-order slot数とmesh数が一致しなければ元表示を使う。影、Ironcladの`slash_mesh`は既定で残す。Regentはさらに`throne*`と`*guy*`を残す。slotの順が変わっても現在のdraw orderで判定し、終了・未対応animation・資源不備・binding失敗時は保存したvisibilityとVFX位置へ戻す。

SpineSprite自体の`Hide()`、alphaゼロ、process無効化はしない。公式4.2 sourceの `update_skeleton` は `is_visible_in_tree()==false` でanimation apply・world transform・mesh更新をskipするため、親を隠すだけではevent/付着点契約を保てない。末端meshの可視性を変える方式なら、親とslot node、独立武器・VFXを処理し続けられる。[公式実装](https://github.com/EsotericSoftware/spine-runtimes/blob/4.2/spine-godot/spine_godot/SpineSprite.cpp)

### 動作・待機・独立物

| 原作経路 | 自作描画の対応 / 保持対象 |
| --- | --- |
| `Idle → idle_loop`、`Relaxed → relaxed_loop` | 現track位相で呼吸。副次運動はskeleton時間を参照。元のidle乱数を引き直さない |
| `Attack → attack`、`Cast/PowerUp → cast` | 自作の上体・頭・手キーを同じ再生位相へ合わせる。カードのdamage delayをclip長と混同しない |
| Ironclad `heavyAttack → attack_heavy` | 強めの主腕動作。元slashのevent/materialを維持 |
| Silent `Shiv → shiv` | 短い主腕動作。target側のShiv/毒VFXは元制御 |
| Regent `sovereignBladeTrigger → attack_sovereign` | 本人の所作のみ。`Weapons/WeaponAnim1/2`、別`NSovereignBladeVfx`の成長・周回・攻撃・消去を置換しない |
| Necrobinder `summonTrigger → cast_mighty` | 指図・手の動作。OstyのCreature/HP/召喚/復活/死亡に干渉しない。頭炎と鎌粒子の既存eventを残す |
| Defect `PowerUp → process` | 両手の動作。OrbManagerの個数・並び・channel/evoke/clearを変更しない |
| `Hit → hurt`、連続Hit、attack→hit→die | 同じ名前でも現trackの時刻を毎回読むため、新しいtrackを同名と誤って無視しない。mixを描画側で反映 |
| `Dead → die`、初期Dead | 元の終端seekとlengthを観測。自作dieはphase 1で保持し、勝手にidleへ戻さない |
| プレイヤー復活 | この５人に固有Revive clipはなく、元の0.2秒fade-out→idle reset→0.2秒fade-in。overlayは同じvisual rootの子なのでfadeを継承 |
| 休憩３Act | `overgrowth_loop / hive_loop / glory_loop` を読む。座った絵は戦闘用と別の`RestRig`を登録できる |

`CreatureCmd.TriggerAnim` は `Cmd.CustomScaledWait(min(waitTime*0.5,0.25),waitTime,...)` を維持。`StartDeathAnim` が元Spineから返す時間、死亡音、`AnimDie`のcancel/除去、merchant/eventからの直接dieも元実装に任せる。自作描画の終了をawaitしない。これらはローカルDLLの静的確認と設計上の保存で、実ゲームでの回帰結果ではない。

## 素材・rig入力契約

`/tmp/sts2-autonomous/runtime-contract.md` を素材担当へ先行共有した。恒久的な定義は本書と`rig_schema.gd`。全体はschema 1、座標は画像左上原点のpx、+Y下。l/rは**画像上の左右**。元ゲームの座標や解剖学的左右を混ぜない。

基本配置:

```text
mod/assets/PopSpireWomen/art/<character>/
  body.png              # 原則1024×1536、alpha、本人/携行装備
  rig.json
  layers/hair_back.png  # 任意、全canvas同寸・同位置
  layers/cloth.png
  layers/arm_front.png
  layers/eyes_closed.png
  layers/eyes_side.png
  select_background.png # 任意、背景のみ1920×1080
  select_body.png        # 選択専用絵が必要なら
  select_rig.json
  rest_body.png          # 座り姿等、戦闘用を無理に流用しない
  rest_rig.json
```

bodyへ別Osty/浮遊Orb/Sovereign Bladeを合成しない。分割した髪・腕・布はbody上に二重に残さず、動いて現れる下地も補う。未分割のbodyからでもスターターrigで検証を始められるが、失われた遮蔽情報をmeshが復元するわけではない。

```json
{
  "schema": 1,
  "canvas": [1024, 1536],
  "origin": [512, 1450],
  "display_height": 300,
  "body": "res://PopSpireWomen/art/silent/body.png",
  "weapon_hand": "hand_r",
  "markers": {
    "hip": [512, 920], "chest": [512, 600], "head": [512, 310],
    "hand_l": [330, 760], "hand_r": [730, 760],
    "foot_l": [435, 1430], "foot_r": [585, 1430],
    "hair": [450, 490], "cloth": [650, 1130]
  },
  "layers": [
    {"id":"hair_back", "texture":"res://PopSpireWomen/art/silent/layers/hair_back.png", "bone":"hair", "z":-1},
    {"id":"eyes", "texture":"res://PopSpireWomen/art/silent/layers/eyes_closed.png", "bone":"head", "z":1, "expression":"blink"}
  ],
  "anchors": {},
  "clips": {}
}
```

座標は例であり採用値ではない。markerは各キャラの実画像を見て作る。`origin`は足元/座面の基準。`display_height`は**canvas全体**のGodot論理高さであり、透明余白を除いた人物高ではない。`offset:[x,y]`を任意で付け、元visual root内の位置を補正できる。

標準bodyは12×18セルを三角形化し、近い３関節へ正規化した重みを与える。髪・布の局所的な影響も入る。独立layerは指定boneへ100%付ける。`z`はキャラ内だけの相対順序で、ゲームUI全体のZ値を変更しない。`expression:"blink"`は瞬き、`"look"`は視線差分の周期表示。閉じ目/横目は元の目を覆える差分を用意する。reduced motionとdieでは周期表示しない。

### 明示mesh・関節・キー

`meshes`を指定すると自動body meshを置換する（`layers`は追加できる）。以下は構文説明用の矩形で、完成キャラrigの指定ではない。

```json
{
  "id":"body",
  "texture":"res://PopSpireWomen/art/silent/body.png",
  "vertices":[[0,0],[1024,0],[1024,1536],[0,1536]],
  "uv":[[0,0],[1024,0],[1024,1536],[0,1536]],
  "triangles":[[0,1,2],[0,2,3]],
  "weights":[{"head":1},{"head":1},{"hip":0.5,"foot_r":0.5},{"hip":0.5,"foot_l":0.5}],
  "z":0
}
```

UVもsource pixel単位。各頂点の重みの和は1、全頂点・UV・weightの個数を一致させる。画像はcanvasと同寸。`bones`は任意の配列 `{"name":"head","parent":"chest","position":[512,310]}` 等で置き換え可能。positionはsetupの絶対canvas座標、親を先に列挙し、rootと必須９markerと同名の関節を含める。追加した肘・袖先等にもweights/keysを付けられる。

clipは原作の **animation名** をkeyにし、各boneに `[phase, dx_px, dy_px, degrees]` の昇順キーを置く。phaseは0〜1。trigger名、実秒、damage delayとは別。

```json
"clips": {
  "attack": {
    "hand_r": [[0,0,0,0],[0.18,-8,-15,-4],[0.32,40,-20,9],[1,0,0,0]],
    "head": [[0,0,0,0],[0.32,2,0,-2],[1,0,0,0]]
  }
},
"secondary": {
  "hair":{"degrees":1.8,"period":2.7,"phase":0.6},
  "cloth":{"degrees":1.2,"period":3.4,"phase":1.4}
}
```

secondaryのperiodは秒、phaseはラジアン。`secondary:{}`で無効化可能。標準キーは`motion_library.gd`、原作時刻に同期するスターター所作で、正式絵の全アクションを仕上げた証拠ではない。原作eventの発火時刻と新しい武器先端の見え方を実機で合わせてclipsを調整する。自作clipを増やせば未対応animation名にも対応でき、それまでは原表示へ戻る。

### 元VFXの付着位置

例えばNecrobinderの頭炎を新しい頭へ移す入力:

```json
"anchors":{"head_fire":{"bone":"head","position":[512,180]}},
"bindings":[{"path":"Visuals/HeadBoneNode/SteppedFireMix_dark","anchor":"head_fire"}]
```

pathは**元visual rootからの子path**。`..`、外側の絶対path、driver自身、Spine bone/slot node自体へのbindingは拒否する。炎・粒子等の子の位置だけを更新し、rotation/scale/visibility/restartはゲームに残す。既存nodeのreparentや削除はしない。解除時は接続直前の位置を復元し、その後の元処理の変化を毎frame上書きしない。

| キャラ | 接続できる元node / 保つ独立物 |
| --- | --- |
| Ironclad | `Visuals/SlashVfxSlot`のslotは`slash_mesh`。meshと元shader eventを既定で保存。斬撃軌道との位置整合は実機で調整 |
| Necrobinder | `Visuals/HeadBoneNode/SteppedFireMix_dark`、`Visuals/ScytheVfxSlot1/ScytheParticles`、`Visuals/ScytheVfxSlot2/ScytheParticles`。鎌先端/柄等のmarkerからanchorsを作る |
| Regent | `Visuals/Explosion`、`Visuals/SpineArmBone/Particles`、`Visuals/SpineChestBone/Particles`・`ParticlesBack`、`Visuals/SpineLegBone/Particles`・`SpineLegBoneL/Particles`。通常武器とSovereign Bladeは独立維持 |
| Defect | ゲームのOrbManagerを変更しない。元`OrbPos`/IntentPosを保持 |

`preserve_slots`は任意のslot名glob配列。省略時は影/slash、Regentなら玉座/従者も保持。Regentのbodyに新玉座が入るときは `"preserve_slots":["shadow","*guy*"]` 等で旧玉座の二重表示を防ぐ。新画像の玉座と人物の未分離状態は制作記録に残す。重なり・座面・VFXの大きさは親の実機確認項目。

## 選択画面の接続

既存５人の`select/<id>.tscn`は空のdescriptorとして残す。親が実素材を確認して下記の値を設定する。

- `rig_path`: `art/<id>/select_rig.json` または同schemaのrig。
- `background_path`: 背景だけの絵。人物を二重に描き込まない。
- `poster_path`: 任意の完成静止絵。rigが欠損/不正ならposter、それもなければ元の背景sceneへ戻る。
- `figure_position`: canvas内の足元等の位置、既定は画面比(0.62,0.94)。`figure_height`: canvas高さの画面比、既定0.88。`loop_seconds`: Godot所作loop、既定8秒。
- `overlay_scene_path`: #21向け独立Control。`set_presentation_state(active,reduced_motion)` を呼ぶ。背景/コンテナはMouseFilter IGNORE、必要な子だけ入力を受ける。

呼吸、髪/布、差分表情に加え、Silentの頭の向き、Regentの指図、Defectの手元確認などキャラ別の小さなスターター所作を持つ。動画プレイヤー・動画loaderは削除。`configure(poster, rig)` の第２引数は旧video pathから**JSON rig pathへ変更**した。旧video APIは継承しない。

pauseはSceneTreeに従う。reduced motionは静止した自作rigを表示し、overlayにも通知。非表示・切替・exitでnode/texture参照を解放、再entryで新しいrigを作る。入力を待ったり出発処理を遅らせたりしない。**Regentの７星座の実際のhover動作は#21で未実装**。テストの１個の四角いhover fixtureをその完成と混同しない。

## 採用状態と親の最終登録

旧 `Approved: bool` / `ApprovedSkinCatalog` を廃止し、`ProductionSkinCatalog` と以下を分離した。

| 項目 | 意味 |
| --- | --- |
| `Acceptance = UserApproved` | 本人のデザインについて実際のユーザー承認記録がある（Silent v0.5の範囲を参照） |
| `Acceptance = DelegatedProductionSelection` | 委任に基づき制作担当/親が採用。user-approvedとは表示・記録しない |
| `ProductionReady = true` | 登録する素材・rig・必要な確認が揃ったと統合担当が判断 |
| `CombatRig / MerchantRig / RestRig / SelectScene` | 完成した面だけを個別登録。未完成面はnull |

技術テストに通っただけではデザイン採用にならない。デザイン採用だけでもruntime有効化しない。catalogはこのPRでは空。親が例えば次の形で登録する。これは使用例であり実登録ではない。

```csharp
new SkinDefinition("SILENT", DesignAcceptance.UserApproved, ProductionReady: true,
    SelectScene: "res://PopSpireWomen/select/silent.tscn",
    CombatRig: "res://PopSpireWomen/art/silent/rig.json",
    MerchantRig: "res://PopSpireWomen/art/silent/rig.json")
```

設定EnabledとEnabledCharacters、採用状態、ProductionReady、厳密なゲームversion/commit、所有resource pathを満たしたものだけを登録する。欠けたrigやtexturesは描画時にも検証し、元のsceneを残す。`affects_gameplay:false`だけでco-op/save互換を保証しない。

## 検証と再現

通常ビルド/配布出力はこれまでどおりゲーム導入と分離。JSONをPCKへ含める`include_filter`を追加し、pack検査はanimation adapterのparse/instantiateも検査する。第三者DLL、原PCK、元atlas/skel、test fixtureを配布に入れない。

```bash
python3 scripts/build_mod.py test --dotnet /tmp/sts2-tools/issue-7/dotnet/dotnet
python3 scripts/build_mod.py export --with-pck \
  --dotnet /tmp/sts2-tools/issue-7/dotnet/dotnet \
  --godot /tmp/sts2-tools/issue-8/Godot_v4.5.1-stable_linux.x86_64 \
  --game-dir '/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2'
python3 tests/animation/run_checks.py \
  --godot /tmp/sts2-tools/issue-8/Godot_v4.5.1-stable_linux.x86_64 \
  --output /tmp/sts2-tools/issue-26/checks \
  --pck mod/build/PopSpireWomen.pck
```

テストは`xvfb-run`とMesaで実描画し、別の一時projectで合成SVG/JSONを生成してtechnical PCKへexportする。空のhostからそのPCKだけで検査するため、source fileが偶然見えて通ったものではない。`tests/select/run_checks.py`はこの新しいsuiteへの互換入口。旧Theora fixture依存を取り除いた。

確認対象: UV/重み・不正rig拒否、描画pixel、手と顔の異なる変形、髪/布の独立変形と重なり、瞬き、同名Hit再開、mix、death終端、idle復帰、alpha fade、loop/速度/seek読取り、観測による状態/event非変更、描画leaseの復帰、VFX anchorの追従と復元、５人×各動作、選択pause/reduced/hover/input/欠損fallback/再entry/連続解放。

native Spineを含まないGodot標準版のため、read adapterの状態は明示的なmockを使った。**このテストは実ゲームのevent・音・RNG・death waitを実行したものではない。** 画像は技術fixtureで、５人の女性デザインの完成画像ではない。[検証記録と実描画画像](../../tests/animation/evidence/validation.json)

### 親への引継ぎ・未確認

- RitsuLibを含むMODの起動と３postfixの実行、実native SpineMesh2Dとdraw orderの対応。この契約が合わなければ元表示へ戻る設計だが、実機動作の確認は必要。
- 全５人の選択/戦闘/商人/休憩の正式素材を統合し、clip・marker・origin・サイズ・UV/重なりを調整。PNG１枚だけで腕の前後交換や背面の描き足しまで完成したとはしない。
- 特にIronclad斬撃、Necro炎・鎌、Regentの玉座・従者・武器・死亡粒子と本人の位置。bindingsは位置のみ。武器の回転/寸法や前後関係は素材/キーと実機で詰める。
- 元Spine materialに直接かかる特殊なHSV/液体overlay等を自作Polygon2Dへ複製する機能は含まない。元shader処理は続くが、新人物への同一shader表現は別検証・対応が必要。root/driverのmodulateとflipは継承する。
- 発火回数/音/待ち時間、初期Dead、death→revive、割込み、速度設定、複数player、保存/再開、co-op、他skin/frameworkとの競合、実ゲーム性能。
- Regentの７星座hoverは#21。ライブラリ自身の互換性も実起動で確認する。

## 出典・固定範囲

ゲームDLLと原資源は所有インストールから読み取りのみ。配布やcommitには含めない。DLL SHA-256は`mod/GameReferences.props`に固定。IL/scene原本はmain worktreeのgitignored調査資料を参照した。

- [動作棚卸し](../research/motion/inventory.md)、`core-animation.il.txt`の５人GenerateAnimator・CreatureAnimator・merchant/rest、`combat-triggers.il.txt`のNCreature Ready/StartDeathAnim/StartReviveAnim/TriggerAnim、各creature_visuals scene。
- [既存方式調査](../research/implementation/options.md)。Spine Editor往復を必須とした旧PoCは今回のゲートではない。
- [Ritsu profile](https://github.com/BAKAOLC/STS2-RitsuLib/blob/2332d9d054f431887aaeffef9aa634959f148889/src/Scaffolding/Characters/CharacterAssetProfile.cs)（SHA-256 `e067ede384b0fc59bbfec80ab51330096a31d36b70ff5fff66f67394f9861d26`）と[factory patch](https://github.com/BAKAOLC/STS2-RitsuLib/blob/2332d9d054f431887aaeffef9aa634959f148889/src/Scaffolding/Content/Patches/ModModelRuntimeGodotFactoryPatches.cs)（`9443dbed7a0be3efe7649a5829a97dcbd9869d55ceef49cd3209e0cfdf77543c`）、取得2026-10-09。
- [Godot 4.5 Polygon2D](https://docs.godotengine.org/en/4.5/classes/class_polygon2d.html)、[CanvasItem](https://docs.godotengine.org/en/4.5/classes/class_canvasitem.html)、取得2026-10-09。mesh/UVと可視性/子への影響の確認。
- [SpineSprite 4.2 source](https://github.com/EsotericSoftware/spine-runtimes/blob/4.2/spine-godot/spine_godot/SpineSprite.cpp)、取得2026-10-09のSHA-256 `8eb74951e2e302dacb9590c0d7ba9d26aa8822cfeddce40147e9265d5838ae3f`。関連TrackEntry/Skeletonも公開methodを確認。取得sourceは調査用tempだけで、組込み/改変/配布していない。公開4.2 branchとゲーム同梱native binaryの同一性を主張しない。

本MODの新規authoringはGodot/自作JSON/自作画像。元ゲームのSpine runtimeを実行時に参照することと、自作runtimeやEditor成果を配布することを区別する。Editor購入、Trial制限の回避、元Spineデータの書出し、native runtimeの改造/同梱は行っていない。
