# H3選択動画 v0.2

2026-10-09。**MiniMax-H3 / 768P**で５人分を実生成した。各８秒・24fps・192frame、同じ16:9画像をfirst/lastへ指定。Subscription Keyでcreditsを使用し、５件のAPI応答でモデル・解像度・尺・`succeeded`を確認した。生成や取得のために別モデルへ変更していない。

| キャラ | 無音のループ版 | 主な演技 |
| --- | --- | --- |
| Ironclad | [MP4](ironclad/selection-h3-v02-loop.mp4) | 掌の炎を抑え、視線を上げて戻す |
| Silent | [MP4](silent/selection-h3-v02-loop.mp4) | 気配に反応し、短剣を右へ構え直す |
| Regent | [MP4](regent/selection-h3-v02-loop.mp4) | 指図する手と顔、玉座・運び手の重心 |
| Necrobinder | [MP4](necrobinder/selection-h3-v02-loop.mp4) | 自由な掌に小さい魔力を集め、収める |
| Defect | [MP4](defect/selection-h3-v02-loop.mp4) | 補修中の腕と工具へ視線を下げ、手元を確かめる |

ここにある映像は**生成素材**で、ゲーム実録ではない。選択UIとRegentの７星座操作は含めず、ゲーム側で独立して重ねる。戦闘・商人・休憩の本人をこの動画で置き換えず、場面別の姿勢とrigを使う。

APIの実出力は1344×768（7:4）。入力の16:9と厳密には一致しないため、元の空間解像度を保ち、ゲームのaspect-coverで上下を約0.8%ずつcropする。横方向へ引き伸ばしていない。最終のUI・頭・足・武器の見切れは実機で確認する。

原MP4にはAAC音声が含まれたので、納品TheoraとプレビューMP4では取り除いた。終端８frameと始端８frameを重ね、その後に元のframe 8〜183を接続。生成尺は８秒、納品loopは**184frame / 24fps ≒ 7.67秒**。最終frameと先頭frameが元動画の連続したframe183/184に対応する。原MP4は各ディレクトリの `selection-h3-v02-take01.mp4` に保持し、上書きしない。

入力・jobの要求/観測/usage・出力hashは各キャラの `selection-h3-v02-take01.job.json`。処理と出力hashは `selection-h3-v02-production.json` および [production-v02.json](production-v02.json)。キーや署名付きURLは記録しない。[loop境界の数値](loop-checks-v02.json) は補助指標で、知覚品質やゲーム実装の合格を代替しない。親は３fpsの24場面サンプルと0/2/4/6秒の画像で、本人・主要装備・動きの展開・戻りを目視した。全192frameを個別精査したという意味ではない。

入力５枚は既存の自作選択素材をUIなしで描いた `selection-v02-input.png`。生成promptは `art/prompts/<character>/selection-h3-v02.txt`。入力renderの元scene/rig hashは [selection-inputs-v02.json](selection-inputs-v02.json) に当時の版として残す。

５件のusageは各output_seconds=8・input_seconds=0・input_image_count=2。公開料金80 credits/秒から **合計3,200 creditsの見積り**となる。これはアカウント残高や請求を直接測定した値ではない。再生成は行っていない。費用とキーの区分は [H3制作契約](../../docs/research/costs/minimax-h3-production-v02.md)。

再加工は [prepare_selection_video.py](../../tools/assets/prepare_selection_video.py)。生成済みの出力を上書きせず、別の版を用意して品質・接続・実機を確認する。現行のゲーム再生用は `mod/assets/PopSpireWomen/art/<character>/select_loop.ogv` と対応poster。
