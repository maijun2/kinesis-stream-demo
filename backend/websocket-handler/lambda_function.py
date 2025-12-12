import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# AWS サービスクライアント
dynamodb = boto3.resource('dynamodb')

# 環境変数
CONNECTIONS_TABLE_NAME = os.environ['CONNECTIONS_TABLE_NAME']
AGGREGATION_TABLE_NAME = os.environ['AGGREGATION_TABLE_NAME']
WEBSOCKET_ENDPOINT = os.environ['WEBSOCKET_ENDPOINT']

# DynamoDBテーブル
connections_table = dynamodb.Table(CONNECTIONS_TABLE_NAME)
aggregation_table = dynamodb.Table(AGGREGATION_TABLE_NAME)

def lambda_handler(event, context):
    print(f'WebSocket event: {json.dumps(event)}')
    
    route_key = event['requestContext']['routeKey']
    connection_id = event['requestContext']['connectionId']
    
    try:
        if route_key == '$connect':
            handle_connect(connection_id)
        elif route_key == '$disconnect':
            handle_disconnect(connection_id)
        elif route_key == 'getCurrentData':
            handle_get_current_data(event)
        else:
            print(f'Unknown route: {route_key}')
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success'})
        }
        
    except Exception as error:
        print(f'WebSocket handler error: {str(error)}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_connect(connection_id):
    """WebSocket接続時の処理"""
    print(f'New WebSocket connection: {connection_id}')
    
    try:
        # 接続情報をDynamoDBに保存
        ttl = int(datetime.utcnow().timestamp()) + (2 * 60 * 60)  # 2時間後に削除
        
        connections_table.put_item(
            Item={
                'connectionId': connection_id,
                'timestamp': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
        )
        
        # 現在の集計データを取得して送信
        current_data = get_current_aggregation()
        send_initial_data(connection_id, current_data)
        
        print(f'Connection {connection_id} registered and initial data sent')
        
    except Exception as error:
        print(f'Error handling connect: {str(error)}')
        raise error

def send_initial_data(connection_id, aggregation_data):
    """WebSocket接続時に初期データを送信"""
    try:
        apigateway_client = boto3.client('apigatewaymanagementapi',
                                       endpoint_url=WEBSOCKET_ENDPOINT)
        
        message = json.dumps({
            'type': 'update',
            'data': aggregation_data,
            'timestamp': datetime.utcnow().isoformat()
        }, cls=DecimalEncoder)
        
        apigateway_client.post_to_connection(
            ConnectionId=connection_id,
            Data=message
        )
        print(f'Initial data sent to connection: {connection_id}')
        
    except Exception as error:
        print(f'Error sending initial data to connection {connection_id}: {str(error)}')
        # 初期データ送信エラーは無視（接続は維持）

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

def handle_disconnect(connection_id):
    """WebSocket切断時の処理"""
    print(f'WebSocket disconnection: {connection_id}')
    
    try:
        connections_table.delete_item(
            Key={'connectionId': connection_id}
        )
        print('Connection removed from DynamoDB')
        
    except Exception as error:
        print(f'Error handling disconnect: {str(error)}')
        # 切断時のエラーは無視する

def handle_get_current_data(event):
    """現在のデータ取得リクエストの処理"""
    connection_id = event['requestContext']['connectionId']
    send_current_data(connection_id)

def send_current_data(connection_id):
    """現在の集計データをクライアントに送信"""
    try:
        # 現在の集計データを取得
        aggregation = get_current_aggregation()
        
        # WebSocket経由でデータを送信
        apigateway_client = boto3.client('apigatewaymanagementapi',
                                       endpoint_url=WEBSOCKET_ENDPOINT)
        
        message = json.dumps({
            'type': 'update',
            'data': aggregation,
            'timestamp': datetime.utcnow().isoformat()
        }, cls=DecimalEncoder)
        
        try:
            apigateway_client.post_to_connection(
                ConnectionId=connection_id,
                Data=message
            )
            print(f'Current data sent to connection: {connection_id}')
        except apigateway_client.exceptions.GoneException:
            # 接続が切れている場合は削除
            print(f'Connection {connection_id} is gone, removing from table')
            connections_table.delete_item(
                Key={'connectionId': connection_id}
            )
        except Exception as send_error:
            print(f'Error sending data to connection {connection_id}: {str(send_error)}')
            
    except Exception as error:
        print(f'Error in send_current_data: {str(error)}')
        # エラーが発生してもWebSocket接続処理は続行

# DynamoDB用のJSONエンコーダー（Decimalサポート）
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)
