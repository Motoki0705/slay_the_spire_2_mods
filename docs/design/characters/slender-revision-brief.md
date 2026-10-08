# 華奢さとキャラらしさを両立する４人の改訂案

状態: **生成前の設計案。新しい画像は未生成・未評価**。[Issue #24](https://github.com/Motoki0705/slay_the_spire_2_mods/issues/24) / [ウェブ調査と根拠](../../research/art-direction/non-generic-characters.md) / [現行画像と承認状態](review-gallery.md)。確認日: 2026-10-09（JST）。

## 今回のレビュー

ユーザーの指示は「サイレントはOKです」「その他のキャラはスタイルが良すぎます」「まずは、ウェブ調査で画像生成AIへのプロンプトでキャラがAIっぽくならない方法を探しましょう」「華奢な感じが魅力的」。

Silent v0.5最終版は[承認対象の画像とhash](silent/review-v05.md#ユーザー承認2026-10-09)を固定する。他４人の個別v0.1/v01は要修正。今回は調査と次案の設計までを扱う。

「華奢」は、まず肩・胴・手足の線が繊細で、胸腰や脚の長さを誇張しない成人の体つきとして具体化する。身長・胸囲・頭身を全員同じ数値で固定する指示はない。小さな骨格を保ちつつ、衣服の量感、重心、視線、手の使い方を各人の行動から決める。

細くするだけで、同じ顔・同じ立ち方・同じ光沢へ揃う問題は解消しない。ユーザーが求めてきた明確な擬人化・女性化と、本人の意志が見える表情・仕草を引き続き優先する。

## 保持するものと変更するもの

| 対象 | 保持する核 | 今回の変更対象 |
| --- | --- | --- |
| Silent | 承認済みv0.5の本人、可愛さ、露出、澄んだ光と質感 | 今回の再生成対象にしない。将来の部位・動画・rig制作は別工程 |
| Ironclad | 人の顔、赤と金銅の装備、剣、携行する仮面、手の炎を制御する意志 | 身体と鎧の量感を分け、華奢な身体でも力と緊張が読める構成へ |
| Regent | 女性の星の継承者、青い王衣、橙の意匠、玉座・従者・独立した剣 | 堂々とした体型による威厳を弱め、身振りと大きな王衣との対比から自負を表す |
| Necrobinder | 人の顔、赤紫の長衣、大きな襟、鎌、独立した左の骨の手Ostyとの信頼 | 細い肩・胴と衣服の落ち方を整理し、くびれや脚線に頼らず合図と表情を主役にする |
| Defect | 人の顔・髪・表情、青と金の機械身体、自己修繕、独立オーブへの好奇心 | 大きい前腕・すね・足の量感を配分し、細い機構と局所的な補修部品の差を見せる |

これはMODの制作提案であり、公式設定の身体や性別についての追加事実ではない。Osty・剣・オーブを本人の身体へ統合せず、ゲームでは独立制御するという実装方針も維持する。

## プロンプトの差し替え候補

以下は英語の**未実行の部品**。現行プロンプトへ全部を追記するのではなく、競合する体格・装備の記述を置き換える。参照画像の役割や、そのキャラの保持条件を添えて使う。英語であれば改善するという比較結果はなく、既存運用との統一のため英語にしている。

共通の意図は、成人としての読みやすさと、人の顔・髪・表情を持つ女性への翻案。体型の差し替え時には、身長、顔、姿勢、光などを同時に無制限に変えない。

**Ironclad — 細い身体で装備と力を支える落ち着き。** `athletic`と幅広い肩当ての組合せを見直す。強さは剣へ伝わる荷重と手の緊張で示す。

```text
A lightly built adult female soldier, with narrow shoulders, fine wrists,
a gently defined waist, and ordinary adult limb proportions.
Keep her facial identity, bronze armor, sword, carried mask, and restrained flame.
Use short, thin shoulder plates close to the upper arms; let the armor reveal
the slight frame beneath it. Her weight settles through one heel and the planted
sword, while her free hand draws inward to control the flame.
```

**Regent — 大きな権威を演じる小柄な成人の可笑しさ。** `compact, sturdy build`を、小さな身体と大きな王衣の関係へ置き換える。王衣を細くするだけでは本人の特徴が失われる。

```text
A small-framed adult woman inside an oversized cobalt royal mantle.
Fine wrists show at the cuffs; broad folds and gaps at the elbows reveal
how much larger the robe is than her body. Keep her adult facial proportions.
Her chin stays proudly raised while her eyes drop toward the struggling bearer.
One hand points; the other grips the armrest as her composure briefly falters.
Keep the throne, orange star motifs, bearers, and separate celestial sword.
```

**Necrobinder — 鋭さの中に見えるOstyへの信頼。** 現行案は既に細いので、さらに細くする指示を重ねず、腰の絞りと縦長の見え方を調整する。

```text
A slender adult woman with ordinary limb lengths, fine wrists,
and a gently defined, uncinched waist. Her magenta traveling robe falls
in broad planes beneath its distinctive pointed collar.
Keep her human face, hair, bone motifs, and scythe. Her gaze follows Osty's
answering finger; one eyebrow lifts and her mouth briefly softens.
Keep Osty an independent giant skeletal left hand, clearly separated from her.
```

**Defect — 自己修繕の手が好奇心で止まる瞬間。** 厚い前腕・すね・重い足を全身に並べる指定を変える。交換部品の一箇所に量感を残し、用途のある不揃いを作る。

```text
An adult female automaton with a human face, visible hair, and a lightly built
articulated chassis. Slim upper arms, tapered shins, and compact functional feet
contrast with one larger salvaged forearm plate.
Her tool pauses at the adjustment screw as her eyes track the Lightning orb.
Keep the blue and gold identity and independently floating orbs.
Concentrate mechanical detail at the open repair and simplify the other shell planes.
```

塗りを検討する別の回では、例えば次のように焦点と静かな面を指定する。Silentの外套の量や細部は承認されているため、全キャラ一律の描き込み削減にはしない。

```text
Use clear, luminous illustrated color with readable shadow groups.
Place the crispest accents around the eyes, hands, and the action's focal object.
Let broad cloth planes remain quieter; distinguish skin, cloth, and metal
through their edges and reflections. Keep each character's own facial structure.
```

必要な除外は短い自然言語の補助条件にする。`Avoid exaggerated hourglass shaping, elongated fashion-figure proportions, and uniform gloss across every material.` は候補であり、専用negative promptパラメータや効果保証ではない。禁止文だけで目的の姿を定義しない。

## 参照を渡すときの考え方

入力画像には、役割と引き継がない要素を対応させる。原作画像は色・装備・能力の根拠、当該キャラの旧案は既に翻案した装備や場面の参考、Silentは承認された光・線・色面の扱いの参考とする。全部を同じ強さの見本として扱わない。

体型を直す回で「本人の身体・比率・輪郭を完全に保持」「他は一切変更しない」と指示すると、直したい特徴まで保持対象になる。保持する顔・色・装備と、再設計する肩・胴・四肢・服の輪郭を分けて書く。強く固定された旧案の編集で変化が足りない場合は、装備の参照を残して人物全体を再構成する方法を検討する。

Silentの顔・白髪・緑の衣装・狩人の姿勢を４人へ転写しない。画風のみという指示が十分効くかは未検証なので、結果で確かめる。複製傾向が強ければ、Silent画像の使用範囲や入力そのものを見直す。

## 次に比較するとき

1. **旧案と対象を固定する。** ギャラリーのcommit・PNG・プロンプトを基準にする。体型、装備の厚み、表情、塗りのうち、最初に変更する観点を一つ選ぶ。
2. **モデル条件を固定する。** 既存の `gpt-image-2 / high / 1024×1536` とAPI運用を保ち、入力画像・役割・プロンプト・出力hashを記録する。調査した別モデルの構文を混ぜない。
3. **最初は身体と衣服の量感を比較する。** 顔、場面、色、光を可能な範囲で保ち、華奢さが読めるかを見る。人体を細くしたのに厚い鎧で同じ外形になる場合は、身体と装備を別々に再検討する。
4. **次に所作と絵の密度を調整する。** その人物が何をしているかが、目線・手・重心で伝わるかを見る。顔や手に視線が集まり、広い布や背景には静かな面が残るかを確かめる。
5. **採否は画像で判断する。** 改善した箇所と失った箇所を並べ、ユーザーにキャラ別でレビューしてもらう。１枚の成功をプロンプトの普遍的な効果とせず、失敗を無制限の再生成で埋めない。

比較時は、華奢さ、脚や胸腰の誇張、姿勢と行動の一致、キャラの識別性、肌・髪・布の透明感、装備の意味、手と相棒の構造を確認する。全員の体型が同じになった場合や、女性化・擬人化が弱まった場合も改訂対象にする。

この比較計画はまだ実行していない。新しい画像、料金、成功率、ユーザー承認を今回の成果に数えない。

公開Images APIスキーマではseed指定を確認できていない。同じ入力と設定でも出力の変動を含むため、単発の比較は制作上の採否に使い、特定の単語の因果を証明した実験とは呼ばない。判断が揺れる場合だけ、条件を揃えた追加比較を検討する。
