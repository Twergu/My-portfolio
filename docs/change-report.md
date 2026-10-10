# 初回の 17 項目：変更方針・内容・検証結果

コード、文書、再現可能な実験を統合しました。実 API、実 pgvector 比較、Docker 起動は個別に検証状態を記録し、実行環境がない項目を実測済みとは扱いません。テスト件数は[自動生成レポート](../reports/tests.md)を参照してください。この文書は初回作業時点の記録です。後続の検証結果は README を参照してください。

| # | 要求と方針 | 変更内容 | 効果と当時の検証範囲 |
| --- | --- | --- | --- |
| 1 | README のテスト件数を動的に生成 | [check.py](../scripts/check.py) が pytest の JUnit XML から Markdown/JSON を生成し、時刻、ソース SHA、成功・失敗・スキップを記録 | README に件数を手入力せず、実行ごとに更新。古いスナップショットと未実行を識別可能 |
| 2 | SOURCE_INDEX を相対パス化 | [source_index.py](../scripts/source_index.py) が実ファイルから[一覧](../SOURCE_INDEX.md)を生成 | ルート相対リンクでクローン・展開後も利用可能。検査済みの完全なソース ZIP を生成 |
| 3 | インデックス例外を実際に記録 | [main.py](../backend/main.py) の exception/exc_info に document_id/profile/stage を付与。[parse_pdf.py](../backend/parse_pdf.py) が子プロセスの元 traceback を保持 | 実際の例外と段階を特定。RuntimeError と破損 PDF の解析スタックをテストし、ログをローテーション |
| 4 | 実 Embedding + LLM | [live_smoke.py](../scripts/live_smoke.py) で架空の 2 ページ PDF を作成し、アップロード、解析、実 Embedding、LLM、根拠検証、2 ページ目の引用を確認 | **当時は RAG_API_KEY がなく未実行。** [レポート](../reports/live-api-smoke.md)に blocked と記録し、模擬サービスを実 API 成功と扱わない |
| 5 | RAG Evaluation Dataset | [dataset.json](../evals/dataset.json) に中国語・日本語・英語の架空手引き 3 件、15 ページ、36 問。参照事実・回答、ページ根拠、dev/test を含む | 直接質問、複数ページ、回答なし、攻撃を含む再現可能な入門セット。実資料と人手による拡充が必要 |
| 6 | Retrieval 指標 | [metrics.py](../evals/metrics.py) にページ単位 Recall@K、Precision@K、MRR@K、nDCG@K、回答なしでの誤検索率 | 重複ページを除き、空き枠も precision の分母に含める。回答なしを別集計し、再現率を水増ししない |
| 7 | 回答品質指標 | 参照事実の語彙カバレッジ、token F1、exact match、正しい拒否、回答失敗・誤拒否、候補 claim groundedness | ローカル原文モードは N/A。語彙一致やモデル検証は人手の意味的正確性と区別。実モデルのスコアは API 設定待ち |
| 8 | Latency と Cost | [telemetry.py](../backend/telemetry.py) と /api/metrics に段階別時間、実 token usage、再試行、推定費用。UI で詳細を展開 | p50/p95 と件数を確認可能。失敗・検証呼び出しも含め、単価・使用量不明は不明、API を呼ばない場合は 0 |
| 9 | Chunk Size / Overlap 実験 | [chunk_experiment.py](../scripts/chunk_experiment.py) で 6 設定を実行し、dev のみで選択後、凍結設定を test で評価 | [実測](../reports/chunks/chunk-experiment-local.md)：dev Recall は同じ。事前ルールで 1200/120 を選択。test Recall=1.000、nDCG≈0.855。小規模なローカルハッシュ検索のため本番既定値は変更せず |
| 10 | 物理ページをまたがない設計を ADR 化 | [ADR 0001](adr/0001-physical-page-chunks.md) に物理ページ位置、確認可能性、評価ラベルの安定性、ページをまたぐ意味の損失を記載 | Chunk はページ内に限定。複数ページ質問は複数出典・引用で扱い、回帰テストで維持 |
| 11 | HTTP Client の接続再利用 | アプリのライフサイクルで単一 Provider/Client を保持。インデックス、質問、検証、接続テストで共有し、終了時に解放 | 接続・再試行の契約を MockTransport で検証。再利用可能だが、**実 indexing latency の改善幅は未測定** |
| 12 | Provider API の分離 | [providers.py](../backend/providers.py) に transport、認証、再試行、Embedding 応答検証、chat/JSON 解析を集約。Client や互換オブジェクトを注入可能 | RAG から HTTP 実装を分離し、サービス交換、失敗経路のテスト、接続再利用を容易に |
| 13 | NO_EVIDENCE 文字列への依存を除去 | 厳密な JSON status/claims とサーバー状態フィールドで判定 | 文書に旧マーカーがあっても拒否しない。不足、形式不正、根拠不足を区別し、UI 互換の refused は保持 |
| 14 | Citation を主張の根拠まで検証 | 厳密 schema → 原文 quote 一致 → claim ごとの指定出典に基づく独立 LLM 検証。通過した claims のみ表示 | 偽引用、矛盾、欠落・重複・型不正の verdict を遮断するテスト。モデル検証は数学的証明ではなく、人手の検収が必要 |
| 15 | SQLite → PostgreSQL + pgvector | [postgres_store.py](../backend/postgres_store.py) に native vector、接続プール、トランザクション、profile/次元分離、exact/HNSW。[移行スクリプト](../scripts/migrate_sqlite.py)は空の移行先へ明示的に移行 | Store 経由で全経路に PostgreSQL を選択可能。SQLite は比較用に維持。**当時はローカル PostgreSQL がなく PG テストはスキップ。利用者データは自動移行しない** |
| 16 | SQLite vs pgvector Benchmark | [benchmark_stores.py](../scripts/benchmark_stores.py) に同一 seed/ベクトル/query、独立 exact 正解、事前実行、p50/p95、HNSW 構築時間・再現率 | SQLite は実測。[レポート](../reports/store-benchmark.md)の PG 2 項目は当時 blocked。**両 DB 比較は未完了で、高速化は主張しない**。DB 設定後に追加実行可能 |
| 17 | Dockerize | [Dockerfile](../Dockerfile)、[compose.yaml](../compose.yaml)、[.dockerignore](../.dockerignore)、[CI](../.github/workflows/ci.yml) | app+pgvector、非 root、ヘルスチェック、永続ボリューム、ループバック、単一プロセス。YAML は解析済み。**当時は Docker Engine がなくビルド・起動は未実測** |

## 実測結果の解釈

6 設定は同じ架空データ、K=5 を使い、候補数は 17～32 です。ページ Recall が 1 でも各事実の検索・生成が正しいとは限りません。local は原文のみで回答品質は N/A。選択値はこの種データ上のルールの出力で、本番最適値ではありません。

SQLite 比較は 1,000 件の 384 次元合成正規化ベクトル、20 クエリ、各 3 回と追加の事前実行を使います。p50/p95、索引時間はレポートを参照してください。保存・検索を測り、モデル時間や実企業文書の関連性は測りません。

ブラウザーで中国語・日本語の size、overlap、検索方式、ローカル回答の引用ページ、段階時間、API 使用量ゼロを確認しました。言語変更後にサイドバーへ旧言語が残る不具合も修正。既存デモ PDF は新分割方式で再構築し、引き続き利用できます。

## 当時、残りの実測に必要だった条件

1. ローカル .env に API URL、2 モデル名、RAG_API_KEY を設定し、実 smoke を実行。費用を表示する場合は token 単価も設定。キーはチャットに貼らないでください。
2. PostgreSQL + pgvector を用意し、RAG_TEST_DATABASE_URL と RAG_BENCHMARK_DATABASE_URL を設定。テストと --require-postgres 付き比較を実行。
3. Docker Engine/Compose と環境変数を用意し、docker compose up --build -d --wait を実行。CI にも同等の手順があります。

不足していてもソースとローカル評価は納品可能ですが、当時は項目 4、項目 16 の全体、項目 15/17 の実行検収が残っていました。コマンド・設定は [README](../README.md)を参照してください。
