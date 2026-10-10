# 検索・権限に関する 12 項目の変更と検証

この段階の実装を前回の記録と分け、元の実験レポートを維持しました。この時点の依頼に従い、人手レビュー、Agent、Human-in-the-loop は保留しました。

| 項目 | 方針と効果 | 検証 |
|---|---|---|
| 1 Hybrid Retrieval | Dense + SQLite BM25 / PostgreSQL Full-text、Top 20 を RRF 融合。数値・日付・制度番号と中国語・日本語に共通の解析器 | `tests/test_stores.py`、[実 3 方式比較](../reports/v3/retrieval.json) |
| 2 Reranker | 独立設定可能な LLM で全候補を並べ替え、Top 5 を Generator へ。形式修正は最大 1 回、失敗と全費用を記録 | `tests/test_retrieval.py`。test Recall@5 は 88.1%→100%、検索 P50 は 0.46→6.16 秒 |
| 3 Verifier 校正 | 36 件の中国語・日本語・英語 Claim/Evidence。supported/unsupported/partial、数値、否定、税、版、例外。dev/test は半分ずつ | [データ](../evals/claim_calibration.json)、[dev 比較](../reports/v3/calibration-calibrated-dev.json)、[test](../reports/v3/calibration-calibrated-test.json)。dev は両プロンプトとも Precision=1、Recall=6/7、校正 test は 18/18。普遍的改善とは主張しない |
| 4 Verification 方針 | off/fast/strict を保持し all/selective を追加。省略可能な単純原文引用を厳しく制限し、未検証は unknown | `tests/test_verifier_calibration.py`。生成した 59 主張の再評価で省略可能は 0、節約は未確認。既定 all |
| 5 人手レビューセット | 依頼者の明示的な指示で保留。人手ラベルを捏造しない | 全データの出所を明示し、後続で業務担当者が確認 |
| 6 Metadata / Version | 独立 policy_status、有効開始・終了日、部門、版。SQL で範囲を解決後に検索。中国語・日本語の編集・絞り込み UI | `tests/test_stores.py` で日付境界、草案・旧版・未分類、空範囲を検証。[手順](access-control.md) |
| 7 ACL | User、Role、Document Permission、所有者。required でサーバー認証。両検索、ファイル、一覧、変更、設定を保護。SQLite→PG 移行で ID・権限・版を維持 | SQLite/PG 共通権限テストと HTTP 越権・モデル通信分離。[読み取り専用ブラウザー検収](../reports/v3/browser-access.json)。local は単一ユーザー開発と明示 |
| 8 HNSW | Exact が既定。実索引計画、Recall≥95%、より短い P95 を満たした場合のみ人手評価の候補にし、自動切替しない | `backend/search_policy.py` と scale benchmark の `ann_acceptance`。合成実験は本番 ACL フィルター下の保証ではない |
| 9 Latency / Cost | query embedding/retrieval/reranking/generation/verification を分離。役割別 tokens、既知・未知費用、実 RAG 比較。問題ごとの中間保存と再起動時の索引費用 | [strict / fast 実測](../reports/v3/summary.md)：P50 13.90 / 10.50 秒、平均 USD 0.002028 / 0.001694。失敗を隠さず、Judge 費用を app/query に混ぜない |
| 10 品質・保守性 | Ruff E/F/I/B、format、pytest-cov 分岐カバレッジを CI に追加。Provider/Verifier/Reranker/統制を集約 | [CI](../reports/ci-status.json)、[動的テスト結果](../reports/ci/tests.md)、[PostgreSQL 込みカバレッジ](../reports/ci/coverage.json)。mypy は型インターフェースから段階的に導入予定 |
| 11 Agent | 依存する基盤の順序に従い LangGraph と複数 Agent を保留 | [導入条件](adr/0003-agent-gates.md) |
| 12 Human-in-the-loop | 実操作ツールは公開せず、将来の承認は確認可能な正確な引数と有効な権限に結び付ける | 同上。操作承認とユーザー監査は当時未実装 |

設定と再現：

```bash
python -m scripts.retrieval_experiment
python -m scripts.calibrate_verifier --split dev --prompt baseline --output reports/v3/calibration-baseline-dev-live.json
python -m scripts.calibrate_verifier --split dev --prompt calibrated --output reports/v3/calibration-calibrated-dev.json
python -m scripts.calibrate_verifier --split test --prompt calibrated --output reports/v3/calibration-calibrated-test.json
python -m scripts.evaluate --mode api --split test --overlap 0 --retrieval-mode hybrid --reranker-mode llm --verification-mode strict --judge-model gpt-4.1 --concurrency 2 --output reports/v3/quality-strict-test
python -m scripts.evaluate --mode api --split test --overlap 0 --retrieval-mode hybrid --reranker-mode llm --verification-mode fast --judge-model gpt-4.1 --concurrency 2 --output reports/v3/quality-fast-test
python -m scripts.v3_results
python -m ruff check .
python -m ruff format --check .
python -m scripts.check
```

API コマンドは設定した有料モデルを呼び出します。3 方式は同じ索引を使い、各方式で実 query Embedding を呼び出しました。初回 dev の Reranker schema エラー 1 件を保持し、全件成功と偽っていません。test は 3 方式それぞれ 54 問で失敗なし。既存 test を回帰に使っており、新しい未見セットとは呼べません。

## 実際の効果と制約

Hybrid 単独で Recall@1 は 58.33%→63.10% に改善しましたが、Recall@5 は 88.10% のままです。LLM Reranker を加えると Recall@1 は 73.81%、Recall@3/5 は 100%、MRR は 0.9643、nDCG は 0.9736。このセットの主要な順位改善は再ランキングによるもので、全効果を Hybrid に帰属させません。

RAG の strict / fast は各 54 問を完了し、API/Judge の形式エラーは残りませんでした。Answer Correctness は 90.48% / 92.86%、Refusal Accuracy は 92.59% / 96.30%、回答可能な問題の未回答率は 9.52% / 4.76%。引用支持の自動スコアは両方 100% で、分母は回答済みの 38 / 40 件です。信頼性の保証ではなく、Judge の見逃しと誤判定も判明しました。[事例診断](../reports/v3/grounding-diagnostics.md)を参照してください。

独立した 2 実行で fast は strict より P50 が 24.5%、平均アプリ費用が 16.5% 低下しましたが、実行時の意味的 Verifier はありません。生成と再ランキングの確率的変動があるため、Verifier を外した純粋な因果効果とは断定できません。strict の Reranker P50 は約 6.78 秒、Generator 約 4.14 秒、Verifier 約 2.50 秒、実 DB 検索は約 0.016 秒。段階の分位数は加算できません。次の時間短縮は再ランキングと生成を優先すべきです。

既定は Exact、Dense、有料 Reranker 無効、strict/all、baseline Verifier プロンプトを維持します。高再現率設定は hybrid + llm を選びます。Verifier/Reranker は別モデルを指定できますが、この段階で軽量独立 Verifier の実測や費用削減はしていません。

実 CI 2 回で全 DB テストと 1k/10k/100k 比較を実施。HNSW の Recall は 10k、ef=400 で 95% / 91%、100k、ef=1000 で 57% / 67%。索引構築と共有 runner には変動があります。[初回結果](../reports/v3/ci-first/README.md)と[最終再検証](../reports/vector-scale.md)を保持し、一度の達成を安定性の保証としません。

追跡可能な実験費用小計は USD 0.662463 で、索引、検索、校正、2 回分の追加 Judge を含みます。それ以前の中断実行の使用量は不明で、[中断記録](../reports/v3/interrupted-quality-run.json)に分離しています。ゼロ扱いや品質の推測はせず、事後診断で元スコアを変更しません。
