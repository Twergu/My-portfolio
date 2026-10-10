# pgvector Exact と HNSW：規模別ベンチマーク

状態：**completed**; 実行日時：2026-10-05T12:33:38.664119+00:00

合成した正規化ガウスベクトルを使用。事前実行後、単一クライアントで測定し、独立した float64 NumPy 正解と比較します。HNSW は ef_search=100/400/1000、既定 m=16/ef_construction=64。COPY 取り込みと索引構築は別計測。実アプリの SQL とサーバーカーソルの条件で計画を取得します。HNSW は Exact への代替を防ぐため sequential/bitmap scan と sort を無効にし、Exact は index/bitmap scan を無効にします。

| Chunk 数 | 検索 | p50 ms | p95 ms | Recall@K | 状態 |
|---:|---|---:|---:|---:|---|
| 1000 | exact | 2.781 | 2.887 | 1.000 | measured |
| 1000 | HNSW ef=100 | 3.161 | 3.300 | 1.000 | measured |
| 1000 | HNSW ef=400 | 3.624 | 5.179 | 1.000 | measured |
| 1000 | HNSW ef=1000 | 4.257 | 4.432 | 1.000 | measured |
| 10000 | exact | 13.115 | 13.762 | 1.000 | measured |
| 10000 | HNSW ef=100 | 4.459 | 4.742 | 0.550 | measured |
| 10000 | HNSW ef=400 | 7.400 | 7.737 | 0.910 | measured |
| 10000 | HNSW ef=1000 | 10.834 | 11.297 | 1.000 | measured |
| 100000 | exact | 111.236 | 125.633 | 1.000 | measured |
| 100000 | HNSW ef=100 | 9.081 | 10.133 | 0.130 | measured |
| 100000 | HNSW ef=400 | 24.142 | 30.982 | 0.350 | measured |
| 100000 | HNSW ef=1000 | 52.500 | 53.898 | 0.670 | measured |

Exact の実測 p95 が SLO を満たすなら Exact を選びます。HNSW は再現率も品質目標を満たす場合にのみ選択します。合成データから汎用の切替閾値は決められません。索引サイズ、構築時間、実行計画、マシンとソフトウェアの版は JSON に保存し、サービス未実行の結果は推定しません。
