# pgvector Exact と HNSW：規模別ベンチマーク

状態：**completed**; 実行日時：2026-10-05T01:05:09.552242+00:00

合成した正規化ガウスベクトルを使用。事前実行後、単一クライアントで測定し、独立した float64 NumPy 正解と比較します。HNSW は ef_search=100/400/1000、既定 m=16/ef_construction=64。COPY 取り込みと索引構築は別計測。実アプリの SQL とサーバーカーソルの条件で計画を取得します。HNSW は Exact への代替を防ぐため sequential/bitmap scan と sort を無効にし、Exact は index/bitmap scan を無効にします。

| Chunk 数 | 検索 | p50 ms | p95 ms | Recall@K | 状態 |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 3.257 | 3.365 | 1.000 | measured |
| 1000 | HNSW ef=100 | 3.899 | 3.968 | 1.000 | measured |
| 1000 | HNSW ef=400 | 4.306 | 4.430 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 5.067 | 5.332 | 1.000 | measured |
| 10000 | exact | 10.304 | 10.639 | 1.000 | measured |
| 10000 | HNSW ef=100 | 4.649 | 7.372 | 0.600 | measured |
| 10000 | HNSW ef=400 | 7.038 | 10.672 | 0.960 | measured |
| 10000 | HNSW ef=1000 | 8.688 | 8.880 | 1.000 | measured |
| 100000 | exact | 101.508 | 132.877 | 1.000 | measured |
| 100000 | HNSW ef=100 | 7.534 | 8.198 | 0.130 | measured |
| 100000 | HNSW ef=400 | 17.209 | 24.827 | 0.350 | measured |
| 100000 | HNSW ef=1000 | 34.543 | 37.563 | 0.590 | measured |

Exact の実測 p95 が SLO を満たすなら Exact を選びます。HNSW は再現率も品質目標を満たす場合にのみ選択します。合成データから汎用の切替閾値は決められません。索引サイズ、構築時間、実行計画、マシンとソフトウェアの版は JSON に保存し、サービス未実行の結果は推定しません。
