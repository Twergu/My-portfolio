# pgvector Exact と HNSW：規模別ベンチマーク

状態：**completed**; 実行日時：2026-09-16T00:38:40.289783+00:00

合成した正規化ガウスベクトルを使用。事前実行後、単一クライアントで測定し、独立した float64 NumPy 正解と比較します。HNSW は ef_search=100/400/1000、既定 m=16/ef_construction=64。COPY 取り込みと索引構築は別計測。実アプリの SQL とサーバーカーソルの条件で計画を取得します。HNSW は Exact への代替を防ぐため sequential/bitmap scan と sort を無効にし、Exact は index/bitmap scan を無効にします。

| Chunk 数 | 検索 | p50 ms | p95 ms | Recall@K | 状態 |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 2.331 | 2.380 | 1.000 | measured |
| 1000 | HNSW ef=100 | 2.718 | 3.389 | 1.000 | measured |
| 1000 | HNSW ef=400 | 3.121 | 3.257 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 3.737 | 5.257 | 1.000 | measured |
| 10000 | exact | 8.328 | 9.768 | 1.000 | measured |
| 10000 | HNSW ef=100 | 3.408 | 3.568 | 0.600 | measured |
| 10000 | HNSW ef=400 | 5.116 | 5.268 | 0.910 | measured |
| 10000 | HNSW ef=1000 | 7.001 | 7.216 | 1.000 | measured |
| 100000 | exact | 91.499 | 105.971 | 1.000 | measured |
| 100000 | HNSW ef=100 | 7.254 | 8.119 | 0.150 | measured |
| 100000 | HNSW ef=400 | 17.810 | 18.870 | 0.400 | measured |
| 100000 | HNSW ef=1000 | 37.490 | 38.937 | 0.670 | measured |

Exact の実測 p95 が SLO を満たすなら Exact を選びます。HNSW は再現率も品質目標を満たす場合にのみ選択します。合成データから汎用の切替閾値は決められません。索引サイズ、構築時間、実行計画、マシンとソフトウェアの版は JSON に保存し、サービス未実行の結果は推定しません。
