"""
Script to generate kinoko vs takenoko purchase data and send to Kinesis stream.
きのこ vs たけのこ リアルタイム購入サイト用のクリックストリームデータ生成スクリプト
"""

import json
import random
from datetime import datetime
import sys
import time
import uuid
import requests
import boto3


# 日本の主要都市データ（簡略版）
JAPAN_CITIES = [
    {"name": "東京", "lat": 35.6762, "lng": 139.6503, "region": "関東"},
    {"name": "大阪", "lat": 34.6937, "lng": 135.5023, "region": "関西"},
    {"name": "名古屋", "lat": 35.1815, "lng": 136.9066, "region": "中部"},
    {"name": "札幌", "lat": 43.0642, "lng": 141.3469, "region": "北海道"},
    {"name": "福岡", "lat": 33.5904, "lng": 130.4017, "region": "九州"},
    {"name": "仙台", "lat": 38.2682, "lng": 140.8694, "region": "東北"},
    {"name": "広島", "lat": 34.3853, "lng": 132.4553, "region": "中国"},
    {"name": "京都", "lat": 35.0116, "lng": 135.7681, "region": "関西"},
    {"name": "横浜", "lat": 35.4437, "lng": 139.6380, "region": "関東"},
    {"name": "神戸", "lat": 34.6901, "lng": 135.1956, "region": "関西"},
    {"name": "静岡", "lat": 34.9756, "lng": 138.3828, "region": "中部"},
    {"name": "新潟", "lat": 37.9026, "lng": 139.0232, "region": "中部"},
    {"name": "熊本", "lat": 32.7898, "lng": 130.7417, "region": "九州"},
    {"name": "岡山", "lat": 34.6617, "lng": 133.9341, "region": "中国"},
    {"name": "高松", "lat": 34.3402, "lng": 134.0434, "region": "四国"}
]

# 地域別の重み付け
REGION_WEIGHTS = {
    "関東": 0.35,
    "関西": 0.20,
    "中部": 0.15,
    "九州": 0.12,
    "東北": 0.08,
    "中国": 0.05,
    "四国": 0.03,
    "北海道": 0.02
}


def detect_region():
    try:
        response = requests.get(
            "http://169.254.169.254/latest/dynamic/instance-identity/document"
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        metadata = response.json()
        return metadata["region"]
    except requests.RequestException:
        print("Failed to fetch EC2 instance metadata")
        return None


def generate_order_id():
    """注文IDの生成（既存アプリと同じ形式）"""
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    return f'order_{timestamp}_{unique_id}'


def get_product():
    """きのこ or たけのこをランダムに選択"""
    products = ["kinoko", "takenoko"]
    return random.choice(products)


def get_user_id():
    """ユーザーIDの生成"""
    MAX_USER_ID = 100
    return f"user_{random.randint(1, MAX_USER_ID)}"


def get_timestamp():
    """ISO形式のタイムスタンプを生成"""
    return datetime.utcnow().isoformat() + 'Z'


def get_weighted_random_city():
    """重み付きランダムで日本の都市を選択"""
    random_value = random.random()
    cumulative_weight = 0
    
    for region, weight in REGION_WEIGHTS.items():
        cumulative_weight += weight
        if random_value <= cumulative_weight:
            region_cities = [city for city in JAPAN_CITIES if city["region"] == region]
            if region_cities:
                return random.choice(region_cities)
    
    # フォールバック
    return random.choice(JAPAN_CITIES)


if __name__ == "__main__":
    print("\n=== きのこ vs たけのこ クリックストリーム生成器（地図対応版） ===")
    print("\n Number of arguments:", len(sys.argv), "arguments")
    print("\n Argument List:", str(sys.argv))
    print("\n The program name is:", str(sys.argv[0]))
    
    if len(sys.argv) < 3:
        print("\n使用方法: python clickstream_generator_items.py <stream_name> <max_interval_seconds> [--verbose]")
        print("例: python clickstream_generator_items.py kinesis-stream-demo 5 --verbose")
        sys.exit(1)
    
    stream_name = str(sys.argv[1])
    max_interval = int(sys.argv[2])
    verbose = len(sys.argv) > 3 and str(sys.argv[3]) == "--verbose"
    
    print(f"\n Kinesis Stream名: {stream_name}")
    print(f"\n 最大間隔（秒）: {max_interval}")
    if verbose:
        print("\n Verbose モード: ON")

    # AWS設定
    my_session = boto3.session.Session()
    region = detect_region()
    if not region:
        region = "ap-northeast-1"  # デフォルトリージョン
    print(f"\n リージョン: {region}")
    
    client = boto3.client("kinesis", region_name=region)

    print("\n=== データ生成開始（地図機能付き） ===")
    print("Ctrl+C で停止")
    
    try:
        while True:
            # ランダムな間隔で待機
            delay = random.randint(1, max_interval)
            time.sleep(delay)
            
            # ランダムな日本の都市を選択
            location = get_weighted_random_city()
            
            # きのこvsたけのこアプリ用のデータを生成（位置情報付き）
            order_data = {
                "orderId": generate_order_id(),
                "product": get_product(),
                "timestamp": get_timestamp(),
                "userId": get_user_id(),
                "location": location
            }

            # JSON形式でデータを準備
            if verbose:
                data = json.dumps(order_data, indent=2, ensure_ascii=False)
            else:
                data = json.dumps(order_data, ensure_ascii=False)
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 送信データ:")
            if verbose:
                print(data)
            else:
                product_name = "きのこの山" if order_data["product"] == "kinoko" else "たけのこの里"
                print(f"  {product_name} @ {location['name']}({location['region']})")
            
            # Kinesisに送信
            encoded_data = data.encode("utf-8")
            response = client.put_record(
                StreamName=stream_name, 
                Data=encoded_data, 
                PartitionKey=order_data["product"]  # 商品タイプでパーティション分割
            )

            if verbose:
                print("✅ Kinesis Data Streamに送信完了")
                print(f"ShardId: {response['ShardId']}")
                print(f"SequenceNumber: {response['SequenceNumber']}")
                print(f"HTTPStatusCode: {response['ResponseMetadata']['HTTPStatusCode']}")
            else:
                print(f"✅ 送信完了 (Shard: {response['ShardId']})")
                
    except KeyboardInterrupt:
        print("\n\n=== データ生成を停止しました ===")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    print("\n=== きのこ vs たけのこ クリックストリーム生成器 ===")
    print("\n Number of arguments:", len(sys.argv), "arguments")
    print("\n Argument List:", str(sys.argv))
    print("\n The program name is:", str(sys.argv[0]))
    
    if len(sys.argv) < 3:
        print("\n使用方法: python clickstream_generator_items.py <stream_name> <max_interval_seconds> [--verbose]")
        print("例: python clickstream_generator_items.py kinesis-stream-demo 5 --verbose")
        sys.exit(1)
    
    stream_name = str(sys.argv[1])
    max_interval = int(sys.argv[2])
    verbose = len(sys.argv) > 3 and str(sys.argv[3]) == "--verbose"
    
    print(f"\n Kinesis Stream名: {stream_name}")
    print(f"\n 最大間隔（秒）: {max_interval}")
    if verbose:
        print("\n Verbose モード: ON")

    # AWS設定
    my_session = boto3.session.Session()
    region = detect_region()
    if not region:
        region = "ap-northeast-1"  # デフォルトリージョン
    print(f"\n リージョン: {region}")
    
    client = boto3.client("kinesis", region_name=region)

    print("\n=== データ生成開始 ===")
    print("Ctrl+C で停止")
    
    try:
        while True:
            # ランダムな間隔で待機
            delay = random.randint(1, max_interval)
            time.sleep(delay)
            
            # きのこvsたけのこアプリ用のデータを生成
            order_data = {
                "orderId": generate_order_id(),
                "product": get_product(),
                "timestamp": get_timestamp(),
                "userId": get_user_id()
            }

            # JSON形式でデータを準備
            if verbose:
                data = json.dumps(order_data, indent=2, ensure_ascii=False)
            else:
                data = json.dumps(order_data, ensure_ascii=False)
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 送信データ:")
            print(data)
            
            # Kinesisに送信
            encoded_data = data.encode("utf-8")
            response = client.put_record(
                StreamName=stream_name, 
                Data=encoded_data, 
                PartitionKey=order_data["product"]  # 商品タイプでパーティション分割
            )

            if verbose:
                print("✅ Kinesis Data Streamに送信完了")
                print(f"ShardId: {response['ShardId']}")
                print(f"SequenceNumber: {response['SequenceNumber']}")
                print(f"HTTPStatusCode: {response['ResponseMetadata']['HTTPStatusCode']}")
            else:
                print(f"✅ 送信完了 (Shard: {response['ShardId']})")
                
    except KeyboardInterrupt:
        print("\n\n=== データ生成を停止しました ===")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
