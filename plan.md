# Kinesis Stream サンプルアプリケーション構成計画

## 提案システム構成

### フロントエンド
- **Amazon S3 + CloudFront**: 静的ウェブサイトホスティング
- **HTML/CSS/JavaScript**: シンプルなSPA（Single Page Application）
  - きのこの山・筍の里の購入ボタン
  - リアルタイム棒グラフ表示（Chart.jsなど使用）
  - WebSocketでリアルタイム更新

### バックエンド（サーバーレス構成）
- **Amazon API Gateway**: REST API + WebSocket API
- **AWS Lambda (Python 3.12)**: 
  - 注文処理用Lambda（Kinesis Data Streamへデータ送信）
  - データ集計用Lambda（Kinesis Data Streamからデータ受信・処理）
  - WebSocket接続管理用Lambda
- **Amazon Kinesis Data Streams**: リアルタイムデータストリーミング
- **Amazon DynamoDB**: 
  - 注文データ保存
  - WebSocket接続情報管理
  - 集計結果キャッシュ

### データフロー
1. ユーザーがブラウザで商品購入ボタンをクリック
2. API Gateway経由でLambdaが注文データをKinesis Data Streamに送信
3. Kinesis Data StreamからLambdaがデータを受信し、DynamoDBに保存・集計
4. WebSocket経由で全接続中のクライアントに集計結果をリアルタイム配信
5. ブラウザ上の棒グラフが自動更新

### ファイル構成案
```
kinesis-stream-demo/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/
│   ├── order-processor/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   ├── data-aggregator/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   └── websocket-handler/
│       ├── lambda_function.py
│       └── requirements.txt
├── infrastructure/
│   └── cloudformation.yaml
└── README.md
```

## 技術スタック
- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+), Chart.js
- **バックエンド**: Python 3.12 (AWS Lambda)
- **インフラ**: AWS CloudFormation
- **データベース**: Amazon DynamoDB
- **ストリーミング**: Amazon Kinesis Data Streams
- **API**: Amazon API Gateway (REST + WebSocket)
- **ホスティング**: Amazon S3 + CloudFront

## 開発手順
1. インフラストラクチャの構築（CloudFormation）
2. Lambda関数の実装
3. フロントエンドの開発
4. API Gatewayの設定
5. 統合テスト
6. デプロイメント
