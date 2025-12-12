import json
import boto3
import os
import uuid
from datetime import datetime

# AWS サービスクライアント
kinesis = boto3.client('kinesis')

# 環境変数
STREAM_NAME = os.environ['KINESIS_STREAM_NAME']

def lambda_handler(event, context):
    print(f'Received event: {json.dumps(event)}')
    
    try:
        # リクエストボディの解析
        body = json.loads(event['body'])
        product = body.get('product')
        timestamp = body.get('timestamp')
        location = body.get('location')  # 位置情報を追加
        
        # バリデーション
        if not product or product not in ['kinoko', 'takenoko']:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Invalid product type'
                })
            }
        
        # Kinesisに送信するデータを準備
        order_data = {
            'orderId': generate_order_id(),
            'product': product,
            'timestamp': timestamp or datetime.utcnow().isoformat(),
            'userId': event.get('requestContext', {}).get('connectionId', 'anonymous'),
            'location': location  # 位置情報を追加
        }
        
        print(f'Order data with location: {json.dumps(order_data)}')
        
        # Kinesis Data Streamにデータを送信
        response = kinesis.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps(order_data),
            PartitionKey=product  # 商品タイプでパーティション分割
        )
        
        print(f'Successfully sent to Kinesis: {response}')
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'orderId': order_data['orderId'],
                'sequenceNumber': response['SequenceNumber'],
                'location': location
            })
        }
        
    except Exception as error:
        print(f'Error processing order: {str(error)}')
        
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }

def options_handler(event, context):
    """OPTIONSリクエスト（CORS対応）"""
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': ''
    }

def generate_order_id():
    """注文IDの生成"""
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    return f'order_{timestamp}_{unique_id}'
