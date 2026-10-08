# 動作調査の証拠・再現方法

対象は2026-10-08にローカルで確認した公式配布v0.107.1 / commit59260271 / 2026-06-18。ゲーム原本は変更せず、起動もせずに読んだ。PCKはGDPC v3 / Godot4.5.1、file_base112、directory_offset1899867440、15658レコード。ヘッダ・索引読み方は [キャラ調査の引継ぎ](../../characters/ironclad-silent.md) と [Godot4.5公式PCK reader](https://github.com/godotengine/godot/blob/4.5/core/io/file_access_pack.cpp) に基づく。

## ファイルの役割

| ファイル | 用途 |
| --- | --- |
| `pck-index.json` | 全レコードのpath/offset/size/MD5/flagsという索引のみ。全アセット本文を展開したものではない |
| `resources/**` | 関係scene/tres/importと24Spineバイナリ等、選別した公式資源。PCK内の相対pathを保持 |
| `resource-manifest.json` | 全選別資源の元path/offset/size/MD5と抽出後SHA-256 |
| `source-binaries.json` | DLL/XMLとインストール直下のrelease_info.jsonのサイズ・SHA-256。IL証拠の版を固定 |
| `release_info.json` | ゲームインストール直下の版情報の未改変コピー。PCKレコードではない |
| `scene-map.json` | scene中の外部参照と動くnodeの正確なname・元行番号 |
| `spine-summary.json` | バイナリのexact animation name・duration・event・skinの短い索引 |
| `spine-inventory.json` | 上記にbones/slots/各timelineの骨・slot・eventを加えた解析結果 |
| `core-animation.il.txt` | 選択screen/button/Regent hover、商人、休憩、Spine auto player、５人GenerateAnimatorと一般CreatureAnimator |
| `combat-triggers.il.txt` | NCreature、Osty、orb、SovereignBlade、CreatureCmd/OstyCmd/OrbCmd/AttackCommand等 |
| `room-vfx-triggers.il.txt` | Ironclad/Necro VFX、combat/rest/merchant room、orbモデル |
| `card-examples.il.txt` | 原行動に接続する代表カード。５Defend、５Strike、Shiv、Blade、召喚/毒/炎等 |
| `event-rest-end.il.txt` | PunchOff/TheArchitect、game-over、休憩optionとasync本体 |
| `secondary-motion.il.txt` | Forge、orb基底、power、energy UI、カードtrail |
| `character-effects.il.txt` | GroundFire/FireBurning、PoisonImpact、ShivThrow、DaggerSprayImpactの動作接点 |
| `animation-callers.json` | ゲームDLL全体の関連直接呼出し横断索引。方法/token/RVA/calls/ldstrの抜粋。未使用資源や反射経路まで到達を保証しない |

ILはDLLをロード実行せず、dnfile0.18.0/dncil1.0.2で読み取った。メソッドごとに完全名、MethodDef token、RVA、命令offsetを保持する。`IL_`のoffsetはdncil出力値。token解決の`.?`は一般型/TypeSpecをこの小さいreaderが完全展開しない箇所であり、型の完全なdecompileとは称さない。アニメ・trigger名はldstrとSpine解析を照合した。

Spineの`.spskel`実体は先頭からSpine binary。公式 `@esotericsoftware/spine-core` **4.2.43**の`SkeletonBinary.readSkeletonData`で読み、全24本の解析に成功した。スケルトン自身の版は4.2.40 / 4.2.43（個別JSONに記載）。根拠は [Esoteric Softwareの4.2公式parser](https://github.com/EsotericSoftware/spine-runtimes/blob/4.2/spine-ts/spine-core/src/SkeletonBinary.ts)。atlasには仮の1×1regionを供給して**名称・timeline・eventの解析だけ**を行い、テクスチャ・シルエット・姿勢のrenderは行っていない。durationはtimeline最大終端で、実ゲームの攻撃delayとは異なる。骨名やtimelineの存在だけで視覚的な部品の意味を確定しない。

## 再現

作業dirは `/home/kamimura/projects/slay_the_spire_2`。ゲーム本体は `/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2`。以下は調査用依存ツールだけを`/tmp/sts2-motion-tools`へ置く。ゲームのインストール・原本変更・ゲーム起動は不要。

```bash
uv venv /tmp/sts2-motion-tools/venv
uv pip install --python /tmp/sts2-motion-tools/venv/bin/python dnfile==0.18.0 dncil==1.0.2
npm install --prefix /tmp/sts2-motion-tools @esotericsoftware/spine-core@4.2.43 --no-audit --no-fund
python3 docs/research/motion/evidence/pck_read.py index
node docs/research/motion/evidence/spine_inventory.mjs
python3 docs/research/motion/evidence/build_catalog.py
```

`pck_read.py save <path>`で必要なレコードだけ保存できる。`read <path>`はstdoutへ返す。flags0以外を拒否し、本文MD5を元索引と照合する。`.skel/.atlas`の実体は同名`.import`中の`.godot/imported`pathを辿る。PNGやatlasの画面renderは別段階。

`dll_il.py '<型名regex>'`は関連型とそのnested async bodyをdisassembleする。`dll_il.py calls '<呼出しregex>'`は直接呼出し横断索引を返す。既存証拠ファイルを再生成すると文書のL番号が変わることがあるため、MethodDef token/RVA/IL offsetも照合する。

## 検証と限界

選別資源198件、計4,588,725bytes（PCK本文のみ）を元MD5と照合。24Spineバイナリ、50scene。大きいPNG/音声の全量抽出、全モンスターのアニメ解析、Godot render、ゲームUI操作は行っていない。研究文書・JSON・IL・索引を含む保存容量は約11MB。

この照合は資源を正しく読んだことの検証であり、MODの動作テストではない。実プレイ時の到達、最新build、生成素材のloop継目・透明化・実装互換性は未検証。名前が収録されているだけのアニメと、コード側の通常triggerに接続するアニメは [inventory.md](../inventory.md) で区別する。
