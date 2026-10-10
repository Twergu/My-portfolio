# SQLite と pgvector のベンチマーク

生成日時：2026-09-16T00:37:47.622214+00:00

乱数 seed：20260914; ベクトル数：1000; 次元：384; クエリ数：20; 繰り返し：3.

| バックエンド | 状態 | 検索 p50 (ms) | 検索 p95 (ms) | Recall@k | 索引作成 (ms) | HNSW 構築 (ms) |
|---|---|---:|---:|---:|---:|---:|
| sqlite_exact | measured | 132.071 | 133.875 | 1.000 | 459.860 | — |
| pgvector_exact | measured | 2.345 | 2.388 | 1.000 | 378.089 | — |
| pgvector_hnsw | measured | 2.756 | 2.807 | 1.000 | 378.089 | 369.719 |

欠測値は推定しません。両データベースの実測がそろうまでは高速化を主張しません。

正解は独立した float64 の総当たり計算です。事前実行は計測に含めません。保存・検索性能の測定であり、文書の関連性や回答品質は評価しません。

実 PostgreSQL + pgvector データベースを用いて実行します。

```sh
export RAG_BENCHMARK_DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DATABASE"
python -m scripts.benchmark_stores --count 1000 --dimensions 384 --queries 20 --repeats 3
```

作成・削除するのはランダム名の `kb_bench_...` schema のみで、アプリのテーブルは変更しません。

規模拡大時は複数の文書数と実 Embedding モデルの次元で再測定してください。Exact は最大 16000 次元に対応し、この実装の HNSW は 2000 次元超を拒否します。
