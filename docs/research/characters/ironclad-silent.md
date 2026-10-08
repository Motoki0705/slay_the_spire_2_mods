# Ironclad / Silent — 一次資料に基づく調査

> 制作提案の扱い: この調査時点の原型維持の提案は、後のユーザーレビューで擬人化不足と判断された。公式事実は資料として採用し、外観の現行方針は [v0.3](../../design/characters/review-v03.md) を参照。

確認日: 2026-10-08。対象はこの二人のみ。公式の事実、画像からの観察、本MODの提案を分ける。正式画像・動画・MODの実装は行っていない。

## 結論

Ironclad は「銅色の仮面を着けた女性剣士」だけでは足りない。StS2 の選択説明は、最後の兵士で、本人の意思に反して剣と炎で敵を粉砕すると明記する。金銅色の閉じた仮面、橙色の眼光、重い鎧と長剣、灰色の髪の断片、怒りと呪われた炎が核となる。

Silent は公式に女性として扱われている。女性化を追加する対象というより、既存の女性狩人をポップな画風へ翻案する対象である。頭蓋骨を小さな髪飾りにせず、緑の大きな外套、長い頭蓋骨と角、包帯、波打つ短剣、骨の背面装飾、毒と無言の狩りを保つ。

二人とも人型だが、調べた一次本文は生物学的な種族を「human」と確定していない。人型だから通常の人間へ変換すべきだ、とは解釈しない。仮面を外して美顔を描くことは、公式が重視する顔の隠れた世界と、両者の識別性を失わせる。

## 版と証拠の扱い

| 資料 | 何の証拠か | 限界 |
| --- | --- | --- |
| [2024-10 Neowsletter #3](https://www.megacrit.com/news/2024-10-02-neowsletter-issue-3/) | Casey Yano による StS1 のデザイン意図、Marlowe Dobbe による StS2 の画風方針、StS2 初期コンセプトとアニメーション | 採用前の案を含む。現在の衣装図として一括採用しない |
| [2025-03 Neowsletter #8](https://www.megacrit.com/news/2025-3-12-neowsletter-issue-8/) | 開発時点の Ironclad 全身、Marlowe のポーズ参照から公式絵へ変わる GIF | 鳥は Quest の随伴者。Ironclad 固有の常設相棒ではない |
| [2025-05 Neowsletter #10](https://www.megacrit.com/news/2025-5-15-neowsletter-issue-10/) | Anthony による Silent の新しい Sly 設計 | 2025 年の開発紹介。カード数値の現行性を保証しない |
| [2025-11 Neowsletter #16](https://www.megacrit.com/news/2025-11-13-neowsletter-issue-16/) | Casey による Ironclad の仮面保持の回答 | 短いユーモラスな Q&A。未記載の機構を補わない |
| [2026-02 発売日告知](https://www.megacrit.com/news/2026-02-19-release-date-trailer/) | 発売期の５人の頭部／上半身、協力戦の動作 | 広報映像。正確なゲーム build は未記載 |
| [現行 Steam ストア](https://store.steampowered.com/app/2868840/Slay_the_Spire_2/) | 2026-10-08 現在掲載されている全身の宣伝スクリーンショット | 公開画像の撮影 build は未記載。最新版の実プレイキャプチャとは称さない |
| ローカル公式配布 PCK | キャラ説明、代名詞、Timeline の文章、Ancients の台詞、選択アイコン | **v0.107.1 / commit 59260271 / 2026-06-18**。2026-10 の最新 build ではない。画面で実際に表示されるところまで起動確認していない |

ゲームインストール直下の `release_info.json` は `version: v0.107.1`、`commit: 59260271`、`date: 2026-06-18T15:43:56-07:00`。この版情報ファイルは PCK 内ではない。選択キー・Timeline キーの原文は PCK から読み、キャラごとの `official/game-assets/*-localization-{eng,jpn}-v0.107.1.json` に保存した。全文書のコピーではなく、関係するキーを未改変で選択した派生資料である。元リソースの MD5 を照合済み。

公式ページの Community / Fan Art 欄、表紙投稿、コスプレは公式キャラクター原画の根拠に採用していない。#3 の Ironclad Demon Form ファンアートも未採用。

## Ironclad の設定

| 論点 | 一次資料が述べる内容 | 根拠 |
| --- | --- | --- |
| 出自／立場 | Ironclads の最後の兵士 | ゲーム `characters.json` → `IRONCLAD.description`。日本語は「アイアンクラッド族、最後の兵士」 |
| 性別の扱い | 英語の主語 `he`、目的語 `him`、所有 `his` | 同 `IRONCLAD.pronounSubject / pronounObject / pronounPossessive`。MOD の女性化は今回の改変 |
| 種族 | Ironclads という集団／一族に属する。調べた本文では人間・悪魔等の生物種を確定しない | 「族」を独立した異種族の証拠にも、普通の人間の証拠にも読み替えない |
| 戦い方 | 剣と炎で敵を粉砕するが、本人の意志に反する | 同 `IRONCLAD.description`。英語の `against his will` と日本語訳の両方を確認 |
| 人物像 | 痛みより目前の敵の死を優先する短い独白。仲間にはまだ自分が必要だ、とも述べる | 同 `IRONCLAD.aromaPrinciple / eventDeathPrevention`。独白の用途は実プレイ未確認 |
| 元のデザイン意図 | 呪われた騎士と悪魔のエネルギー。顔が見えない威圧感、重い攻撃の感覚 | #3、Casey の StS1 制作回顧。StS1 の最終ポーズは別作品に触発されたと本人が説明するが、その別作品を MOD の参照にはしない |
| 仮面 | ironclads は噛むことで保持する、と Casey が回答 | #16 Q&A。留め具・魔法の吸着・常に外れる等の追加設定は本文にない |

「悪魔の力を楽しむ熱血英雄」「王族」「人々を救うためだけに登る」「仮面の下の顔が美しい」は、今回確認した選択説明からは導けない。

## Silent の設定

| 論点 | 一次資料が述べる内容 | 根拠 |
| --- | --- | --- |
| 出自／立場 | 塔の外から来た狩人 | ゲーム `characters.json` → `SILENT.description`。英語は `huntress` |
| 性別の扱い | 主語 `she`、目的語 `her`、所有 `hers` | 同 `SILENT.pronounSubject / pronounObject / pronounPossessive`。#3 でも Casey は `her` を使用 |
| 種族 | 女性狩人であることは確認できるが、生物種は未確定 | 骨を身に着けるという意図を、本人がスケルトン／リッチである設定へ変換しない |
| 武器／技能 | ナイフと毒で立ちはだかる者を仕留める | 同 `SILENT.description` |
| 人物像 | 狩り・証明・居場所を求める独白。生き延びて狩りを続けたい。英語では sisters を思う | 同 `SILENT.aromaPrinciple / eventDeathPrevention / goldMonologue`。日本語 `goldMonologue` は同胞に「証」を認められる、という訳 |
| 元のデザイン意図 | 骨をまとう怖い暗殺者。外套の下が見える頃には相手が暗殺されている、という隠密性。波形の Kris dagger | #3 の StS1 制作回顧。骨をまとった狩人と解釈する根拠であり、骨格の身体という意味ではない |
| 新作の設計 | Sly は捨てられたとき無料で自動使用する。捨て札を利用する戦い方を増やす | #10 の Anthony による説明。敏捷さのゲーム的根拠として使用し、性格の「色気」に結び付けない |
| 行動 | 影から出てきて、戦闘の挑戦から逃げながら武器を盗む場面もある | `ancients.json` → `NONUPEIPE.talk.SILENT.0-1.char / TANX.talk.SILENT.2-1.char`。場面の地の文。すべての場面で臆病だ、とは一般化しない |

静かさは女性の従順さの記号ではない。「妖艶な暗殺者」「人を誘惑する」「肌を見せて敵を欺く」は、この調査の一次根拠にはない。

## 視覚の観察と保存すべき形

観察は文章設定からの推論ではなく、`view_image` で画像そのものを確認した結果。

| 要素 | Ironclad | Silent |
| --- | --- | --- |
| 大きい輪郭 | 踏ん張った足、両手で長剣を支える構え、張った肩と腕、鎧の厚み | フードと外套が作る緑の大きな塊。戦闘では斜めに張り、店では身体を細長く包む |
| 頭部 | 金銅色〜橙褐色の尖った仮面。下へ絞られる面、細い橙色の眼光、銀灰色の髪の断片 | 淡い骨色の長い鼻先と眼窩、後方へ伸びる一対の角。フードと顔を覆う頭蓋骨。緑色の眼光 |
| 衣装 | 金銅色の肩当て・前腕／腰／脚の装甲、暗い胴、赤褐色の下衣。現行資料で大きな赤い肩布は確認しない | 緑〜青緑の覆い、灰色の内側の布、手足の淡色の巻き布。細い灰色の髪束が頭骨の脇から出る。背面には長い骨／脊椎形の装飾 |
| 手持ち | 明るい銀色の長く幅のある剣、暗い柄と特徴的な鍔 | 明るい青白色の波打つ短剣。開発 GIF には左右の手に一振りずつ。現行 Steam 戦闘画面も短剣と大きい外套の動きを確認できる |
| 動きの読め方 | 足で支え、手で剣を扱う重量。炎の VFX が身体全体を包む場面 | 手と短剣が先に走り、外套と背面の骨が追う。伸ばした腕と身体を外套が再び隠す |
| 表情の代替 | 仮面の角度、眼光、肩と握り、剣の傾き | 頭骨の角度、緑の眼光、手首と短剣、外套の畳まれ方 |

剣の素材・鎧の厳密な合金、髪の正確な長さ、角の生物学的分類、仮面下の眼や顔は、この画像観察だけで確定しない。背面の骨を短い三つ編みと取り違えない。

## 短い character bible — 今回の制作提案

ここからは公式設定そのものではなく、本MOD向けの翻案方針。

**Ironclad:** 元の閉じた金銅色の仮面と銀灰色の髪、橙の眼光、重い実用鎧、長剣と踏ん張る構えを持つ、力強い女性の最後の兵士。女性化は同じ装備が乗る身体の造形と必要なら軽い髪の整理で示す。胸や腰を露出させず、仮面を額の髪飾りに移さない。鮮明な色面、鎧の大きい形、剣と足の明快なリズムでポップにする。怒りと本人の意志に反する炎が残るよう、愛想のよい笑顔・ウインク・誘惑ではなく、握りと肩の緊張、仮面の小さな傾きで活気を出す。

**Silent:** すでに女性である外来の狩人を、骨の頭部・緑の外套・包帯・波形短剣を維持したままポップに描く。顔と身体を外套が隠す量を保つ。細い身体そのものより、動いて開き、閉じて潜む外套の形で軽さを示す。狩りの集中、無言の観察、短剣のすばやい取り回しが個性。親しみは小さな首の動き、すばしこい重心移動、外套の弾みで出す。人間の素顔、長い派手な髪、コルセット、脚を見せるドレスへ置換しない。

両者の女性的な記号を揃える必要はない。Ironclad は鎧と重量、Silent は外套と隠密性の違いを優先する。声・表示代名詞を変更する場合も、外観だけから性格や出自を捏造しない。

## 仮案 v0.2 への訂正・注意

- Ironclad の「暗い赤の短い束ね髪」は公式画像の銀灰色の髪から離れる。本案固有の髪型としても、現行の核を守る目的には不要。灰色を基準に戻す。
- 「赤い肩布」は StS1 の赤い布のイメージ／古い開発絵を現行 StS2 へ持ち込むおそれがある。現行の金銅色の肩装甲と暗い胴を優先する。
- Ironclad を単に「悪魔の力を宿した騎士」として陽気な力自慢へ変えると、StS2 が明示する本人の意志に反する戦いを落とす。
- Silent の「灰色の短い三つ編み」は、選んだ現行資料から長さ・髪型を確定できない。背面の長い骨の装飾も独立して維持する。
- Silent の骨の仮面とフードを残す方針は支持できる。ただし元々女性のため、性差を強める改造より画風整理を中心にする。
- 「ポップ＝個性ある表情」を、人間の露出した顔の表情だけへ限定しない。仮面のある身体の動きで表現できる。

## 物語のネタバレを含む補足 — 外観参照への入力は必要範囲だけ

以下はローカル v0.107.1 `epochs.json` の文章。時系列の全貌と最新追加分は未検証。未完成の `*_EPOCH8/9` に `TODO` があるため、先の結末は作らない。

**Ironclad:** `IRONCLAD4_EPOCH.description` は、Ironclads と Valleyguard が何世紀も戦い、野心を持った若い ironclad が禁じられた境界で sacred “Demon” と取引したと述べる。`IRONCLAD3` は契約の炎が血を流れ、敵の集団だけでなく馴染みある青銅装備の戦士の群れも焼かれると描く。`IRONCLAD2` は呪われた血と本能によって理性とアイデンティティを失った戦士とする。`IRONCLAD5/6` は Heart を倒したあと Contract が Blight を吸収し、戦士と Blight が燃え続ける展開を描く。`IRONCLAD7` では Demon が自分の death puppet に Architect を殺せと命じる。

Ancients の場面では `VAKUU.talk.IRONCLAD.0-1.char` で本人が何をされたか問い、`VAKUU.talk.IRONCLAD.2-1.char` で Architect の次にはお前を殺す、と抗議する。これは本人の声として、単なる好戦性に縮めないための有用な資料。NPC が発する評価は、その NPC の台詞として扱う。

**Silent:** `SILENT6_EPOCH.description` は Foglands を苦しめる haunter を狩り、その頭蓋骨を Sisters が儀式的に彼女へ被せると記す。タイトルは **Nemesis**。したがって頭蓋骨は個体の骨格の顔でも、単なる流行の小物でもなく、狩りと儀礼に結び付いた装具として扱うのが証拠に合う。見た目の獣種名をヤギ／鹿と確定しない。

`SILENT5` は特製の毒で Heart を止め、Heart の一片を戦利品として持ち帰ると記す。`SILENT2` は三世紀以上会わなかった fourth one に他の sisters が満足せず、本人はより大きい戦利品で自分を証明しようとする。`SILENT3` ではその Heart の欠片が持つ Blight に侵され、欠片を海へ捨てても治らない。`SILENT1` は Spire 再開を聞いて The Capital へ船で向かい、再び塔へ入る。長命や一度目の死の詳細を、この断片だけから不死・エルフ等へ補完しない。

親のレビュー用の短い外観説明には、この節の全展開を入れず、呪われた炎／儀礼の頭蓋骨／無言の狩人という外観と動作に必要な特徴を使う。

## 絵師・画像AIへ渡す参照の選定

キャラごとの [Ironclad 資料索引](../../../art/references/ironclad/README.md)、[Silent 資料索引](../../../art/references/silent/README.md) と `sources.json` に、全ファイルの来歴と派生関係を記した。同じ GIF の複数フレームは独立した原画の点数に数えない。

Ironclad は現行 Steam 協力戦の前景左側の全身、共通 lineup の左端、公式ポーズ GIF の**キャラ絵だけになった frame040**を主参照にする。開発過程の実在の人間の顔を生成AIのキャラ顔参照として渡さない。Silent は現行 Steam merchant の全身、共通 lineup の左から２番目、公式 animation の frame055 / frame080 を主参照にする。2024 の初期コンセプト集は方針の変遷を見る補助資料とし、複数の案を合成して現行設定にしない。

## 未確認

- 両者の生物学的な種族、仮面下の顔と眼、正確な身長・年齢。Silent の三世紀の断片から具体的な年齢を算出しない。
- 2026-10-08 現在の最新ゲーム build と、ローカル v0.107.1 の物語差分。
- ゲームに収録された各独白／Ancient 台詞がすべて現在の通常プレイで到達・表示可能か。PCK 収録は確認したが起動実験は未実施。
- StS1 のキャラ選択／Sensory Stone の本文を直接取得できていない。今回の StS1 設定の根拠は公式の制作回顧に限定した。第三者 Wiki の転載本文は根拠にしていない。

## PCK 読み取り引継ぎ — 動作箇所の別担当調査用

全動作の棚卸しは本調査の範囲外。以下は重複した全アセット展開を避けるためのアクセス手段。

原本: `/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.pck`。先頭 magic `GDPC`、PCK version **3**、Godot **4.5.1**、pack flags **2**。header byte24 から little-endian uint64 の file_base (**112**) と directory_offset (**1899867440**) を読む。directory に uint32 file_count (**15658**)、続いて各レコード: uint32 path_length → UTF-8 path（末尾 NUL を除く）→ uint64 offset → uint64 length → 16-byte MD5 → uint32 flags。原本がスタンドアロンのため絶対 file offset は `file_base + offset`。本文は非暗号レコードのみ扱い、MD5 を検証する。

形式の一次参照: [Godot 4.5 `file_access_pack.cpp`](https://github.com/godotengine/godot/blob/4.5/core/io/file_access_pack.cpp) の `PackedSourcePCK::try_open_pack`。ゲーム原本を変更しない。

```python
from pathlib import Path
import struct, hashlib, re

task_pck = Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.pck')
with task_pck.open('rb') as task_file:
    assert task_file.read(4) == b'GDPC'
    assert struct.unpack('<I', task_file.read(4))[0] == 3
    task_file.seek(24)
    task_base, task_directory = struct.unpack('<QQ', task_file.read(16))
    task_file.seek(task_directory)
    task_count = struct.unpack('<I', task_file.read(4))[0]
    task_entries = {}
    for _ in range(task_count):
        task_path_len = struct.unpack('<I', task_file.read(4))[0]
        task_path = task_file.read(task_path_len).rstrip(b'\0').decode('utf-8')
        task_offset, task_size = struct.unpack('<QQ', task_file.read(16))
        task_md5 = task_file.read(16).hex()
        task_flags = struct.unpack('<I', task_file.read(4))[0]
        task_entries[task_path] = (task_base + task_offset, task_size, task_md5, task_flags)

    # この索引検索は読み取りのみ。関係ないアセット本文を展開しない。
    task_pattern = re.compile(r'^(animations/(characters|character_select|rest_site|merchant)/|scenes/(creature_visuals|screens/char_select|rest_site|merchant)/)')
    for task_path, task_info in task_entries.items():
        if task_pattern.search(task_path):
            print(task_path, task_info)

    # 必要な小さい scene / tres / import / JSON を一つ指定して本文を読む。
    task_resource = 'scenes/creature_visuals/ironclad.tscn'
    task_offset, task_size, task_md5, task_flags = task_entries[task_resource]
    assert task_flags == 0, 'encrypted/removal resource: do not use this simple reader'
    task_file.seek(task_offset)
    task_bytes = task_file.read(task_size)
    assert hashlib.md5(task_bytes).hexdigest() == task_md5
    print(task_bytes.decode('utf-8'))
```

最初の追跡候補は `scenes/creature_visuals/{character}.tscn`、`scenes/screens/char_select/char_select_bg_{character}.tscn`、`scenes/rest_site/characters/{character}_rest_site.tscn`、`scenes/merchant/characters/{character}_merchant.tscn`。`ext_resource` の `SpineSkeletonDataResource` が指す `*_skel_data.tres` から `*.atlas.import / *.skel.import / *.png.import` と `.godot/imported/` の実体を辿れる。これらが存在することと、動画差し替えを既存イベントへ接続できることは別問題である。

Ironclad と Regent の大きい選択背景は単独 PNG ではなく Spine を含む scene だった。Silent の選択背景にも Spine と別の背景 Texture2D がある。選択アイコン `images/packed/character_select/char_select_{character}.png` は **132×195 の頭部アイコン**であり、全身の背景画像ではない。

参考の小さい絵のデコード: 今回の二人の選択アイコン ctex は `GST2` から始まり、byte56 に `RIFF` があり、続く uint32 + 8 bytes が埋め込まれた WebP の長さだった。ctex 原本を保存し、その WebP bytes のみを取り出した。すべての ctex に同じ offset が使えるとは一般化しない。
