# pgvector Exact と HNSW：規模別ベンチマーク

状態：**completed**; 実行日時：2026-10-07T11:42:31.468673+00:00

合成した正規化ガウスベクトルを使用。事前実行後、単一クライアントで測定し、独立した float64 NumPy 正解と比較します。HNSW は ef_search=100/400/1000、既定 m=16/ef_construction=64。COPY 取り込みと索引構築は別計測。実アプリの SQL とサーバーカーソルの条件で計画を取得します。HNSW は Exact への代替を防ぐため sequential/bitmap scan と sort を無効にし、Exact は index/bitmap scan を無効にします。

| Chunk 数 | 検索 | p50 ms | p95 ms | Recall@K | 状態 |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 1.744 | 1.800 | 1.000 | measured |
| 1000 | HNSW ef=100 | 2.067 | 2.222 | 1.000 | measured |
| 1000 | HNSW ef=400 | 2.350 | 2.443 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 2.756 | 2.918 | 1.000 | measured |
| 10000 | exact | 8.327 | 9.048 | 1.000 | measured |
| 10000 | HNSW ef=100 | 2.954 | 3.165 | 0.600 | measured |
| 10000 | HNSW ef=400 | 4.893 | 5.294 | 0.920 | measured |
| 10000 | HNSW ef=1000 | 7.264 | 10.724 | 1.000 | measured |
| 100000 | exact | 79.571 | 103.004 | 1.000 | measured |
| 100000 | HNSW ef=100 | 6.764 | 7.796 | 0.160 | measured |
| 100000 | HNSW ef=400 | 18.882 | 25.253 | 0.360 | measured |
| 100000 | HNSW ef=1000 | 40.557 | 43.098 | 0.600 | measured |

Exact の実測 p95 が SLO を満たすなら Exact を選びます。HNSW は再現率も品質目標を満たす場合にのみ選択します。合成データから汎用の切替閾値は決められません。索引サイズ、構築時間、実行計画、マシンとソフトウェアの版は JSON に保存し、サービス未実行の結果は推定しません。
