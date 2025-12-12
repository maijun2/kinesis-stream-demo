#!/bin/bash

# きのこ vs たけのこ デモ - フロントエンドデプロイスクリプト
# キャッシュを無効化してファイルをアップロード

BUCKET_NAME="kinesis-stream-demo-frontend-891377047426"
REGION="ap-northeast-1"
DISTRIBUTION_ID="E13L9X5TUJR2ST"

echo "🚀 フロントエンドファイルをS3にアップロード中..."

cd frontend

# 全ファイルをno-cacheヘッダー付きでアップロード
aws s3 cp index.html s3://${BUCKET_NAME}/ \
  --cache-control "no-cache, no-store, must-revalidate" \
  --region ${REGION}

aws s3 cp style.css s3://${BUCKET_NAME}/ \
  --cache-control "no-cache, no-store, must-revalidate" \
  --region ${REGION}

aws s3 cp script.js s3://${BUCKET_NAME}/ \
  --cache-control "no-cache, no-store, must-revalidate" \
  --region ${REGION}

aws s3 cp cities.js s3://${BUCKET_NAME}/ \
  --cache-control "no-cache, no-store, must-revalidate" \
  --region ${REGION}

echo "✅ S3アップロード完了"

# CloudFrontキャッシュを無効化
echo "🔄 CloudFrontキャッシュを無効化中..."
CALLER_REF="deploy-$(date +%s)"

aws cloudfront create-invalidation \
  --distribution-id ${DISTRIBUTION_ID} \
  --region us-east-1 \
  --invalidation-batch "{\"Paths\":{\"Quantity\":1,\"Items\":[\"/*\"]},\"CallerReference\":\"${CALLER_REF}\"}"

echo "✅ CloudFrontキャッシュ無効化完了"
echo "🌐 サイトURL: https://d1aupd1z3alw9l.cloudfront.net"
echo "⏰ キャッシュ無効化が完了するまで数分お待ちください"
