# プレイアブルと相棒の動作棚卸し

調査日: 2026-10-08。対象: ローカル公式配布 **v0.107.1 / commit 59260271 / 2026-06-18**、Godot 4.5.1。５人の外観変更計画に影響する動作を調べた。ゲーム起動、ゲーム原本の変更、MOD実装、画像・動画生成は実施していない。現行最新版の実プレイ確認とは区別する。

## 調査結果と読む順番

選択画面の５人は、それぞれ **１本の `animation` をループ**する。入場・選択・解除ごとに別名のキャラ演技があるとは確認できなかった。キャラ切替で背景sceneを作り直すため、別のキャラから戻った場合には同じループが再開する。同じ選択済みボタンの再選択は `Select` の早期returnで抑止される。

戦闘は、全員の待機・通常攻撃・cast・被弾・死亡に加え、Ironcladの重攻撃、SilentのShiv、RegentのSovereign Blade動作、Necrobinderの召喚動作、Defectのpower動作が別にある。**Osty、Regentの武器とSovereign Blade、Defectのオーブは本体と独立した動作**である。商人と休憩も対象に含まれ、イベントで通常戦闘の動作を使う場面、商人・休憩・イベントからの死亡表示も存在する。

動画生成AIの使用候補は、まず選択画面の背景込みループ、次にキャラ単体の待機・攻撃・被弾・死亡等の素材制作。戦闘状態、ターゲット、数値、相棒の生死に依存する動作は、独立したゲーム側制御を残す。この分類は制作案であり、動画差替え方式の可否・費用・生成AIサービスの対応形式を実証したものではない。方式は [実装調査](../implementation/) に引き継ぐ。

| 証拠レベル | 本書で確定すること | 確定しないこと |
| --- | --- | --- |
| 資源解析 | PCKにあるscene、参照、Spineアニメ名・長さ・骨・slot・event | すべての資源が通常プレイに到達すること |
| 静的runtime追跡 | DLLの呼出し・条件分岐・状態遷移にある接点 | ゲーム起動時の成功、実際の見た目、最新buildとの一致 |
| 制作提案 | 以下のA/B/C分類、制作単位、優先度 | 現在ゲームが動画生成AIを使っているという主張 |

一次資源と解析方法は [evidence/README.md](evidence/README.md)。[scene-map.json](evidence/scene-map.json) はscene内の正確なノード名・元行番号、[spine-summary.json](evidence/spine-summary.json) は各バイナリのアニメ名・長さ・eventの短い索引、[spine-inventory.json](evidence/spine-inventory.json) は骨・slot・timelineまでの詳細。全抽出資源は [resource-manifest.json](evidence/resource-manifest.json) のPCK内path、offset、サイズ、MD5、SHA-256で固定した。

## １. キャラ選択と画面の小さい動き

PCK内のpathはすべて `res://` を付けて使う。下表のscene名にある `{c}` は表の小文字キャラIDで置き換える。

共通scene: `scenes/screens/character_select_screen.tscn`。大きい背景の親は `AnimatedBg`。キャラごとのscene: `scenes/screens/char_select/char_select_bg_{c}.tscn`。Spineノードはすべて `SpineSprite`、子に `NSpineAutoPlayer`。資源は `animations/character_select/{c}/characterselect_{c}_skel_data.tres` → `characterselect_{c}.skel.import` → `.godot/imported/characterselect_{c}.skel-*.spskel`。

| キャラ | 収録・runtime再生される名 | 元アニメの長さ | 動く部位・別レイヤーの確認 | sceneの具体的根拠 |
| --- | --- | ---: | --- | --- |
| Ironclad | `animation`, loop | 5.333s | 本体・腕・髪・fireの骨/timeline。灰・火花のCPUParticles2Dは別node | [ironclad scene](evidence/resources/scenes/screens/char_select/char_select_bg_ironclad.tscn):49, 202, 206 |
| Silent | `animation`, loop | 11.667s | 本体・`breath`・肩・`body*`の骨/timeline。背景TextureRectと別粒子 | [silent scene](evidence/resources/scenes/screens/char_select/char_select_bg_silent.tscn) |
| Regent | `animation`, loop | 6.667s | 本体・腕・脚・eye、星座slot、星のCPUParticles2D。星座Hoverはskin切替 | [regent scene](evidence/resources/scenes/screens/char_select/char_select_bg_regent.tscn):183, 187, 236 |
| Necrobinder | `animation`, loop | 8.000s | 本体・服・鎌・骨の手/Ostyの指。`OstyFireSlot` / `HeadFireSlot`はshader付き別node | [necrobinder scene](evidence/resources/scenes/screens/char_select/char_select_bg_necrobinder.tscn):179, 334, 338, 361 |
| Defect | `animation`, loop | 13.333s | 本体・頭・neck tubes・腕・hand・fabric・orb・sparkle・shineの骨/timeline | [defect scene](evidence/resources/scenes/screens/char_select/char_select_bg_defect.tscn) |

骨名は形・動作を識別する手掛かりとして扱う。骨に名称があるだけで、画面に常時その部品が見えることまでは断定しない。時間はSpineの最大timeline終端であり、動画納品仕様の指定値ではない。

| 発生タイミング | 実在する動きと再生経路 | キャラ演技を別に作る根拠 |
| --- | --- | --- |
| 画面を開く・初期選択 | `OnSubmenuOpened` / `AfterInitialized`が選択状態を準備。選択されたsceneを追加し、Spine準備後に唯一アニメをloop再生 | 独立introアニメは未確認。既存ループから始める経路を確認 |
| 別キャラへ選択変更 | `NCharacterSelectButton.Select` → delegate `SelectCharacter`。旧背景をRemove/QueueFree、新しい`CharacterSelectBg`をInstantiate。情報パネルposition tween、選択音、screen shake | 動画を切替・開始する候補。キャラが入場して止まる専用one-shotとは確認しない |
| 既に選択中のキャラへ再操作 | `Select`は`_isSelected`ならreturn。`OnPress`は空 | 毎クリックintro再生は原挙動から導けない |
| 他のキャラから戻る | 旧sceneが破棄済みなので再Instantiateし、同じloopを開始 | 同じループの再開で説明できる |
| hover / focus / 解除 | アイコンのscale、HSV、outline、remote player iconsを更新。解除`Deselect`は`RefreshState` | キャラ本体ではなくUI制御。AI動画化の必須対象ではない |
| キャラのアンロック | `PlayUnlockCharacterAnimation` / button `AnimateUnlock`。背面マスク、選択ボタン・鍵・icon・shader等のtween | 専用キャラ背景アニメは未確認。UI側の演出を残す |
| Regent背景の星座hover | `NRegentCharacterSelectBg._Ready`で7hover領域のmouse entered/exitedを`SetSkin`へ接続 | 動画全置換するとこのインタラクションを別途扱う必要がある |
| multiplayerのready / unready | ボタン入力、待機パネル、remote iconsを更新。本人の背景に新しいreadyアニメ名は見つからない | UI状態を独立に維持 |
| 出発・画面閉鎖 | `StartNewSingleplayerRun` / `StartNewMultiplayerRun` / `OnSubmenuClosed`の画面遷移とcleanup | 背景キャラのexitアニメは未確認 |

根拠: [core-animation.il.txt](evidence/core-animation.il.txt): `NCharacterSelectButton.Select` L480、`NCharacterSelectScreen.OnSubmenuOpened` L1541、`SelectCharacter` L1923、`NSpineAutoPlayer`の準備後callback L7964。後者はアニメ数が**ちょうど１**でなければ例外、唯一のアニメをtrack0/loop=trueで再生する。

Regentの収録skinは `default`, `normal`, `amogus constellation`, `cultist constellation`, `deca outline`, `sentry constellation`, `shapes constellation`, `snecko constellation`, `spheric guardian constellation`。DLLのhover callbackとこれらのskin名の対応を確認。skin反映の画面確認は未実施。

## ２. 戦闘本体の動作

sceneは `scenes/creature_visuals/{c}.tscn`。各sceneは `NCreatureVisuals`、本体Spine node `Visuals`を持つ。主資源は `animations/characters/{c}/{c}_skel_data.tres` → `{c}.skel.import` → `.godot/imported/{c}.skel-*.spskel`。詳細参照: [ironclad](evidence/resources/scenes/creature_visuals/ironclad.tscn), [silent](evidence/resources/scenes/creature_visuals/silent.tscn), [regent](evidence/resources/scenes/creature_visuals/regent.tscn), [necrobinder](evidence/resources/scenes/creature_visuals/necrobinder.tscn), [defect](evidence/resources/scenes/creature_visuals/defect.tscn)。

### 状態と正確な名

下表は「trigger → Spine animation」。idle/relaxedはloop、cast/attack/hurt/固有攻撃はone-shot後idleへ戻る。５人のdieはone-shotで、次のidleを登録していない。全員に独立した `block` / `victory` / `revive` というSpineアニメがあるとは確認できなかった。

| 用途 | Ironclad | Silent | Regent | Necrobinder | Defect |
| --- | --- | --- | --- | --- | --- |
| 基本待機 | `Idle → idle_loop` 2.000s | 同 1.067s | 同 19.444s | 同 2.000s | 同 12.000s |
| 通常攻撃 | `Attack → attack` 1.167s | 同 0.933s | 同 1.389s | 同 1.000s | 同 1.500s |
| スキル等のcast | `Cast → cast` 1.567s | 同 1.300s | 同 1.875s | 同 0.967s | 同 1.233s |
| power | `PowerUp → cast` | `PowerUp → cast` | `PowerUp → cast` | `PowerUp → cast` | `PowerUp → process` 1.567s |
| 被弾 | `Hit → hurt` 1.000s | 同 0.733s | 同 0.972s | 同 0.833s | 同 0.733s |
| 死亡 | `Dead → die` 2.333s | 同 1.867s | 同 4.340s | 同 2.333s | 同 2.233s |
| 安息姿勢 | `Relaxed → relaxed_loop` 12.000s | 同 7.000s | 同 13.889s | 同 6.000s | 同 12.000s |
| キャラ固有 | `heavyAttack → attack_heavy` 1.533s | `Shiv → shiv` 0.700s | `sovereignBladeTrigger → attack_sovereign` 1.215s | `summonTrigger → cast_mighty` 1.667s | 上記`process` |

`Relaxed` branchの登録と商人での`relaxed_loop`再生は確定。通常戦闘勝利が`Relaxed`を発火する経路は今回の直接呼出し走査では確認できなかったため、これを「勝利アニメ」と呼ばない。

根拠: [core-animation.il.txt](evidence/core-animation.il.txt) の５人の`GenerateAnimator`: Defect L4022、Ironclad L4292、Necrobinder L4593、Regent L4895、Silent L5188。各アニメ長は [spine-summary.json](evidence/spine-summary.json)。

### どの行動から発生するか

| きっかけ | 確認したruntime経路 | 本体 / 別動作 | AI素材候補の切り方 |
| --- | --- | --- | --- |
| 戦闘を開く | `NCreature._Ready` → `HasSpineAnimation` → `Character.GenerateAnimator` →初期idle | 本体。初期死亡時はDeadを設定してtrack終端へ | idleループ。初期・終端姿勢も必要 |
| 通常攻撃・多段攻撃 | `AttackCommand.Execute` → `CreatureCmd.TriggerAnim`、カードで`WithAttackerAnim`等を指定 | 本体＋target別VFX、打撃数やタイミングはゲーム状態 | 汎用attackを1素材単位にする。カードごとに演技が別とは限らない |
| 重攻撃 | 例`Bludgeon.OnPlay`が`Ironclad.GetHeavyAnimIfApplicable` →`heavyAttack` | 剣・本体。slash slotとshaderは別 | attack_heavy＋slashのevent時間を保つ |
| Shiv | `Shiv.OnPlay`でownerがSilentなら`WithAttackerAnim("Shiv",0.2,...)` | 本体＋対象への刃VFX | shiv。通常attackと区別 |
| 召喚・Osty強化 | 例`Bodyguard.OnPlay`が`GetSummonAnimIfApplicable` →`summonTrigger`、別に`OstyCmd.Summon` | Necrobinder本体＋独立Osty・回復VFX | cast_mightyとOsty素材を分ける |
| Sovereign Blade使用 | カード`SovereignBlade.OnPlay`でRegentなら`sovereignBladeTrigger`/delay0.25、`BeforeDamage`で剣nodeのAttack | Regent本体＋独立剣。多段・全体/単体対象で処理差 | 本体演技と剣飛翔素材を分ける |
| スキル / power | 例`DeadlyPoison`, `Zap`は`Cast`、`DemonForm`等は`PowerUp` | 本体＋power/poison/orb等別VFX | castとprocess。全カード用専用演技を捏造しない |
| Defendのブロック獲得 | ５人の`Defend*.OnPlay`は`CreatureCmd.GainBlock`。確認した経路に本体`Cast`/`Block`triggerはない | block表示/獲得VFX、数値はゲーム状態 | 防御専用本体素材は現段階で必須にしない |
| ダメージを受ける | `CreatureCmd.Damage`の結果・条件により`Hit`を発火。全ダメージが必ず同じ演技を出すとは一般化しない | 本体hurt、UI・被弾VFX・shake別 | hurt短素材、割込みとidle復帰が必要 |
| 死亡 | `NCreature.StartDeathAnim` →`Dead`、現在Spineアニメ長を取得、`AnimDie` Task | 本体die。Regent/Necro等のevent・炎visibilityも連動 | die素材＋終端/復活/死亡待ちのbridgeが必要 |
| プレイヤー復帰 | `StartReviveAnim`。５人にRevive branchはなく、`AnimTempRevive`でalpha0へ0.2s→`ImmediatelySetIdle`→alpha1へ0.2s | 本体nodeのtweenとidle reset | 復活専用動画を原機能として扱わない |
| 勝利・戦闘終了 | `OnCombatEnded`はintentを隠しオーブをclear。専用`victory`は収録なし | UI/状態と既存本体 | 勝利動画の新規追加は別提案 |
| hover / target / missing Osty | selection reticle、色/scale/position tween、`AnimShake`、Osty死亡時のshake | UI/node動作、状態依存 | 既存の独立制御を残す |

呼出し横断索引は [animation-callers.json](evidence/animation-callers.json)。例カードの全文ILは [card-examples.il.txt](evidence/card-examples.il.txt)。Defend５件 L4097 / 4175 / 4253 / 4331 / 4409、Shiv L5638、SovereignBlade L5876。`CreatureCmd.TriggerAnim(Creature,string,float waitTime)`は元`sts2.xml` L3617に公開契約があり、内部は [combat-triggers.il.txt](evidence/combat-triggers.il.txt):14237の`Cmd.CustomScaledWait(min(waitTime*0.5,0.25),waitTime,...)`。**アニメ全長・ダメージまでのdelay・ゲーム速度での待ちを同じ時間と扱わない。**

### 本体に付随する炎・剣・衣服

| 対象 | 正確な接点・別node | 確認済みのイベント / 状態 | 注意 |
| --- | --- | --- | --- |
| Ironcladの剣の軌跡 | `Visuals/SlashVfxSlot`, `NIroncladVfx`、`images/vfx/slash_shader_flat.tres` | `attack`の`attack_slash_start`約0.100s、`attack_heavy`の`heavy_slash_start`約0.414s → shader step tween | 動画に剣光を焼く場合、既存slotとの二重表示とevent欠落を解決する |
| Ironcladの炎 | selection `fire`骨、別の`NGroundFireVfx` / `NFireBurningVfx`等。sceneは`scenes/vfx/fires/vfx_ground_fire.tscn`, `scenes/vfx/vfx_fire_burning.tscn` | `Inflame.OnEnqueuePlayVfx`はowner CreatureへのGroundFire＋PowerUp、`Pyre.OnEnqueuePlayVfx`はFireBurning＋PowerUp。戦闘本体に専用fireアニメ名はない | 仮面・剣・呪われた炎の特徴を保存。炎VFXを本体rigと同一資源とみなさない |
| Silentの外套・刃・毒 | 本体skelの布/腕/短剣、`shiv`。別sceneは`scenes/vfx/vfx_shiv_throw.tscn`, `vfx_dagger_spray_impact.tscn`, `vfx_poison_impact.tscn`（後２件も`scenes/vfx/`配下） | cast/attack/shivを確認。Shiv/DaggerSpray/DeadlyPoisonのtarget FXも確認。毒は専用本体`poison`アニメとして収録されていない | 毒・刃を本体動画へ恒常的に焼き込まない |
| Necrobinderの頭炎・鎌 | `Visuals/HeadBoneNode/SteppedFireMix_dark`, `ScytheVfxSlot1/2/ScytheParticles`, `NNecrobinderFlameVfx`(scriptは`NNecrobinderVfx`) | `die`開始で頭炎のnodeを非表示。`cast_mighty`に`scythe_fx1`約0.133/0.200s、`scythe_fx2`0.500s→one-shot GPU粒子restart | 火はTIMEで動くshader。鎌FXはSpine event依存 |
| Regentの従者と玉座 | 本体skelに`throne_*`, `minion_l_*`, `minion_r_*`の骨/timeline | 本体idle/attack/die等と同じskel。別の戦闘Creatureとして分離されてはいない | 本体動作素材には従者と玉座も含める。独立剣とは分ける |
| Regent通常攻撃の武器 | `Visuals/Weapons/WeaponAnim1`, `/WeaponAnim2`, `regent_weapon_skel_data.tres` | 本体`attack`の`attack1`約0.139s →それぞれ`attack` / `attack2` 0.972sをone-shot再生 | Sovereign Bladeとは別資源。両者を混同しない |
| Regent死亡粒子 | `Explosion`, arm/chest/legのSpineSlotNode下GPU粒子、`NRegentVfx` | `death_particles_start`0.069、start2 0.347、end 2.569、`explode_dead`2.604、`explode_end`3.090s | 本体dieを動画化するならevent時刻の再送または代替合成が必要 |

根拠: [room-vfx-triggers.il.txt](evidence/room-vfx-triggers.il.txt): `NIroncladVfx` L3、`NNecrobinderVfx` L184/266/289。[combat-triggers.il.txt](evidence/combat-triggers.il.txt): `NRegentVfx` L3/130/238。カードとFX生成・scene名は [card-examples.il.txt](evidence/card-examples.il.txt) と [character-effects.il.txt](evidence/character-effects.il.txt)。炎shaderの時間入力: [fire_dark](evidence/resources/shaders/vfx/vfx_stepped_shader_fire_dark.tres):378/426/515、[fire_flat](evidence/resources/shaders/vfx/vfx_stepped_shader_fire_flat.tres):350/390/475。

## ３. Osty、Sovereign Blade、Defectのオーブ

### Osty

戦闘scene `scenes/creature_visuals/osty.tscn`、本体node `Visuals`、炎slot `Visuals/Flame/SteppedFireMix_dark`。資源は **`animations/monsters/osty/osty_skel_data.tres`**（characters配下ではない）。独立したCreature・HP・生死を持ち、Necrobinder本体への一枚合成では表現を保てない。

| 状態・trigger | exact animation | 長さ | 次状態・到達根拠 |
| --- | --- | ---: | --- |
| 初期待機 | `idle_loop` | 0.667s | loop。`Osty.GenerateAnimator`初期状態 |
| `Attack` | `attack` | 1.000s | one-shot→idle。例`Flatten`はOstyをattackerにする |
| `attack_poke` | `attack_poke` | 0.533s | one-shot→idle。`Poke.OnPlay`が`WithAttackerAnim("attack_poke",...)` |
| `Hit` | `hurt` | 0.900s | idle/attack/poke/hurt等からのbranch、one-shot→idle |
| `Dead` | `die` | 1.333s | one-shot→`dead_loop` |
| 死亡維持 | `dead_loop` | 0.167s | loop。死体を消して新しい別人とみなす動作ではない |
| `Revive` | `revive` | 0.967s | one-shot→idle。`OstyCmd.Summon`の既存Ostyと復活条件、`StartReviveAnim`を追跡 |
| `Cast` | コードは`cast`を登録 | — | **このskelにcastの収録なし。実際にCastへ到達して成功するとは確認しない** |

`OstyCmd.Summon`は既存OstyならHP/maxHP処理を行い、必要条件で復活。新規なら独立Creature/nodeを追加する。`vfx/vfx_heal_osty.tscn`も別にある。Ostyが死んでいる状態でカードを使おうとした場合の`CheckMissingWithAnim`→`ShakeOstyIfDead`も確認。根拠: [combat-triggers.il.txt](evidence/combat-triggers.il.txt):5893 (`GenerateAnimator`)、`OstyCmd+<Summon>`、[card-examples.il.txt](evidence/card-examples.il.txt)の`Poke`/`Flatten`。

### Sovereign Blade

scene **`scenes/vfx/sovereign_blade.tscn`**、script `NSovereignBladeVfx`、Spine node `SpineSword`、`SwordBone/ScaleContainer`下に刀身・柄・detail・glow・粒子、別`Trail`とpath/hover hitboxがある。資源 `animations/vfx/vfx_sovereign_blade/sovereign_blade_skel_data.tres` の元skel名は綴りが **`soveriegn_blade.skel`**。

| 動作 | 確認した処理・animation | 固定素材化への制約 |
| --- | --- | --- |
| 初出/Forge | `ForgeCmd.PlayCombatRoomForgeVfx`が剣nodeを作る。`Forge(value,isNew)`は柄切替、damage値に応じた部品scale、glow/tween、炎/火花を扱う | Forgeで剣の大きさ・見た目が変化。一本の固定動画に全成長段階を閉じない |
| 待機・周回 | `NSovereignBladeVfx._Process`がOrbitProgress、path、Positionを更新。`CleanupAttack`で`idle_loop` 2.667sをloop再生 | 周回位置、剣の個数、targetはゲーム側。Spineのループと周回移動は別 |
| 攻撃 | `Attack(target)`が`attack` 1.000sをone-shot再生し、rotation/global_positionをtargetへtween。終了cleanupでidleへ | 相手位置へ向かう動きを独立に保つ。画面全体の攻撃動画にしない |
| Forge火花/斬撃 | `ForgeSparks`, `SpawnFlames`, `SpawnFlamesBack`, `ChargeParticles`, `SlashParticles`、`Trail`等 | 成長・攻撃時に個別制御される |
| 消去・owner死亡 | `OnOwnerDied`→`RemoveSovereignBlade`、scale tween/cleanup | 死亡・破棄タイミングに追従 |

資源だけに確認したアニメ: `appear`0.900s、`attack2`1.233s、`idle_demo1/2/3`10.667s、`idle_loop2`2.667s。これらを通常ゲームで必ず再生される素材として計上しない。根拠: [combat-triggers.il.txt](evidence/combat-triggers.il.txt):337 (`_Ready`)、667 (`_Process`)、800 (`Forge`)、1039 (`Attack`)、1389 (`CleanupAttack`)、1457 (`OnOwnerDied`)、[secondary-motion.il.txt](evidence/secondary-motion.il.txt):1637 (`PlayCombatRoomForgeVfx`)。

### Defectのオーブ

Defectの戦闘本体skelと、浮遊オーブ群は別。共通scene `scenes/orbs/orb.tscn`（`NOrb`）と `scenes/orbs/orb_manager.tscn`（`NOrbManager`）。個別は `scenes/orbs/orb_visuals/{type}_orb.tscn`、資源は `animations/ui/combat/orbs/{type}_orb_skel_data.tres`。Defect限定の能力と断定せず、他のプレイヤーがオーブを持つ場合もこの系統を使う。

| 種類 | 正確なループ名・長さ | 別の動作・表示 |
| --- | --- | --- |
| Lightning | `idle_loop` 0.417s | lightning攻撃はtarget側の`vfx/vfx_attack_lightning`等 |
| Frost | `idle_loop` 6.250s | `single_cycle`2.083sは収録のみ。block獲得表示・FXは独立 |
| Dark | `idle_loop` 8.333s | 蓄積/evoke数値とラベル・target別damage処理は独立 |
| Plasma | `idle_loop` 2.778s | energy状態/表示は独立。`old_opacity`2.778sは収録のみ |
| Glass | `idle_loop` 8.333s | passive/evokeのゲーム処理・数値は独立 |

`NOrb`はSpine準備後`idle_loop`をloop再生。`OrbCmd.Channel`→`NOrbManager.AddOrbAnim`がslotを置換、必要なら先頭orbをevokeしてlayoutをtweenする。`OrbCmd.Evoke`→`EvokeOrbAnim`は該当nodeを0.25sでfadeし破棄、空slotを作りlayoutを更新する。**Spineに各種`channel`/`evoke`アニメがあると命名しない**。発動のflashは共通`NOrb.Flash`→CPUParticles2D emitting。各orbモデルのPassive/Evokeと値更新・対象を、そのまま独立のゲーム処理として残す。

根拠: [combat-triggers.il.txt](evidence/combat-triggers.il.txt):1655 (`UpdateVisuals`)、1913 (`Flash`)、2222 (`AddOrbAnim`)、2314 (`EvokeOrbAnim`)、8081 (`idle_loop` callback)、`OrbCmd`のasync body。[room-vfx-triggers.il.txt](evidence/room-vfx-triggers.il.txt) の５orb model。全slot/label/particleノードは [scene-map.json](evidence/scene-map.json)。

## ４. 休憩・鍛冶・商人

### 休憩中の本人とOsty

scene: `scenes/rest_site/characters/{c}_rest_site.tscn`。Spine資源は `animations/rest_site/{c}/rest_site_{c}_skel_data.tres` → `restsite_{c}.skel.import`。Necrobinderにはさらに `rest_site_osty_skel_data.tres`、別node `Necro` と `Osty`がある。

| キャラ | 主Spine node | 収録している環境別ループ | 各ループ長 |
| --- | --- | --- | ---: |
| Ironclad | `SpineSprite` | `overgrowth_loop`, `hive_loop`, `glory_loop` | 各6.667s |
| Silent | `SpineSprite` | 同３本 | 各8.000s |
| Regent | `SpineSprite2` | 同３本 | 各8.000s |
| Necrobinder | `Necro` | 同３本 | 各21.333s |
| Osty | `Osty` | 同３本 | 各10.000s |
| Defect | `SpineSprite` | 同３本 | 各8.000s |

`NRestSiteCharacter._Ready`はCurrentActIndex 0/1/2をそれぞれovergrowth/hive/gloryに対応させ、子Spine全体へその名をloop再生する。**寝る・鍛冶・筋トレ等の選択肢ごとに本人の別演技へ切替える資源ではない。** `_tracks/light_off` / `_tracks/light_on`は各skelにありduration0のslot/照明設定。`HideFlameGlow`はlight_offをtrack1へ適用する。これは連続演技動画とは異なる。

Necrobinderの頭炎は`Necro/SpineBoneNode/NecroFire`、Ostyの炎は`Osty/SpineSlotNode/OstyFire`。shader位相を`RandomizeFire`で変える。多人数でキャラindexが一定以上ならOstyを`OstyRightAnchor`へ移し、`FlipX`はSpineのscaleXとUIアンカー等を扱う。各本人・手を一つの固定背景へ合成すると配置変更に対応できない。

| 選択肢・操作 | 実在した動き | 本体専用animationの有無 |
| --- | --- | --- |
| hover / 選択中 / 決定 | `ThoughtBubbleLeft/Right`に選択肢icon、確認bubble/reticleの表示・fade | 本体は環境別loopを継続する経路 |
| Heal/休息 | `HealRestSiteOption`の回復SFX、全画面のhealVFX/remote用別healVFX | 本体のsleep one-shotは未確認 |
| Smith/鍛冶 | `SmithRestSiteOption.DoLocalPostSelectVfx`は選んだカードへ`NCardSmithVfx`、remoteでは本人nodeへ別FXを追加 | 本体がハンマーを振る専用animationは収録・トリガーを確認できず |
| Clone / Dig / Lift | localはscreen shakeや対象FX、remoteは`NRestSiteCharacter.Shake`で本人nodeを揺らす | 同じ環境loop＋node shake |
| Kindle | fire関連VFX/SFX、`NRestSiteCharacter.Shake` | 環境loop＋状態連動FX |

根拠: [core-animation.il.txt](evidence/core-animation.il.txt):3127 (`_Ready`)、3477付近 (`HideFlameGlow`)、3633 (`ShowSelectedRestSiteOption`)、7596 (`DoShake`)。[event-rest-end.il.txt](evidence/event-rest-end.il.txt):2957 (`HealRestSiteOption`)、3483 (`Smith remote`)、8338 (`Smith local async`)。[room-vfx-triggers.il.txt](evidence/room-vfx-triggers.il.txt) の`NRestSiteRoom.AfterSelectingOptionAsync`でlocal/remote経路を確認。

### 商人

scene: `scenes/merchant/characters/{c}_merchant.tscn`、Spine node `SpineSprite`、script `NMerchantCharacter`。資源: `animations/merchant/{c}/{c}_merchant_skel_data.tres`。**skeleton_file_resは戦闘の`animations/characters/{c}/{c}.skel`を再利用し、atlasは`{c}_shop`を参照**する。顔・衣装差替えには別atlasがあることも考慮する。

全員、Spine準備後 **`relaxed_loop`をloop再生**する（上の戦闘表の同じ秒数）。Necrobinderは商人sceneにも`HeadBoneNode`/頭炎shaderと`NNecrobinderVfx`を持つ。売買ごとに本人のbuy/sell等の演技があるとは今回確認できなかった。ゲームオーバーでは `NGameOverScreen.MoveCreaturesToDifferentLayerAndDisableUi` がmerchantの本人へ **`PlayAnimation("die",false)`**を指示して前面へreparentする。

根拠: [core-animation.il.txt](evidence/core-animation.il.txt):3/17/49、[merchant resources](evidence/resources/animations/merchant/) の各tres L4、[event-rest-end.il.txt](evidence/event-rest-end.il.txt):1016以下のmerchant分岐。

## ５. イベント、死亡画面、マルチプレイ、付随UI

| 場所・動作 | 確認した接点 | 対象となる差替え範囲・未確認 |
| --- | --- | --- |
| PunchOffイベント | `PunchOff.PunchEachOther`の`Attack`/`Hit`対象は`CombatState.Enemies[0/1]`。`NCombatRoom`のVfxContainerへ`scenes/vfx/events/punch_off_vfx.tscn`を追加 | **本人の殴り合い演技ではない**。戦闘layoutを使うイベントの例だが、敵の演技は本MODの置換候補から除外 |
| TheArchitectイベント | `AnimPlayerAttackIfNecessary`が台詞に指定されたStartAttackers/EndAttackersからplayer `Attack`、相手`Hit`、characterの`GetArchitectAttackVfx`を使う | ５人の攻撃VFX差がある。NPCの固有アニメは本MOD棚卸しから除外 |
| 通常のイベント画面 | 共通`scenes/rooms/event_room.tscn`。上述例以外の全イベントに常時プレイヤーが動くとは確定しない | 動かないイベントイラストと、戦闘layoutのイベントを分けて扱う |
| 商人・休憩・イベントからのgame over | merchantは既存merchant nodeをdie再生。restは`Creature.CreateVisuals`の戦闘visualを生成しdieを直接再生、休憩本体を隠す。他roomも戦闘visualからdie | **scene差替えだけの死角**。普段の戦闘経路を経ずに本体資源を使う |
| 戦闘からのgame over | 生存/死亡のCreatureノード・visualを前面へ移し、UIを隠す | 独立「死亡画面キャラ」だけを描き直す構成ではない |
| 戦闘のremote player / pet | 同じ`NCreature`とSpine animator、HP/intent/reticle/remote状態表示・scale/hue・layout差。pet ownerと本人のlocal判定は別 | 相棒/オーブ/ターゲットを固定した映像に合成しない |
| 多人数休憩・商人 | 各player別visual、休憩flip/位置・Osty配置、remote選択bubble/FX、商人visual配列 | 一枚の全画面動画では人数変化に対応しない |
| 選択画面のremote状態 | `RefreshButtonSelectionForPlayer`はlocalならSelect、remoteは`OnRemotePlayerSelected`/icons更新 | remote切替がそのまま大背景キャラ切替になると一般化しない |
| キャラ別energy UI | `scenes/combat/energy_counters/{c}_energy_counter.tscn`、`NEnergyCounter._Process`が`RotationLayers`を回し、数値変化時に別energyVFX | 本人の身体ではない。既存のゲーム側回転・状態処理を維持する候補 |
| キャラ別カードtrail | `scenes/vfx/card_trail_{c}.tscn`、`NCardTrail/NCardTrailVfx._Process`がカードのposition/rotationへ追従、別粒子とfade | カードのUI動作。美少女化に合わせた色/形変更は任意追加scope |

根拠: [event-rest-end.il.txt](evidence/event-rest-end.il.txt):6141 (`PunchEachOther`のactor判定)、6856 (`TheArchitect.AnimPlayerAttackIfNecessary`)、1016 (`MoveCreatures...`)。[secondary-motion.il.txt](evidence/secondary-motion.il.txt):19/298 (trail)、858 (energy rotation)。全イベント/NPC/モンスター/全UIの網羅調査はしていない。

## ６. 動画生成AIの使用候補 — 存在確認から分離した制作案

A＝背景込み選択動画、B＝キャラ動作素材→透過/連番等へ加工、C＝状態依存なので独立したゲーム側動作を残す。ユーザー候補のMiniMax H3 / Seedance2.5等の適否・提供状況・透明出力は本書では検証せず、動画制作前に別途確認する。

| 区分 | 使用候補 | 制作単位・優先度 | 残す条件 |
| --- | --- | --- | --- |
| A | ５人の選択背景ループ | **最優先５本**。仮面/骨/異星人/機械という原特徴を保持し、既存loopの小さな揺れ・髪/外套/炎/機械部・背景を翻案 | UI文字/ボタンは別、Regent星座hoverを保持するかレビューで決める。素材長は生成上限とloop連結を考慮 |
| B | 戦闘本人idle / attack / cast / hurt / die | ５人×共通動作。まず1人のidle＋attackで切替/透過/割込みのPoC。**デザインレビュー後**に制作へ進む | 戦闘timeline・遷移・終端姿勢・spine event・ダメージdelayをbridgeしないまま全面置換しない |
| B | 固有heavy / shiv / sovereign / mighty / process | キャラごとに1動作。汎用attack/castと分けて生成 | 原trigger名・存在する動作を保持 |
| B | 商人relaxed / 休憩環境別loop | 商人５人。休憩は５人＋Osty×３環境の照明・姿勢差を管理 | 商人別atlas、休憩light track、flip、Osty位置、死亡fallbackを考慮 |
| B＋C | Ostyのidle / attack / poke / hurt / die / dead / revive | Necrobinderと独立素材。骨の手の構造・指・霊炎を維持 | HP/死体/復活と独立位置をゲーム側に残す |
| B＋C | Regent本体・従者・玉座、通常武器演技 | 本体の一体化したrigはまとめた素材候補。独立WeaponAnimは別素材 | event時刻・武器複数node・死亡粒子を保持 |
| C中心 | Sovereign Blade周回/攻撃/Forge成長 | 任意に刀身/炎の短い映像素材を作る。剣の移動・拡大・数・targetは独立 | 一本の固定動画でForgeの全値・多段/全体攻撃を表現しない |
| C中心 | ５種orb idle素材 / Channel / Evoke / Passive | orb模様loopの新素材は任意。channel/evoke/layout/flash/値はコード制御 | Defect本体へorb数や軌道・ダメージを焼き込まない |
| C | 火花/毒/攻撃targetFX、hover/アンロック/ready/energy/trail | キャラ変更で必要な見た目だけ任意生成。既存shader/粒子/tween主体 | ゲーム状態、UI入力、数値、targetを維持 |

本書の「素材候補数」は実装の納品本数ではない。同じSpineスケルトンで複数atlasや環境照明を使う場所があり、実装方式次第で画像部品の再利用・rig変更・連番の共用ができる。最初から全組合せを動画生成する計画にはしない。

## ７. 実装担当への制約・残る確認

1. `NCreature._Ready`は`HasSpineAnimation`がfalseだとGenerateAnimator、Spine signal接続、初期死亡track終端設定をskipする。`SetAnimationTrigger`は`_spineAnimator`がnullなら何もしない。既存５人のSpineを動画nodeに置き換えるだけでは動作triggersが届かない。
2. `StartDeathAnim`はfloat0を初期値にし、Spine animatorがある場合に死亡音・Dead・現在animation長を取得する。`AnimDie` Task自体は呼ぶが、既存５人のnon-Spine戻りdurationは0になり得る。Monster overrideまたは`min(duration,30)`の戻りを利用する箇所、death待ち・生死後処理も確認する。`StartReviveAnim`は前記fade/idle resetを扱う。根拠: [combat-triggers.il.txt](evidence/combat-triggers.il.txt):3117付近、4067、4192、4301。
3. 攻撃・death動画には元のSpine event signalがない。Ironclad slash、Necro scythe、Regent武器/粒子の時刻を代替駆動するか、ゲーム側Spine/FXの制御を保持する。eventを消して成功とみなさない。
4. `CreatureCmd.TriggerAnim`は全長完了待ちではなくゲーム速度対応のdelay契約。高fps/長い生成動画をそのまま完了待ちへ変えてゲーム行動時間を変えない。
5. PCKで収録のみ確認したもの: Ironclad `weak_loop`、Necro `nervous_loop`と`_ignore/*`、Osty `_ignore/*`と未収録`cast`branch、Frost `single_cycle`、Plasma `old_opacity`、Sovereignのdemo/第二アニメ。`weak`状態等から通常再生されると推定で補わない。
6. 専用victory/player revive/block/商人buy/sell/休憩smith/sleepアニメ名は未確認。選択ループ以外の入退場キャラ演技、全room遷移のcharacter-specific wipeの図柄も未確認。専用動画を作るなら原機能の差替えとは分けて提案する。
7. 静的runtime接点は確認したが、gameplay/マルチプレイ/速いゲーム速度/途中セーブ/復活/死亡/resize/skin hoverの画面検証は未実施。最新build差分も未確認。次段階はユーザーのキャラ案レビュー後の小さいPoCとする。

キャラ原設定の制作条件は [Ironclad/Silent](../characters/ironclad-silent.md)、[Regent/Necrobinder](../characters/regent-necrobinder.md)、[Defect/世界観](../characters/defect-world.md)。Silent/Necrobinderは元の女性設定を維持し、骨・機械・異星人の身体を通常の人間に均質化しない。
