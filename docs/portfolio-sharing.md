# 求職用ポートフォリオの共有とデプロイ

リポジトリの閲覧、ダウンロードによる再現、アクセスを制限したオンライン Demo は、それぞれ独立した利用方法です。現在はソースコードとデプロイ設定を提供しています。サーバーやドメインは未取得で、公開オンライン URL はありません。`127.0.0.1` はブラウザーを実行している端末自身を指します。

## 採用担当者向けの入口

最新資料を含む[プロジェクトブランチ](https://github.com/Twergu/My-portfolio/tree/codex/rag-quality-v2)を共有してください。README から実際の画面、構成、最終 24 問の結果を確認できます。デフォルトブランチに未マージの場合、リポジトリのトップには旧版が表示されることがあります。

- **30 秒**：README 冒頭の機能、画面、18/24 の凍結結果と 6 件の失敗。
- **2 分**：[デモ手順](demo-walkthrough.md)で検索、物理ページへの引用、ツールの根拠、保守的な回答拒否を確認。
- **詳細確認**：[全ソース一覧](../SOURCE_INDEX.md)、[設計判断](architecture.md)、[凍結評価](../reports/agent-freeze-20261005/acceptance.md)、[CI](https://github.com/Twergu/My-portfolio/actions/workflows/ci.yml)。

画像は過去の実画面の記録で、対象バージョンと制約を明記しています。静止画、Mock カレンダー、ローカル検索を、実モデルによるオンラインデモとして扱いません。API key、訪問者の token、非公開文書、ローカル DB は公開しません。新しいデモ動画は未収録です。デモ手順に沿って録画できます。

## API 利用料が不要なローカル再現

Git と Docker Compose をインストールし、空のディレクトリで実行します。

```sh
git clone --branch codex/rag-quality-v2 https://github.com/Twergu/My-portfolio.git
cd My-portfolio
docker compose up --build -d --wait
```

ブラウザーで `http://127.0.0.1:8000` を開き、内蔵サンプル PDF を取り込むと、原文検索と引用を試せます。既定は local 開発モードで、ループバックにのみバインドします。公開 Demo ではありません。業務 Agent には実モデル API の設定が必要で、API を使わないモードでは Agent 出力を捏造しません。

## サーバー取得後のデプロイ手順

単一 Linux ホスト、Uvicorn worker 1 個を想定します。Docker Engine + Compose v2 を用意し、ドメインの A/AAAA をサーバーへ向け、TCP 80/443 のみを一般公開します。SSH は自身の運用方針に従って開放します。DB のポート公開は不要です。アプリの 8000/18001 ポートをインターネット向けに変更しないでください。クラウドプロキシや CDN を使う場合、信頼するプロキシと実 IP 設定を再確認してください。本テンプレートは Caddy への直接接続を前提とします。

1. 上記ブランチをクローンし、`.env.demo.example` を `.env.demo` にコピーして読み取り権限を制限します。

   ```sh
   cp .env.demo.example .env.demo
   chmod 600 .env.demo
   ```

2. `RAG_DEMO_DOMAIN` を自身のドメインに変更します。`https://`、ポート、パスは付けません。`RAG_MODE=local` のまま先にデプロイを検証できます。実 Agent を使う場合は `RAG_MODE=api` とし、API URL、モデル、サーバー専用 API key、各モデルの実際の 100 万 token あたり単価を入力します。サービス側にも利用枠やプロジェクト上限を設定し、強制停止する上限か確認してください。価格が空欄またはゼロの場合、Demo は有料呼び出しを拒否します。

3. 独立した Demo プロジェクトを起動します。専用ボリュームを使い、通常のローカルプロジェクトのデータは使用しません。

   ```sh
   docker compose --env-file .env.demo -f compose.demo.yaml config --quiet
   docker compose --env-file .env.demo -f compose.demo.yaml up --build -d --wait
   ```

   画面共有中に `--quiet` なしの `config` を実行するとキーが展開される可能性があります。DNS と 80/443 が利用できれば Caddy が証明書を取得します。CI は localhost の内部 CA で HTTPS を検証しており、公開ドメイン証明書の取得を意味しません。

4. リポジトリ内の 8 ページの**架空**の制度文書を初期登録します。自身の文書ディレクトリは読み込みません。

   ```sh
   # local モード：モデル利用料なし
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.prepare_demo
   # api モードはこちらを使用。Embedding は課金対象で、予算ガードを通ります
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.prepare_demo --live
   ```

   再実行しても文書は重複しません。Embedding 設定が変わると再インデックスします。他の利用中のナレッジベースにこの初期化コマンドを使わないでください。保守と利用者のリクエストが重ならないよう、初期化後に訪問者アカウントを発行します。

5. 採用担当者ごとに読み取り専用アカウントを作成します。トークンは非公開ファイルにのみ保存し、ログには出力しません。

   ```sh
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.manage_access create-user reviewer-01 --roles demo-reviewer --token-file /app/data/.secrets/reviewer-01.txt
   mkdir -p .secrets
   chmod 700 .secrets
   docker compose --env-file .env.demo -f compose.demo.yaml cp app:/app/data/.secrets/reviewer-01.txt .secrets/reviewer-01.txt
   chmod 600 .secrets/reviewer-01.txt
   ```

   `https://自身のドメイン` とトークンは非公開の連絡手段で相手に送ります。README、URL クエリ、公開 Issue、画像に載せません。ログイン後は HttpOnly / Secure / SameSite=Strict cookie を使います。トークン自体に自動失効機能はなく、展示終了後に管理者が無効化します。

   ```sh
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.manage_access list-users
   docker compose --env-file .env.demo -f compose.demo.yaml exec app python -m scripts.manage_access disable-user USER_ID
   ```

6. ログイン、引用 PDF、日本語 UI、Agent、回答拒否を非公開で検証します。`/api/health` はトークン不要ですが、他のデータには ACL を適用します。Web のアップロード、再インデックス、設定・権限変更は管理者でも無効です。運用はホストの CLI で行います。

## 利用上限と実行上の制約

| 項目 | 既定値 / 動作 |
|---|---|
| ユーザー別の日次リクエスト | 20。新規質問と追加確認への各返信を個別に数え、失敗も含めます |
| サイト全体の日次リクエスト | 100。UTC の日付変更で回復 |
| IP 別リクエスト | 推論は毎分 10 回。ログインは別枠で IP ごとに毎分 10 回、全体で毎分 60 回 |
| 同時推論 | 全体で 2 件、ユーザーごとに 1 件。混雑時は 429 を返し、長い待ち行列は作りません |
| 入力 / 出力 | HTTP リクエスト 64 KiB。モデルへのシリアライズ済み UTF-8 入力は最大 60,000 bytes、出力は最大 4,096 tokens |
| 日次モデル予算 | 既定は設定単価による推定 USD 1。各 API 前に予約し、成功かつ信頼できる使用量を取得した場合のみ差額を戻します |
| 失敗 / 使用量不明 | 予約額全体を維持。暗黙の HTTP 再試行なし。報告された実使用量が予約を超えると、以降の有料リクエストを遮断 |
| 再起動 | 配額と予算は app_data に保持。メモリ上の Agent 追加確認セッションは失われ、やり直しが必要 |
| 規模 | 単一プロセス。同時実行枠はプロセス間で共有せず、複数レプリカ・worker は非対応 |

費用制限は、設定単価、UTF-8 バイト数、プロトコルの余裕分から入力上限を推定します。サービスの請求額を厳密に制限するものではありません。tokenizer、追加料金、誤った単価・使用量報告のリスクが残り、最初の異常超過は応答後にしか検出できません。サービス側の独立した上限も維持してください。予算ガードは Planner、Embedding、Generator、Verifier を対象とし、節約のために Strict を省略しません。

Demo でも権限のある文書の閲覧・PDF ダウンロードは可能なため、公開可能な架空資料だけを登録します。質問は設定したモデルサービスへ送信されます。実在企業の機密情報や個人情報は入力しないでください。運用ログと Agent 出力には利用者の入力が含まれる可能性があり、サーバー上で管理し、公開パッケージに含めません。ボリューム削除は配額、アカウント、予算を消去するため、上限回避には使わないでください。

TLS は [Caddy 自動 HTTPS](https://caddyserver.com/docs/automatic-https)、転送元の識別は [reverse_proxy 文書](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)に基づきます。アプリは固定プロキシ IP のみを信頼し、Caddy が偽造 X-Forwarded-For を上書きします。ネットワーク競合時は `RAG_PROXY_SUBNET`、`RAG_PROXY_IP`、`RAG_APP_IP` を合わせて変更し、両コンテナーに同一サブネット内の異なる IP を割り当てます。継承は [Docker extends](https://docs.docker.com/compose/how-tos/multiple-compose-files/extends/)に従います。

## パッケージ作成と確認

```sh
python -m scripts.source_index --archive
python -m scripts.release_check --git .
```

`exports/knowbase-source-latest.zip` と独立した `exports/knowbase-release-check.json` を生成します。後者は ZIP の SHA-256、ファイル数、検査範囲、検出結果を記録します。対象はソースパッケージ、既知のローカル認証情報、一般的なキー形式、到達可能な全 Git 履歴オブジェクトです。侵入テストではなく、未知の形式や到達不能な履歴の検出は保証しません。最終ファイル確定後に再度パッケージ化・検査します。自己参照ハッシュを避けるため、検査結果は ZIP に含めません。

汎用のオープンソースライセンスは指定していません。採用担当者への公開は任意の再配布許可を意味しません。ライセンス決定時に別途追加します。GitHub Release は最終検収とバージョン決定後に ZIP と検査レポートを公開できます。現時点では tag、PR マージ、Release を自動作成しません。
