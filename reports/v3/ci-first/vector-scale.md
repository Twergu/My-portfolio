# pgvector Exact と HNSW：規模別ベンチマーク

状態：**completed**; 実行日時：2026-09-16T00:26:51.735067+00:00

合成した正規化ガウスベクトルを使用。事前実行後、単一クライアントで測定し、独立した float64 NumPy 正解と比較します。HNSW は ef_search=100/400/1000、既定 m=16/ef_construction=64。COPY 取り込みと索引構築は別計測。実アプリの SQL とサーバーカーソルの条件で計画を取得します。HNSW は Exact への代替を防ぐため sequential/bitmap scan と sort を無効にし、Exact は index/bitmap scan を無効にします。

| Chunk 数 | 検索 | p50 ms | p95 ms | Recall@K | 状態 |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 2.366 | 2.401 | 1.000 | measured |
| 1000 | HNSW ef=100 | 2.776 | 3.833 | 1.000 | measured |
| 1000 | HNSW ef=400 | 3.191 | 3.254 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 3.740 | 3.829 | 1.000 | measured |
| 10000 | exact | 8.425 | 9.372 | 1.000 | measured |
| 10000 | HNSW ef=100 | 3.479 | 3.705 | 0.560 | measured |
| 10000 | HNSW ef=400 | 5.117 | 5.459 | 0.950 | measured |
| 10000 | HNSW ef=1000 | 7.134 | 10.760 | 0.990 | measured |
| 100000 | exact | 92.388 | 100.690 | 1.000 | measured |
| 100000 | HNSW ef=100 | 7.218 | 7.759 | 0.170 | measured |
| 100000 | HNSW ef=400 | 18.337 | 19.528 | 0.350 | measured |
| 100000 | HNSW ef=1000 | 39.664 | 41.716 | 0.570 | measured |

Exact の実測 p95 が SLO を満たすなら Exact を選びます。HNSW は再現率も品質目標を満たす場合にのみ選択します。合成データから汎用の切替閾値は決められません。索引サイズ、構築時間、実行計画、マシンとソフトウェアの版は JSON に保存し、サービス未実行の結果は推定しません。
