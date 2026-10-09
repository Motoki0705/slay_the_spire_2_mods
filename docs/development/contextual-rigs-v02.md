# 場面別rig v0.2 — Issue #53

[Issue #53](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/53) の制作実装。基準は `b80bb5b790918dc764bb11ee062bfff919e6338c`。画像は親の制作採用に基づく入力であり、このrig担当がユーザーの個別承認を取得したものではない。Silent本人のv05デザインのみ既存のユーザー承認がある。選択画面のMiniMax H3 / 768P動画、画像生成、production scene、ゲームへの導入は親の担当。

## 場面の分離

`art/<character>/{combat,merchant,rest}_rig.json` は、その場面のPNGを左上原点のsource pixelで計測した完全なschema 1 rig。新たな `canvas`、９marker、足元または座席の `origin`、握り手、顔・掌・靴の剛体領域、武器の輪郭とVFX anchorを記録する。`rig.json` と選択用の原画を変更せず、歩く絵を戦闘や休憩へ変形して流用しない。

全15場面は `surface` と `motion_profile: contextual_v02` を持つ。呼吸、商品を見る所作、座位の手・髪はruntimeの場面profileを使う。接地した武器や肘掛けの手を固定する場面だけ、新座標で作った明示ambient clipへ同じ呼吸・手・髪の演技を接続する。攻撃・被弾・死亡は、その絵で見えている範囲へ動きを抑えた局所clipを持ち、1536pxのcanvasから単位を換算する。明示clipは計測した手名を使い、legacyの左右交換に依存しない。元driverの位相・mix・速度・死亡待ち・復活・音・eventは編集しない。

`rig-overrides.json` の共通/全場面の古い握り手と、旧姿勢のclip・休憩origin・throne・目layer・VFX座標を撤去する。新しい場面の設定はそのsource rigだけが所有する。旧selectionに必要だった設定は `select` へ移す。コンパイル結果とsource rigの辞書一致を検査し、古いoverrideの混入を防ぐ。

## 剛性と隠れ面

武器は既存 `weapon_mesh.py` の `generate_mesh` / `generate_underlays` を再利用する。Shapely 2.1.2 / GEOS 3.13.1に固定し、元PNGを一切書き換えない。別textureになった新poseの輪郭は新たに計測する。柄・刃・握りを同じ骨へ100%固定し、刀身が胴・足の重みに引かれないようにする。

顔・掌・靴は輪郭の内側を１本の骨へ固定し、周囲の帯で元の重みへ戻す。武器の切れ目以外には開いた境界を作らない。靴の接地点をroot配下の足へ固定する。顔の目・口の間隔も変形させず、向きは頭の回転で表現する。

武器の裏に必要なごく小さい布・脚は同じPNGの隣接領域をUV参照する。これは描かれていない裏面の正確な復元ではない。大きく腕を開く、指を個別に折る、二手持ちの支え手を離す動きには別の絵が必要なため、この実装では無理に作らない。静止時の元textureとの描画差、動作時の二重の刃・穴・手首を目視する。新poseへ合わない旧目layerは使わない。

## 再生成と検証

親の画像を別worktreeから読む場合も、出力先はこのworktreeに限定する。入力PNGのhash、canvas、RGBAを検査し、すべての入力が通った後でrigとreceiptを書き出す。透明pixelに残るRGBは背景として扱わず、alphaで合成する。

```bash
uv run --no-project --with pillow==11.3.0 --with shapely==2.1.2 \
  python tools/assets/build_contextual_rigs.py \
  --input-root /path/to/art-worktree --output-root "$PWD"
python3 tools/assets/compile_rigs.py

uv run --no-project --with pillow==11.3.0 --with shapely==2.1.2 \
  python tests/assets/contextual_checks.py \
  --input-root /path/to/art-worktree \
  --godot /tmp/sts2-tools/issue-8/Godot_v4.5.1-stable_linux.x86_64 \
  --output /tmp/contextual-rig-checks
```

`--contexts silent/combat silent/merchant` で変更した入力だけを描画できる。pipelineの入力保護を確認済みで、画像・座標だけを変更した回は `--skip-guards` を使う。画像未到着を成功扱いせず、引き継ぎmanifestのready項目だけを制作する。

通常検証はsource PNGのbyte/hash保持、途中入力不正時の無書込み、重複context拒否、三角形の面積と重み、実schema、実puppetの51位相、剛体probe・接地点・２点間距離、mix、死亡保持、復活/reduced-motion復帰を含む。通常Godotで一時PCKをexportし、loose assetのない空hostから実描画する。ゲーム抽出物・追加DLL・Spine Editorは使わない。

## 場面固有の接点

| 場面 | 接点と制御 |
| --- | --- |
| Ironclad combat | 同じ柄を握る両手と刀身を一体に保つ。支え手を離す絵はないため、castでも柄を離さない |
| Ironclad merchant / rest | 剣の手をroot配下へ置き、刃先を預けた位置へ固定。空いた手と胸・頭で演技する |
| Silent | 短剣の波打った形を保持。新bladeの全縁をsource alpha/色面で計測し、胴や脚へ残像を残さない |
| Regent combat / merchant | 元throne PNGを独立したroot meshで登録。combatは幾何をX反転して右向きの人物に合わせる。肘掛けの手と座面を固定。独立剣のbindingは追加しない |
| Regent rest | 新座位の本人だけ。throne/旧body/旧目layerは含めない |
| Necrobinder | combatの握りはhand_l、新restはhand_r。刃先と石突きを区別し、head_fireも新髪の上端から取り直す。商人/休憩の柄はroot配下で固定 |
| Defect | レンズ、顔、前腕の金属板、脛/足を剛体化。restの工具は握りへ固定。Orbの数や配置をrigへ焼き込まない |

休憩originは各新画像のhip。表示高はIronclad 820 / Silent 760 / Regent 540 / Necrobinder 720 / Defect 760。旧座席基準と新人物の寸法を用いた初期登録値であり、実ゲームの座席・手足との重なりは親が確認する。

Regent combat/merchantのbodyは元のsource pixel座標を保ち、throne側のmeshだけを変換する。合成全体の表示高が旧300相当になるよう、bodyのdisplay_heightは186/195。originは登録した玉座の担ぎ手の足元なので、bodyのbitmap外へ出る場合がある。人物PNGの縮小・再保存や、選択用throne素材の変更は行わない。

Necrobinderの元subtree pathはcombatの `Visuals/HeadBoneNode/SteppedFireMix_dark`、２つの `ScytheVfxSlot`、merchantの `SpineSprite/HeadBoneNode/SteppedFireMix_dark`、restの `Necro/SpineBoneNode/NecroFire` を保つ。頭の倍率は従来の0.6 / 0.4 / 0.65。実binding leaseで位置追従、倍率の重複適用防止、元position/scaleへの復帰、対象外Osty/Weapons/Orbsの不変を合成treeで検査した。

## 検証結果と媒体

**15場面すべてを通常Godot 4.5.1で描画・確認した。** 元PNG 15件のhashは引き継ぎと一致し、書換えなし。専用source rig 15件とcompiled rigの内容は一致し、selection 5件はcompilerのsurface tag以外を旧出力と比較して一致した。新sourceを再生成しても、検証済み出力のhashが一致する。

[15場面の媒体索引](../../tests/assets/contextual-evidence/README.md) と [入力・出力・数値・媒体hash](../../tests/assets/contextual-evidence/validation.json)。戦闘の静止一覧はidle/hurt/attack/die、商人・休憩はambientの２位相/attack/die。短いanimated WebPは実rendererの24frameを並べた所作確認用で、ゲーム実録や元driverの実時間を測った映像ではない。

数値検証は各動作51位相、武器・顔・指・靴の剛体probe、２点間距離、固定接点、mix、死亡保持、復活とreduced motion復帰を含む。probeは元PNGの不透明な画素上に置く。静止時の元描画から16階調を超えた差は、1024×1536画素中で最大3画素（許容20未満）。renderer丸め以外に下地が元の見た目を描き換えないことを確認した。境界から刃がはみ出して二重に見えた初期案、鎌の下地が透明部分へ出た初期案は採用せず、最終の輪郭と下地へ修正した。

既存Python compilerテストは4件中3件成功、1件が `tests/animation/test_compile_rigs.py:62` の「全rigがlegacy_v01」という旧素材前提で失敗する。新しい正しい集合はselect 5件がlegacy、他15件がcontextual。これは本Issueの所有外ファイルなので変更せず、親へ受入更新を引き継いだ。compiler自体は20rigの出力を完了し、新15sourceとの一致検査は成功している。

validatorは指定・試行・完了とも**0回**。Windowsゲームは起動していない。座席・VFXの実ゲームでの位置/倍率、独立Osty/剣/Orbとの重なり、実際のカード/event時刻、死亡・復活のゲーム経路は親の統合QAが残る。新PNGと選択動画はこのPRに含めず、親の #48 素材と合わせて取り込む。大きな腕の解放、指・瞼の個別作画、新しい死亡専用画像は追加していない。
