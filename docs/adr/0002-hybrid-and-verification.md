# ADR 0002：Hybrid Retrieval、任意の再ランキング、検証範囲の明示

接続プールと物理ページ内 Chunk を維持し、共通の多言語語彙解析器、SQLite FTS5 BM25、PostgreSQL `tsvector`/GIN を追加します。ASCII ハッシュ語彙で、両 DB に同じ NFKC 正規化の数値・識別子・中国語/日本語 bigram を適用します。PostgreSQL `ts_rank_cd` は BM25 ではありません。語彙索引は Chunk と同じトランザクションで交換・削除し、既存データは初期化時に補います。

Dense と語彙検索の Top 20 を RRF `sum(1/(60+rank))` で統合し、Chunk ID を重複除去します。cosine、BM25、全文スコアは直接比較できません。Hybrid スコアは融合順位であり確信確率ではありません。Dense の類似度閾値は Dense 経路のみに作用します。

任意の listwise LLM Reranker は同じ長寿命 Provider と独立モデル・役割・単価を使用します。許可候補だけを見て全 ID の順列を返し、新しい根拠は作りません。形式のみの修正は最大 1 回、全試行・費用を保持し、2 回目も不正なら遮断します。Top 5 を Generator へ渡します。時間・費用が大きく増え得るため、全環境で黙って有効にはしません。

off は構造/ID、fast は逐語引用も確認し、strict は意味検証を追加。`verification_strategy=all` が既定です。実験的 selective は質問・主張に高リスク語がなく、単純な抜粋全体の完全引用だけを省略します。数値、否定、版/日付、範囲、言い換えは意味検証を実行。省略は `supported=null`、対象数、`all_supported=null` で示し、検証済みと偽りません。品質・時間の明示的な選択で、安全保証ではありません。

Verifier プロンプトは baseline/calibrated で版管理し、実行時と正解ラベルを入力しない Claim/Evidence 校正器で共有します。dev ラベルはリクエストに入りません。新プロンプトは確立済みの文脈・日付の逐語再掲を要求せず、架空の税条件や根拠のない例外継承は拒否します。dev で同じ結果なら誤拒否改善を主張できず、baseline を既定に維持。自動テストと合成ラベルは業務の人手検収を代替しません。

参考：[SQLite FTS5](https://sqlite.org/fts5.html)、[PostgreSQL 全文検索](https://www.postgresql.org/docs/current/textsearch-controls.html)、[OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)。JSON mode は独自 schema を保証せず、常に厳密検証を適用します。
