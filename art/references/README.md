# 参照画像の案内

キャラごとに階層化した参照。公式の設定資料と、ユーザー指定のデザイン参考を区別し、画像・動画の原本、デコードしたフレーム、ゲーム内文章の根拠を管理する。生成物や完成MOD素材とは別の資料。

| 対象 | 画像と読み方 | 出典・版・派生操作・ハッシュ |
| --- | --- | --- |
| アイアンクラッド | [ironclad/README.md](ironclad/README.md) | [sources.json](ironclad/sources.json) |
| サイレント | [silent/README.md](silent/README.md) | [sources.json](silent/sources.json) |
| ユーザー指定の目標MOD | [擬人化・女性化の参照](silent/mod-reference/kaguya-silent-raven/README.md) | ユーザー添付。公式設定資料とは区別 |
| リージェント | [regent/README.md](regent/README.md) | [sources.json](regent/sources.json) |
| ネクロバインダー・オスティ | [necrobinder/README.md](necrobinder/README.md) | [sources.json](necrobinder/sources.json) |
| ディフェクト | [defect/README.md](defect/README.md) | [sources.json](defect/sources.json) |
| 世界観 | [world/README.md](world/README.md) | [sources.json](world/sources.json) |
| 共通の５人原画 | [shared/official/character-lineup.png](shared/official/character-lineup.png) | [Mega Crit公式掲載ページ](https://www.megacrit.com/news/2026-02-19-release-date-trailer/) |

## 管理構造

```text
art/references/
  ironclad/  silent/  regent/  necrobinder/  defect/
    README.md
    sources.json
    official/
      key-art/       # 頭部・公式プロモ原画
      gameplay/      # ゲーム画面・動作・参照フレーム
      development/   # 開発中の資料。現行と区別
      game-assets/   # 版を固定したローカルゲームの抜粋
  necrobinder/osty/   # 相棒の単独参照
  world/             # 塔・背景・公式美術方針
  shared/            # 複数キャラに共通する原本
```

必要な分類だけを作る。共有原本は重複ダウンロードせず、各索引から参照する。GIFの原本・静止フレーム・フレーム一覧は同じ原典の派生として扱う。公式記事のファンアート欄は、公式の現行デザインと混ぜない。

設定の判断は [キャラ・世界観の調査](../../docs/research/characters/README.md)、制作提案は [キャラクター方針](../../docs/design/characters/review-v03.md) を参照。

## 拡張を判断する考え方

このフォルダーは、後から来る制作者が「なぜその資料を使い、どの特徴を引き継ぐのか」を判断するためのもの。現在のキャラ別・用途別の階層は、その判断を助ける配置であり、将来の対象を拘束する分類ではない。

1. **資料で解きたい不明点を定める。** 外形、背景設定、動き、関係性など、何の判断を支える資料かを考える。枚数を増やすことより、既存資料で埋まっていない問いを優先する。
2. **来歴と読み取れる範囲を確かめる。** 誰が、いつ、どの文脈で作った資料かを確認する。描かれていること、文章で述べられること、こちらの解釈を区別し、資料が証明しないことも残す。
3. **どこに属するかを意味から決める。** 特定の対象、複数の対象の関係、世界全体のいずれを説明する資料かを考える。一つに収まらない場合は、原本の所在と利用側の案内を分けるか、分類自体を変えるかを選ぶ。
4. **原本と利用形を区別する。** 切り出し、フレーム抽出、要約などが必要なら、どの原本から何を変えたかを辿れる形にする。派生物の見やすさと、原本へ戻って解釈を確かめられることを両立させる。
5. **既存の判断を再点検する。** 新しい資料が過去の理解と矛盾した場合は、追加するだけで終えず、どの解釈・デザイン・生成指示が変わるかを見る。新旧を無条件に混ぜたり、新しい方を自動的に正しいと扱ったりしない。

### 分類や形式を作り直すとき

キャラ別では関係性が見えなくなる、版違いが埋もれる、出典形式が新しい媒体を表せないなど、現在の構造が誤解を生む場合は再編する。ディレクトリ名、参照単位、索引やメタデータの形式を、互換性を崩して変更することもできる。

再編では、利用者・生成プロンプト・文書がどの識別子やパスに依存しているかを先に確認する。原資料の同一性、出典、派生関係、選定理由のうち何を引き継ぎ、何を訂正・廃止するかを明示する。変更後は、代表的な資料から原本と出典へ戻れるか、以前の判断がどの新しい資料へ対応するかを確かめる。

古い配置の維持だけを目的に複製を増やさない。残す履歴や移行案内は、追跡可能性と利用者への影響から決める。新しい構造でも説明できない例外が続くなら、分類の前提を再び問い直す。
