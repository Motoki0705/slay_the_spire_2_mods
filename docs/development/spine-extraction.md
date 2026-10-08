# 元Spineデータのローカル抽出とauthoring引継ぎ

Issue [#18](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/18) の実装。骨格再利用 [#9](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/9) の前準備として、所有ゲームの**main combat skeletonだけ**を新しいローカルディレクトリへ取り出す。元の `.spskel` bytesを `.skel` として保持し、`.spatlas` JSONの `atlas_data` を `.atlas` へ戻す。既存の配布テクスチャをPNGへ形式変換できる。元ゲームへの書込み、ゲーム起動、Editor起動・購入、画像生成APIは行わない。

対象版は **v0.107.1 / 59260271 / Godot 4.5.1 / standalone PCK v3 / Spine binary 4.2.43**。別版への対応は宣言しない。[骨格再利用の調査](../research/implementation/rig-reuse.md)と[従来のPCK reader](../research/motion/evidence/pck_read.py)を入力資料にしたが、ツールはその索引、manifest、私的cacheに依存しない。

## 実行条件

- Python 3.10以上。抽出・検査は標準ライブラリのみ。
- PNG変換には **Godot 4.5.1 stable** の実行ファイルが必要。`--godot` で指定するか、PATHの `godot` を使う。自動ダウンロードはしない。
- 入力game directoryに `SlayTheSpire2.pck` と `release_info.json` が必要。
- 出力parentは既存の実ディレクトリ。出力自体は未作成とし、ゲーム内・Git working tree内・symlinkを含む出力pathを拒否する。既存の空ディレクトリも上書きしない。

リポジトリrootで実行する。下のGodot pathは検証時に既に存在した他担当の配置であり、コードに固定していない。実行ファイルを読み取り・起動するだけで、その配置を変更しない。

```bash
python3 -m tools.spine.extract \
  --game-path '/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2' \
  --character silent --context combat \
  --output /tmp/sts2-spine-silent-01 \
  --godot /tmp/sts2-tools/issue-8/Godot_v4.5.1-stable_linux.x86_64
```

Godotがない環境では、PNG化を明示的に外して生CTEXと埋込み画像を受け渡せる。

```bash
python3 -m tools.spine.extract \
  --game-path '/path/to/owned/Slay the Spire 2' \
  --character ironclad --output /tmp/sts2-spine-ironclad-01 \
  --texture-mode embedded
```

`embedded` のmanifestは `png_decode.status=not_requested` とし、PNG・画素検証の未実施を記録する。PNG modeで失敗した際に、このmodeへ自動fallbackしない。成功時は出力path、抽出資源数、page数、PNG状態、manifest SHA-256をJSONで返し、拒否・失敗時はstderrと終了code 1を返す。

## main combatの対応

`tools/spine/extract.py` の `COMBAT` が唯一の対応表。sceneの参照先と `atlas_res` / `skeleton_file_res` を照合してから `.import` のremapを辿る。basename検索や最初に現れたskeletonの採用はしない。

| character引数 | scene | main skeleton data |
| --- | --- | --- |
| `ironclad` | `scenes/creature_visuals/ironclad.tscn` | `animations/characters/ironclad/ironclad_skel_data.tres` |
| `silent` | `scenes/creature_visuals/silent.tscn` | `animations/characters/silent/silent_skel_data.tres` |
| `regent` | `scenes/creature_visuals/regent.tscn` | `animations/characters/regent/regent_skel_data.tres` |
| `necrobinder` | `scenes/creature_visuals/necrobinder.tscn` | `animations/characters/necrobinder/necrobinder_skel_data.tres` |
| `defect` | `scenes/creature_visuals/defect.tscn` | `animations/characters/defect/defect_skel_data.tres` |

各data resourceのatlas／skeletonは同directoryの `<character>.atlas`／`<character>.skel` と明示している。選択・休憩・商人等は未対応。Regentの `regent_weapon_skel_data.tres`、Osty、Orb、別nodeのVFXを本人の出力へ混ぜない。main binary自身に含まれる武器やslash attachmentはそのまま保持する。

## 出力とmanifest

```text
<new-output>/
  manifest.json
  authoring/
    <character>.skel    # .spskelのbytesを変更せずコピー
    <character>.atlas   # JSON atlas_dataのUTF-8、元の改行を保持
    <page>.png          # PNG modeのみ。atlas内のpage名とrelative pathを保持
  sources/
    release_info.json
    scenes/creature_visuals/<character>.tscn
    animations/characters/<character>/...  # data.tresと必要な.import
    .godot/imported/...                    # 元.spatlasとpage.ctex
    embedded/<page>.png.webp               # CTEX base mipのWebP bytes（PNGなら.png.png）
```

`.spskel` の元PCK pathはmanifestに記録し、その `raw_output` は `authoring/<character>.skel` とする。重複したbinaryは保存しない。scene・skeleton dataは参照とanimation mixの引継ぎ用であり、ゲームsceneやscriptを実行しない。

manifestには次を記録する。

- game path、`release_info.json` の版・commit・MD5/SHA-256、PCK pathとsize、format・engine版・flags・file base・directory offset/count。
- headerとdirectoryのSHA-256。**PCK全体のhashは計算しない**と明記する。
- 選択した各資源のPCK内path、絶対offset、size、flags、索引MD5、実読取りMD5/SHA-256、保存先。
- `.skel`、`.atlas`、raw／embedded／PNG等の出力hash、変換操作、入力との対応。
- Spine binary prefixの版、bounds、reference scale、nonessential。bone・weight・timeline全体を解析したという意味ではない。
- atlas page名、page metadata（size、scale、filter、pma等の存在する値）、元texture path、`.import`、実CTEX、埋込み画像、PNGの対応。
- Godot実行ファイルの版・SHA-256、デコードしたRGB8／RGBA8画素のSHA-256とPNG再読込み時の一致、使用したツールの内容hash。
- Editor import/save/export未検証、元Editor project・元高解像度PSDを復元していないこと。

`created_utc` とローカルpathを含むため、manifest全体は実行ごとに変わり得る。コピー・変換した各payloadのhashで照合する。これらのhashは抽出の整合性情報であり、ゲーム配布物の真正性認証ではない。

## 読取り・拒否・PNG変換

PCKは `rb` で開き、header→directoryへseekし、索引だけを保持する。対象本文は必要なrangeだけを最大1 MiBのchunkで読み、各資源のMD5を照合してSHA-256を計算する。対象資源１個は64 MiBまで。PCK全体を `read_bytes()` する処理や全展開はない。抽出終了時に入力のidentity・size・mtimeを再確認する。

pathの `..`、絶対path、backslash、drive／`res://` 以外のscheme、制御文字、空segment、重複pathを拒否する。header／directory／payloadの範囲外、directoryとの重なり、不整合なpayload同士の重なり、短い読取り、破損MD5、未知の版・flags・暗号化・removal・sparse bundleを拒否する。完全に同じrange・size・MD5を持つpayload aliasのみ許容する。

すべての処理は出力parent内の専用一時directoryで完了させる。成功後に新しい出力directoryを排他的に作り、同一filesystemのhard linkでファイルを公開する。別writerが先に作った出力や既存ファイルを置換しない。処理失敗時に一時directoryを除去し、未完成の最終出力を残さない。出力directoryはmode 0700。ゲームpathに書込む処理やDLLの抽出処理はない。

CTEXは `GST2` v1の埋込みPNG／WebP、RGB8／RGBA8だけに対応する。mipのlengthとcontainerを検査し、authoringにはbase mipだけを使う。元CTEXは全bytesを保持する。raw GPU圧縮／Basis Universal、他のpixel format、displayとstored寸法が異なるCTEXは明示的に拒否する。

PNG変換は隔離した空のGodot projectで、自作 `decode_pages.gd` の **`Image.load_*_from_buffer`** を使う。ゲームPCK・ResourceLoader・extension・DLL・sceneはロードしない。CTEXで指定されたRGB8／RGBA8へ変換し、PNGを再読込みして画素bytesの一致を確認する。rescale、回転・trimの解除、premultiply／unpremultiply、色の補正、AI描き直しは行わない。

形式の一次参照: [Godot 4.5.1 PCK reader](https://github.com/godotengine/godot/blob/4.5.1-stable/core/io/file_access_pack.cpp)、[PCK flags](https://github.com/godotengine/godot/blob/4.5.1-stable/core/io/file_access_pack.h)、[CTEX reader](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/compressed_texture.cpp)、[CTEX enums](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/compressed_texture.h)。

## authoringへの受渡しと残課題

`authoring/` の `.skel`、`.atlas`、全page PNGと、manifest・元data.tresのmix設定をauthoring担当へ渡す。atlasのscale・rotation・trim・pma等を保持しているため、独自の補正を先に加えない。`embedded` modeではPNGを揃える工程が残る。

対応版Editorでのデータimport、Texture Unpacker、画像path／縮尺の確認、保存、再export、元runtimeとの同時刻render比較は次工程。現段階では**骨・mesh・weight・モーションが完全に再編集可能／同じposeを再現できるとは確認していない**。原作者のEditor project、作業履歴、PSD layers、縮小前の高解像度画素は復元していない。prefix検査とbyte一致は完全なbinary構造検証・Editor round tripの代用にはならない。

出力の生resourceはローカル資料として扱い、GitやPRへ添付しない。MODには固有のresource path／UIDを使う。女性デザインの承認、re-skin／reweight、ゲーム導入・実プレイ確認、ライセンス判断はこのツールの完了条件に含めず、それぞれの担当工程で確認する。#9全体は閉じない。

## 通常検証の記録

2026-10-09、Python標準 `unittest` と既存Godot **4.5.1.stable.official.f62fdbde1** で実施。validatorは0回。

```bash
STS2_SPINE_GODOT=/tmp/sts2-tools/issue-8/Godot_v4.5.1-stable_linux.x86_64 \
  python3 -m unittest discover -s tests/spine -v
```

合成fixtureの33テストが通過。５人の明示対応、複数／nested page、bytes・hash・改行の保持、path／offset／size／flags／MD5破損の拒否、bounded readと非対象本文の未読取り、既存／競合出力の保持、入力変化検出、WebP／PNGのRGBA・alpha保持、壊れたWebPの失敗時rollbackを検査する。Godotの環境変数を省いた場合、decoderを使う２テストはskipとなる。

所有ゲームに対してSilentと、実際に複数pageを持つIroncladをread-onlyで抽出した。抽出PCK資源と `.skel`／`.atlas` は従来readerのseek読取りと別途byte比較し、MD5／SHA-256と全出力hashを照合した。PNG全pageで変換前後の画素一致を確認した。

| 実抽出 | 対象資源数／本文bytes | page PNG | raw `.skel` SHA-256 |
| --- | --- | --- | --- |
| Silent | 8／379,883 | 1（618×523） | `17294850ae4e0b397b4dc2733af03d2b0d53d88fa504ad69a36d68bb2bbac6b0` |
| Ironclad | 14／365,588 | 4（1000×269、632×82、260×153、17×42） | `f31952dff5790e358e1229b62dac0623db6947d7550db47df7905395c50782dd` |

原PCKは1,901,378,340 bytes。前後でPCK・release_info・exe・Spine DLLのsize／mtime／inodeとrelease_infoのhashが不変だった。最終実装での生出力は `/tmp/sts2-spine-issue18-silent-final/`、`/tmp/sts2-spine-issue18-ironclad-final/`、確認記録は `/tmp/sts2-spine-issue18-checks/` にのみ保存した。これらの一時資料がなくてもgame pathから再実行できる。

Regent／Necrobinder／Defectは対応と参照先を調査・合成fixtureで確認したが、今回の通常検証での実抽出対象にはしていない。Editor import/export、元rigの描画、ゲーム起動・実プレイ、最新版は未確認。
