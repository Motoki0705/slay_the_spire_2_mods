# 武器の剛体mesh — Issue #37

[Issue #37](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/37)。基準commitは `6b190bb82a38052c42de869211586a032140ab84`。Ironcladの死亡時に剣がS字に曲がる問題を、schema 1の明示meshで修正する。Silentの短剣、Necrobinderの鎌も同じ混合重みによる変形があるため対象に含める。**Silentの元から波打った刃、Necrobinderの曲がった鎌刃を直線へ描き直す修正ではない。元の形を保って動かす。**

担当 `weapon_rig` の実装・通常検証。validatorは0回。Windowsゲームは起動していない。修正後の実機QA、compiled rigs、overridesと配布PCKへの統合は親担当。

## 原因と採用した構成

既存の `puppet.gd` は単一body画像に12×18セル、247頂点、432三角形を作り、各頂点を近い３markerへ重み付けする。長い刃や柄は握り手から遠く、途中から足・胴・頭の重みが混ざる。死亡・攻撃でそれらが別々に動き、剣の刃も布のように曲がっていた。

`tools/assets/weapon_mesh.py` と [固定ルール](../../tools/assets/weapon-rules.json) で、次を生成する。

1. 原画像の座標で武器と握り手の輪郭を指定する。既存gridの各三角形を輪郭で切り、内外をそれぞれ三角形化する。入力多角形の辺を保持する [constrained Delaunay triangulation](https://shapely.readthedocs.io/en/2.1.2/reference/shapely.constrained_delaunay_triangles.html) を使い、刃の内外をまたぐ三角形を残さない。
2. 武器内部の全頂点を `weapon_hand` の骨へ100%固定する。変形は `p' = T_hand p` となる。現rendererの骨変換は回転と平行移動の合成なので、任意の２点間の距離と元の曲線形状を保つ。表示用の一様scaleは従来どおり。
3. **武器の外周では同じ座標・UVの頂点を複製し、身体側と武器側を分離する。** 握り手の周囲だけは手の重みを身体へつなぐ。全外周を連続面にした試作は、刀身を硬くできても靴や長衣を武器へ引き延ばしたため棄却した。
4. 分離すると、元PNGで武器に隠れていた布が欠ける。Silentの外套、Necrobinderの襟・裾に限り、**既存の隣接布のUVを延長する下地mesh** を武器の後ろへ置く。PNGへの描画、生成、inpainting、別textureの追加はない。Ironcladの剣は主に透明背景上にあり、下地を追加しない。

下地は元絵にない裏側の正確な復元ではなく、隠れていた小範囲の補間である。模様や陰影が完全に連続することは保証しない。静止時は武器に覆われること、移動後に布の大きな引き延ばしや武器の複製が現れないことを検査する。武器の形だけの数値合格を、完成した見た目の合格と混同しない。

`rig.json` の `meshes` 以外は保持する。元の `body.png`、目layer、markers、anchors、clips、secondary、rest rigには変更しない。DefectとRegentは対象外。共有renderer/schema、`compile_rigs.py`、`rig-overrides.json`、`rigs/**` もこの変更には含めない。

## 座標と生成契約

- `canvas` は1024×1536。左上が原点、+X右、+Y下、単位は原PNGのpixel。l/rは画像上の左右。Ironclad / Silentは `hand_l`、Necrobinderは `hand_r`。
- `polygon` は武器と握り手の分離境界。自由な透明背景上では余白を含め、身体に接する場所では靴・襟・布を取り込まない輪郭にする。Silentの刃は色域抽出を下書きに元画像と照合して座標を固定した。再生成時に色を推測し直さない。
- `grip_polygon` の内部は身体側も手に固定する。外側の `blend_px: 16` の帯で元の重みへ戻す。角はmitre、長さ上限は帯幅の２倍。武器の刃全体へこの帯を付けない。
- 身体の新しい頂点の重みは既存gridの重みを重心座標で補間する。新たに近い骨を選び直さない。元のgrid頂点は保持する。細分割した場所では、重みの補間と変形済み頂点の補間が厳密には同じでないため、身体の移動差も数値検査する。
- body meshのUVは頂点の元座標と同じ。下地だけは `uv = source_position * uv_scale + uv_offset` で隣接布を参照する。下地の位置は武器の元の遮蔽範囲に限定し、UVが武器を再度参照しないことを検査する。`z: -1` はキャラ内部の並びであり、ゲーム全体のZを変えない。
- 三角形と頂点の順序を固定し、座標は小数６桁に揃える。Shapely **2.1.2 / GEOS 3.13.1** のbinary wheelを使い、別版では再現性の確認なしに生成しない。これらは開発時のみ必要で、MOD実行時の依存にはならない。
- `source_sha256` が違うPNGは拒否し、どのrigも書き込む前に全入力を検査する。絵・canvas・握り手・markersが変わった場合は輪郭と結果を再確認する。別姿勢のrest画像へ流用しない。

## 入力と再生成

原PNGのSHA-256:

| キャラ | `art/<id>/body.png` |
| --- | --- |
| Ironclad | `0c8cae656fbaa59f4d5505a00ff48068dabca61faf54f7cbd512e612a032c42b` |
| Silent | `9d26d063fbd1252bbab7c4b06bed67e598919be945bbf8382512c04d742b2887` |
| Necrobinder | `1cdd3fb52e7f6aa4a9d5450ff2b0eaa1fbb6c9cba8240260db6ea28b85e119de` |

作業ブランチのrootで実行する。通常は検査のみ、`--write` を付けたときだけ３つの元rigのmeshを更新する。

```bash
uv run --no-project --with shapely==2.1.2 \
  python tools/assets/weapon_mesh.py --write \
  --receipt /tmp/sts2-autonomous/weapon_rig/mesh-receipt.json

uv run --no-project --with shapely==2.1.2 \
  python tools/assets/weapon_mesh.py

uv run --no-project --with shapely==2.1.2 --with pillow==11.3.0 \
  python tests/assets/weapon_checks.py \
  --godot /tmp/sts2-tools/issue-8/Godot_v4.5.1-stable_linux.x86_64 \
  --output /tmp/sts2-autonomous/weapon_rig/validation
```

テストは `tests/animation/run_checks.py` の実行helperを使い、原texture・実renderer・schema・motion libraryを一時stageへコピーする。独立したPCKをexportし、空のhostからロードして描画する。ゲーム、Steam mods、ユーザーの進行には触れない。入力hash、元rigのmesh以外のcanonical hash、生成器・ルール・出力hashをreceiptへ残す。

親の統合時はPRの元rig変更を取り込んだ後、親が管理するoverrideを重ね直す。

```bash
python3 tools/assets/compile_rigs.py
```

その後、親の [PCK生成・検証経路](pck-only.md) で配布物を作り、原不具合と同じIronclad死亡、３人の攻撃・被弾・死亡・復活を実機で確認する。通常buildからゲームへ自動コピーする処理は追加していない。

## 検証対象と残る制約

通常検証は、原画hash、再生成一致、schema、canvasの隙間・重複、全武器三角形の手100%重み、下地の参照範囲、８動作×101位相、attack→dieのmix、死亡保持、復活resetを含む。手・刃・柄のprobe間距離と手の変換との差を測り、身体には透明部・武器・手首帯を除いた12px間隔の可視点も使う。静止画像の前後差と、実際に描いた攻撃・被弾・死亡も確認する。

数値と目視の固定結果は [検証証拠](../../tests/assets/weapon-evidence/README.md) を参照。原不具合のゲーム画像は親QAの `ironclad-game-over-later.png` をローカルで確認し、このPRへコピーしない。

衝突判定、床に合わせた武器の着地、IK、新しい死亡キー、ゲームのVFX付着点は追加しない。単一画像で隠された部位や前後関係を完全に復元するrigではない。大きい新規キーやmarkersのoverrideを追加したときは、この検証と実機の見え方を再確認する。
