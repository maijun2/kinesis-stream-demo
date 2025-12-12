# Kinesis Stream Demo - きのこ vs たけのこ リアルタイム購入サイト

## 概要
Amazon Kinesis Data Streamsを使用したリアルタイムデータ処理のデモアプリケーションです。
ユーザーがブラウザで「きのこの山」または「たけのこの里」の購入ボタンをクリックすると、
リアルタイムで集計結果が全ユーザーの画面に反映されます。

## アーキテクチャ
- **フロントエンド**: HTML/CSS/JavaScript (Chart.js使用)
- **API**: Amazon API Gateway (REST + WebSocket)
- **処理**: AWS Lambda (Python 3.12)
- **ストリーミング**: Amazon Kinesis Data Streams
- **データベース**: Amazon DynamoDB
- **ホスティング**: Amazon S3 + CloudFront

## ディレクトリ構成
```
kinesis-stream-demo/
├── frontend/                 # フロントエンドファイル
│   ├── index.html           # メインHTML
│   ├── style.css            # スタイルシート
│   └── script.js            # JavaScript
├── backend/                 # Lambda関数
│   ├── order-processor/     # 注文処理Lambda
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   ├── data-aggregator/     # データ集計Lambda
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   └── websocket-handler/   # WebSocket管理Lambda
│       ├── lambda_function.py
│       └── requirements.txt
├── infrastructure/          # インフラ定義
│   └── cloudformation.yaml # CloudFormationテンプレート
├── plan.md                 # 構成計画
├── specs.md                # 仕様書
└── README.md               # このファイル
```

## セットアップ手順

### 1. インフラストラクチャのデプロイ
```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation.yaml \
  --stack-name kinesis-stream-demo \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-1
```

### 2. Lambda関数のデプロイ
各Lambda関数のディレクトリで以下を実行：
```bash
cd backend/order-processor
pip install -r requirements.txt -t .
zip -r function.zip .
aws lambda update-function-code --function-name OrderProcessor --zip-file fileb://function.zip
```

### 3. フロントエンドの設定
1. CloudFormationの出力からAPI Gateway URLとWebSocket URLを取得
2. `frontend/script.js`の設定値を更新
3. S3バケットにファイルをアップロード

## 使用方法
1. ブラウザでサイトにアクセス
2. 「きのこの山」または「たけのこの里」のボタンをクリック
3. リアルタイムで集計結果がグラフに反映される
4. 他のユーザーの購入も自動的に画面に反映される

## 技術的な特徴
- **リアルタイム処理**: Kinesis Data Streamsによる高スループットデータ処理
- **サーバーレス**: 完全サーバーレス構成でスケーラブル
- **リアルタイム通信**: WebSocketによる双方向通信
- **自動スケーリング**: AWS管理サービスによる自動スケーリング

## 開発者向け情報

### 環境変数
Lambda関数で使用される環境変数：
- `KINESIS_STREAM_NAME`: Kinesisストリーム名
- `ORDERS_TABLE_NAME`: 注文データテーブル名
- `CONNECTIONS_TABLE_NAME`: WebSocket接続管理テーブル名
- `AGGREGATION_TABLE_NAME`: 集計データテーブル名
- `WEBSOCKET_ENDPOINT`: WebSocket API エンドポイント

### データフロー
1. ユーザーがボタンクリック → API Gateway → Order Processor Lambda
2. Order Processor → Kinesis Data Stream
3. Kinesis → Data Aggregator Lambda
4. Data Aggregator → DynamoDB更新 → WebSocket通知
5. WebSocket → 全クライアントに更新通知

## トラブルシューティング
- WebSocket接続エラー: CORS設定とエンドポイントURLを確認
- データが更新されない: Lambda関数のログを確認
- パフォーマンス問題: Kinesisシャード数とLambda同時実行数を調整
