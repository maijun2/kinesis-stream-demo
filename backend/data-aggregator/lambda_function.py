import json
import boto3
import os
import base64
from datetime import datetime
from decimal import Decimal

# AWS サービスクライアント
dynamodb = boto3.resource('dynamodb')
apigateway_client = boto3.client('apigatewaymanagementapi',
                                endpoint_url=os.environ['WEBSOCKET_ENDPOINT'])

# 環境変数
ORDERS_TABLE_NAME = os.environ['ORDERS_TABLE_NAME']
CONNECTIONS_TABLE_NAME = os.environ['CONNECTIONS_TABLE_NAME']
AGGREGATION_TABLE_NAME = os.environ['AGGREGATION_TABLE_NAME']

# DynamoDBテーブル
orders_table = dynamodb.Table(ORDERS_TABLE_NAME)
connections_table = dynamodb.Table(CONNECTIONS_TABLE_NAME)
aggregation_table = dynamodb.Table(AGGREGATION_TABLE_NAME)

def lambda_handler(event, context):
    print(f'Received Kinesis event: {json.dumps(event)}')
    
    try:
        # Kinesisレコードを処理
        for record in event['Records']:
            # Base64デコードしてJSONパース
            data = json.loads(base64.b64decode(record['kinesis']['data']).decode('utf-8'))
            print(f'Processing order: {data}')
            
            # 注文データをDynamoDBに保存
            save_order(data)
            
            # 集計データを更新
            update_aggregation(data['product'])
            
            # WebSocket経由で全クライアントに更新を通知（新しい注文情報を含む）
            notify_clients(data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Successfully processed records'})
        }
        
    except Exception as error:
        print(f'Error processing Kinesis records: {str(error)}')
        raise error

def save_order(order_data):
    """注文データをDynamoDBに保存"""
    try:
        # TTL（24時間後に削除）
        ttl = int(datetime.utcnow().timestamp()) + (24 * 60 * 60)
        
        # 保存するアイテムを準備
        item = {
            'orderId': order_data['orderId'],
            'product': order_data['product'],
            'timestamp': order_data['timestamp'],
            'userId': order_data['userId'],
            'ttl': ttl
        }
        
        # 位置情報がある場合は追加（Float値をDecimalに変換）
        if 'location' in order_data and order_data['location']:
            location = order_data['location'].copy()
            if 'lat' in location:
                location['lat'] = Decimal(str(location['lat']))
            if 'lng' in location:
                location['lng'] = Decimal(str(location['lng']))
            item['location'] = location
        
        orders_table.put_item(Item=item)
        print(f'Order saved to DynamoDB: {order_data["orderId"]}')
        
    except Exception as error:
        print(f'Error saving order: {str(error)}')
        raise error

def update_aggregation(product):
    """集計データを更新"""
    try:
        response = aggregation_table.update_item(
            Key={'product': product},
            UpdateExpression='ADD #count :increment',
            ExpressionAttributeNames={'#count': 'count'},
            ExpressionAttributeValues={':increment': 1},
            ReturnValues='ALL_NEW'
        )
        print(f'Aggregation updated: {response["Attributes"]}')
        return response['Attributes']
        
    except Exception as error:
        print(f'Error updating aggregation: {str(error)}')
        raise error

def get_current_aggregation():
    """現在の集計データを取得"""
    try:
        response = aggregation_table.scan()
        
        aggregation = {
            'kinoko': 0,
            'takenoko': 0
        }
        
        for item in response['Items']:
            product = item['product']
            count = int(item.get('count', 0))
            aggregation[product] = count
        
        return aggregation
        
    except Exception as error:
        print(f'Error getting current aggregation: {str(error)}')
        return {'kinoko': 0, 'takenoko': 0}

def notify_clients(new_order=None):
    """WebSocket経由で全クライアントに通知"""
    try:
        # 現在の集計データを取得
        aggregation = get_current_aggregation()
        
        # 接続中のクライアント一覧を取得
        connections_response = connections_table.scan()
        
        # 各クライアントにメッセージを送信
        message_data = {
            'type': 'update',
            'data': aggregation,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # 新しい注文情報がある場合は追加
        if new_order:
            message_data['data']['newOrder'] = new_order
        
        message = json.dumps(message_data, cls=DecimalEncoder)
        
        for connection in connections_response['Items']:
            connection_id = connection['connectionId']
            try:
                apigateway_client.post_to_connection(
                    ConnectionId=connection_id,
                    Data=message
                )
                print(f'Message sent to connection: {connection_id}')
                
            except apigateway_client.exceptions.GoneException:
                # 接続が切れている場合は削除
                print(f'Removing stale connection: {connection_id}')
                connections_table.delete_item(
                    Key={'connectionId': connection_id}
                )
            except Exception as error:
                print(f'Error sending message to connection {connection_id}: {str(error)}')
        
        print('Notifications sent to all clients')
        
    except Exception as error:
        print(f'Error notifying clients: {str(error)}')

# DynamoDB用のJSONエンコーダー（Decimalサポート）
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)
