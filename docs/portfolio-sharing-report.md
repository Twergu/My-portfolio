# 求職用の共有・デプロイ版：変更報告

実装：2026-10-07、検収結果の保存：2026-10-08。再現可能でアクセスを制限した共有版を準備しました。依頼者はサーバー・ドメイン未取得です。この作業では一般公開、有料の 24 問評価の再実行、Agent/RAG プロンプトや元の失敗記録の変更は行っていません。

## 変更内容

| ファイル | 変更と効果 |
|---|---|
| `backend/demo_security.py` | 独立 DemoGuard / DemoProvider。日次配額、ログイン制限、同時実行枠、原子的かつ永続的な費用予約。使用量不明時は返還せず、超過時に遮断し、暗黙の再試行を無効化 |
| `backend/main.py` | Demo で required 認証と Strict/all を強制。HTTP を読み取り専用化。許可ドメイン、HTTPS、リクエストサイズ制限。追加確認返信も含む全推論入口に配額を適用し、ACL と同一オリジン PDF 引用を維持 |
| `dist/governance.js`, `dist/styles.css` | 中国語・日本語で読み取り専用、架空資料、プライバシーを表示。アップロード・再構築を非表示にし、保存先がデモサーバーであることを明示 |
| `compose.demo.yaml`, `deploy/Caddyfile`, `.env.demo.example` | 独立 Compose、Caddy HTTPS、固定の信頼済みプロキシ IP、非公開 DB、ループバックのアプリポート、リソース・ログ制限。実キーなし |
| `scripts/prepare_demo.py` | 8 ページの架空文書を冪等に取り込み、`demo-reviewer` のみに権限付与。API 索引には明示的な `--live` が必要で、同じ予算 Provider を通す |
| `scripts/demo_smoke.py`, `.github/workflows/ci.yml` | 実 Docker / HTTPS / pgvector、ログイン cookie、読み取り専用、ACL、配額、偽造 XFF、再起動時の永続性を検証。有料モデルは呼び出さない |
| `tests/test_demo_security.py`, `tests/test_release_check.py`, `tests/frontend/demo.test.cjs` | ガード、費用推定、異常、日付変更・再起動、権限、中国語・日本語 UI の回帰テスト。モデル通信は明示的な MockTransport で実 API と区別 |
| `tests/conftest.py` | 単体テストが操作者の Demo・ドメイン設定や API key を引き継がないよう変更 |
| `scripts/release_check.py`, `scripts/source_index.py`, `.gitignore` | ZIP、到達可能な Git 履歴、非公開パス、既知・一般形式のキーを検査。デプロイファイルを梱包。`.env.*` は example のみ含める |
| `README.md`, `SECURITY.md`, `docs/portfolio-sharing.md`, `docs/demo-walkthrough.md` | トップに構成、実画面、凍結指標。デプロイ、アカウント発行・無効化、予算の制約、パッケージ検査、2 分のデモ手順 |

## 検証記録

デプロイコード `e603ef2cb38a8a8d74695a2f28d6d3cebd56aff0` の [CI 37615440769](https://github.com/Twergu/My-portfolio/actions/runs/37615440769) は全チェックを通過しました。以下の件数はダウンロードした JUnit / JSON で照合しています。その後のコミットは文書・レポートの保存のみで、実行コードは変更していません。

| 検証 | 実際の結果 / 根拠 |
|---|---|
| Python 全回帰 | **371 passed、0 failed、0 errors、0 skipped**。[生成レポート](../reports/portfolio-sharing/ci-final/tests.md) |
| 実 PostgreSQL + pgvector | **39 ケースを実行して通過**。[ケース一覧と JUnit ハッシュ](../reports/portfolio-sharing/ci-final/postgres-tests.json) |
| フロントエンド / Ruff | **17/17 通過**。lint / format も通過。[フロントエンド結果](../reports/portfolio-sharing/ci-final/frontend-tests.json)、[CI メタデータ](../reports/portfolio-sharing/ci-final/provenance.json) |
| 既存 Docker 回帰 | ビルド、ヘルスチェック、PDF 引用、再起動後の保持を通過。[記録](../reports/portfolio-sharing/ci-final/container-persistence.json) |
| 新 HTTPS Demo | Caddy TLS 証明書検証、pgvector、ログイン、Secure/HttpOnly/SameSite cookie、読み取り専用、クロスオリジン拒否、検索前 ACL、配額を通過。[初回実行](../reports/portfolio-sharing/ci-final/demo-initial.json) |
| 再起動 / IP 偽造 | 文書と配額を保持。X-Forwarded-For の偽造でログイン IP 制限を回避できないことを確認。[再起動記録](../reports/portfolio-sharing/ci-final/demo-restart.json) |
| Exact / HNSW 規模比較 | 1k / 10k / 100k を完了。[元の結果](../reports/portfolio-sharing/ci-final/vector-scale.md) |
| 凍結内容 | 24 問の元 JSON の SHA-256 は不変。Agent、RAG、Provider、Grounding、データセットは変更なし。[照合記録](../reports/portfolio-sharing/frozen-integrity.json) |

HTTPS は localhost の内部 CA で実 TLS と証明書の信頼を検証しており、公開ドメイン証明書の検収ではありません。Docker は実 PostgreSQL とローカル検索を使い、有料モデルは呼び出しません。Provider 配額テストは MockTransport を使います。新 Demo 制限下の実モデル品質実験ではありません。ローカルで PostgreSQL 不在により skipped となった 39 件は、上記 CI ですべて実行しました。

最初の [CI 37614252600](https://github.com/Twergu/My-portfolio/actions/runs/37614252600) は全テスト、既存 Docker、規模比較を通過しましたが、新 HTTPS Demo が失敗しました。アプリがプロキシ起動前に動的に `172.30.48.2` を取得し、プロキシの固定 IP と衝突したためです。アプリに別の固定 IP を指定し、Demo 検収を時間のかかる 100k 比較より前に移しました。失敗実行やテストは削除していません。

パッケージ作成前に `python -m scripts.source_index --archive` と `python -m scripts.release_check --git .delivery/My-portfolio` を実行しました。独立した `exports/knowbase-release-check.json` は最終 ZIP の SHA-256 と範囲を記録し、ZIP 自体には含めません。

ソース ZIP と到達可能な Git 履歴を検査し、既知のローカルキー、対象の一般形式、禁止した非公開パスは検出されませんでした。正確なファイル数、履歴オブジェクト数、範囲、SHA-256 は最終検査 JSON を参照してください。ZIP にはソース、デプロイ設定、テスト、評価データ、過去のレポートを含め、`.env`、実アカウント DB、アップロード資料、ログ、仮想環境は除外します。

## モデル品質・性能・費用

`reports/agent-freeze-20261005/` の凍結結果を維持しています。バージョン `9af3637`、Task Success 18/24、Correctness/Grounded 13/18、P50/P95 12.189/24.922 秒、設定単価による推定 USD 0.002579/task。6 件の失敗をすべて保存しています。デプロイ層はその後の変更であり、新しい制限設定での再測定ではありません。

実モデルの新たなレイテンシ・品質は測定しておらず、高速化は主張できません。Demo はコンテキストと出力を制限するため、拒否や切り詰めが増える可能性があります。厳密な根拠検証は維持します。費用ガードは設定単価による保守的な推定と異常検出後の遮断で、サービス側の強制上限を代替しません。

## 残る制約

- サーバー、ドメイン、公開証明書は未取得。デプロイ設定と検証結果を納品し、架空のオンライン URL は提示しません。
- 単一プロセス / worker 1 個。Agent の追加確認セッションは永続化せず、再起動後はやり直します。配額と予算は永続化します。送信済みモデル HTTP は強制撤回できません。
- 訪問者トークンは非公開で受け渡し、手動で無効化します。セルフ登録、SSO、自動失効は未実装です。
- 公開可能な架空資料のみを登録。権限のある利用者は原文を閲覧・ダウンロードできます。カレンダーは Mock で、承認を意味しません。
- 検査対象は既知の値と特定形式であり、すべての漏えい検出を保証せず、第三者監査でもありません。
- デモ手順は提供済みですが、新しい録画はありません。GitHub Release、tag、PR マージ、ライセンスは公開時に別途決定します。
