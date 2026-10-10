# アクセス制御と制度のメタデータ

`RAG_AUTH_MODE=local` は単一ユーザー向け開発モードで認証を明示的に省略し、付属ランチャー / Compose はループバックにバインドします。組織の認証ではありません。`required` はサーバー認証を有効にし、匿名の文書・質問リクエストを拒否します。サーバー設定であり、クライアントから編集できません。

## ローカル設定

アプリと同じ `RAG_DATA_DIR` と `RAG_DATABASE_URL` を使って登録します。

```powershell
python -m scripts.manage_access create-user admin --roles admin --token-file .secrets/admin.token
python -m scripts.manage_access create-role finance
python -m scripts.manage_access create-user alice --roles reader finance --token-file .secrets/alice.token
```

`.env` に `RAG_AUTH_MODE=required` を設定して再起動し、非公開ファイルのトークンをログイン画面に入力します。トークンはランダムな 256-bit bearer 認証情報で、DB は SHA-256 ダイジェストを保存します。UI は HttpOnly、SameSite=Strict（HTTPS では Secure）の cookie のみを保持し、ブラウザーでの有効期間は 8 時間です。API bearer token はローテーション / 無効化まで有効で、cookie 失効は token 失効ではありません。ファイルは非公開にしてください。`.secrets/` は Git とソース出力の対象外です。Windows はディレクトリ ACL を継承し、Unix は mode 0600 で作成します。ポートフォリオ用認証であり、SSO/MFA ではありません。

```powershell
python -m scripts.manage_access list-users
python -m scripts.manage_access grant DOCUMENT_ID finance read
python -m scripts.manage_access grant DOCUMENT_ID finance write
python -m scripts.manage_access grant DOCUMENT_ID finance revoke
python -m scripts.manage_access set-roles USER_ID reader finance
python -m scripts.manage_access disable-user USER_ID
python -m scripts.manage_access rotate-token USER_ID --token-file .secrets/alice-new.token
```

admin は全文書・設定・権限を管理でき、editor はアップロードでき、reader はアップロードできません。ロールの文書 write は read を含み、所有者は read/write を持ちます。新規・移行文書に**共有権限は自動付与されません**。管理者が文書情報パネルで設定します。所有者のない既存文書は required では最初は admin のみが利用できます。各リクエストでロールと権限を読むため、取り消しは後続リクエストに反映します。実行中のリクエストは開始時に解決した権限範囲を使います。

Compose では `docker compose exec app python -m scripts.manage_access ... --token-file /app/data/admin.token` でアプリコンテナーに登録します。`docker compose cp app:/app/data/admin.token .secrets/admin.token` で非公開ファイルをコピーし、`RAG_AUTH_MODE=required` を有効にしてアプリコンテナーを再作成します。DB、ファイル、ユーザー・権限テーブルは既存ボリュームに保持します。本番の外部公開には HTTPS と組織の ID 基盤が必要です。この変更自体は公開ポートを開放しません。

## 検索とファイルの境界

サーバーは認証済みユーザー → ロール / 所有権 → 要求文書 ID → メタデータ条件 → 許可 ID の順に解決します。これは質問の Embedding、Dense 検索、全文検索、再ランキング、生成、検証の**前**です。各 SQL は順位付け・件数制限の前に ID を適用します。`None` は内部の無制限範囲、`[]` は全拒否で無制限にはなりません。UI の空選択は「許可された全文書」で、サーバーが解決します。

文書一覧、PDF 原本、Chunk、再試行、削除、メタデータ変更、再インデックス、モデル設定、費用指標、権限にも認可チェックがあります。クライアント指定のユーザー ID は無視します。権限のない文書 ID へのアクセスは 404。重複アップロードも非公開文書 ID を漏らしません。required の `/api/health` は稼働状態と保存バックエンドのみを返します。クロスオリジン書き込みは拒否します。

HTTP 認可テストは CI で SQLite と実 PostgreSQL を使い、禁止・空範囲が外部モデルに渡らないことを監視して確認します。検索ストレージ契約は両バックエンドで read/write、所有権、トークン更新、無効ユーザー、制度フィルターを検証します。

## メタデータ API

`status` は既にインデックス状態（`queued`、`ready` など）に使うため、制度の状態は別フィールド `policy_status` を使います。

```json
{"policy_status":"current","effective_from":"2026-04-01","effective_to":"2027-03-31","department":"Finance","document_version":"TR-2026.2"}
```

`PUT /api/documents/{id}/metadata` または文書情報フォームで更新します。日付は ISO 形式で検証し、開始・終了日を含みます。`effective_to=null` は終了日なしです。メタデータは運用者が入力し、有効日の推測や PDF の現行制度への自動分類はしません。

```json
{"question":"What is the travel allowance?","document_ids":[],"filters":{"policy_status":["current"],"as_of":"2026-09-15","department":"Finance"}}
```

`POST /api/chat` は検索前にフィルターを適用します。日付指定では開始日不明の文書を除外し、部門は完全一致です。フィルターを空にすると権限内の全状態・全部門を含み、過去や複数バージョンの質問に使えます。current ラベルだけでは有効期間の証明になりません。再インデックス時もメタデータを維持します。
