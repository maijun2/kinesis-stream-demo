"""
Script to generate kinoko vs takenoko purchase data with better regional distribution
きのこ vs たけのこ リアルタイム購入サイト用のクリックストリームデータ生成スクリプト（地方都市重視版）
"""

import json
import random
from datetime import datetime
import sys
import time
import uuid
import requests
import boto3


# 日本の都市データ（地方都市を大幅に追加）
JAPAN_CITIES = [
    # 関東地方
    {"name": "東京", "lat": 35.6762, "lng": 139.6503, "region": "関東"},
    {"name": "横浜", "lat": 35.4437, "lng": 139.6380, "region": "関東"},
    {"name": "千葉", "lat": 35.6074, "lng": 140.1065, "region": "関東"},
    {"name": "さいたま", "lat": 35.8617, "lng": 139.6455, "region": "関東"},
    {"name": "宇都宮", "lat": 36.5658, "lng": 139.8836, "region": "関東"},
    {"name": "前橋", "lat": 36.3911, "lng": 139.0608, "region": "関東"},
    {"name": "水戸", "lat": 36.3418, "lng": 140.4468, "region": "関東"},
    
    # 関西地方
    {"name": "大阪", "lat": 34.6937, "lng": 135.5023, "region": "関西"},
    {"name": "京都", "lat": 35.0116, "lng": 135.7681, "region": "関西"},
    {"name": "神戸", "lat": 34.6901, "lng": 135.1956, "region": "関西"},
    {"name": "奈良", "lat": 34.6851, "lng": 135.8048, "region": "関西"},
    {"name": "大津", "lat": 35.0045, "lng": 135.8686, "region": "関西"},
    {"name": "和歌山", "lat": 34.2261, "lng": 135.1675, "region": "関西"},
    
    # 中部地方
    {"name": "名古屋", "lat": 35.1815, "lng": 136.9066, "region": "中部"},
    {"name": "静岡", "lat": 34.9756, "lng": 138.3828, "region": "中部"},
    {"name": "新潟", "lat": 37.9026, "lng": 139.0232, "region": "中部"},
    {"name": "金沢", "lat": 36.5944, "lng": 136.6256, "region": "中部"},
    {"name": "富山", "lat": 36.6959, "lng": 137.2139, "region": "中部"},
    {"name": "福井", "lat": 36.0652, "lng": 136.2216, "region": "中部"},
    {"name": "甲府", "lat": 35.6642, "lng": 138.5684, "region": "中部"},
    {"name": "長野", "lat": 36.6513, "lng": 138.1810, "region": "中部"},
    {"name": "岐阜", "lat": 35.3912, "lng": 136.7223, "region": "中部"},
    
    # 東北地方
    {"name": "仙台", "lat": 38.2682, "lng": 140.8694, "region": "東北"},
    {"name": "青森", "lat": 40.8244, "lng": 140.7400, "region": "東北"},
    {"name": "盛岡", "lat": 39.7036, "lng": 141.1527, "region": "東北"},
    {"name": "秋田", "lat": 39.7186, "lng": 140.1024, "region": "東北"},
    {"name": "山形", "lat": 38.2404, "lng": 140.3633, "region": "東北"},
    {"name": "福島", "lat": 37.7503, "lng": 140.4676, "region": "東北"},
    
    # 九州・沖縄地方
    {"name": "福岡", "lat": 33.5904, "lng": 130.4017, "region": "九州"},
    {"name": "熊本", "lat": 32.7898, "lng": 130.7417, "region": "九州"},
    {"name": "鹿児島", "lat": 31.5966, "lng": 130.5571, "region": "九州"},
    {"name": "宮崎", "lat": 31.9077, "lng": 131.4202, "region": "九州"},
    {"name": "大分", "lat": 33.2382, "lng": 131.6126, "region": "九州"},
    {"name": "長崎", "lat": 32.7503, "lng": 129.8779, "region": "九州"},
    {"name": "佐賀", "lat": 33.2494, "lng": 130.2989, "region": "九州"},
    {"name": "那覇", "lat": 26.2124, "lng": 127.6792, "region": "沖縄"},
    
    # 中国地方
    {"name": "広島", "lat": 34.3853, "lng": 132.4553, "region": "中国"},
    {"name": "岡山", "lat": 34.6617, "lng": 133.9341, "region": "中国"},
    {"name": "山口", "lat": 34.1859, "lng": 131.4706, "region": "中国"},
    {"name": "鳥取", "lat": 35.5038, "lng": 134.2380, "region": "中国"},
    {"name": "松江", "lat": 35.4723, "lng": 133.0505, "region": "中国"},
    
    # 四国地方
    {"name": "高松", "lat": 34.3402, "lng": 134.0434, "region": "四国"},
    {"name": "松山", "lat": 33.8416, "lng": 132.7656, "region": "四国"},
    {"name": "高知", "lat": 33.5597, "lng": 133.5311, "region": "四国"},
    {"name": "徳島", "lat": 34.0658, "lng": 134.5594, "region": "四国"},
    
    # 北海道地方
    {"name": "札幌", "lat": 43.0642, "lng": 141.3469, "region": "北海道"},
    {"name": "函館", "lat": 41.7687, "lng": 140.7290, "region": "北海道"},
    {"name": "旭川", "lat": 43.7711, "lng": 142.3649, "region": "北海道"},
    {"name": "釧路", "lat": 42.9849, "lng": 144.3820, "region": "北海道"},
    {"name": "帯広", "lat": 42.9244, "lng": 143.2142, "region": "北海道"},
]

# より均等な地域別重み付け（地方都市重視）
REGION_WEIGHTS = {
    "関東": 0.25,      # 従来0.35から削減
    "関西": 0.18,      # 従来0.20から削減
    "中部": 0.15,      # 維持
    "九州": 0.12,      # 維持
    "東北": 0.10,      # 従来0.08から増加
    "中国": 0.08,      # 従来0.05から増加
    "四国": 0.06,      # 従来0.03から増加
    "北海道": 0.04,    # 従来0.02から増加
    "沖縄": 0.02       # 新規追加
}


def detect_region():
    try:
        response = requests.get(
            "http://169.254.169.254/latest/dynamic/instance-identity/document"
        )
        response.raise_for_status()
        metadata = response.json()
        return metadata["region"]
    except requests.RequestException:
        print("Failed to fetch EC2 instance metadata")
        return None


def generate_order_id():
    """注文IDの生成"""
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
    """重み付きランダムで日本の都市を選択（地方都市重視）"""
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
    print("\n=== きのこ vs たけのこ クリックストリーム生成器（地方都市重視版） ===")
    print("\n Number of arguments:", len(sys.argv), "arguments")
    print("\n Argument List:", str(sys.argv))
    print("\n The program name is:", str(sys.argv[0]))
    
    if len(sys.argv) < 3:
        print("\n使用方法: python clickstream_generator_regional.py <stream_name> <max_interval_seconds> [--verbose]")
        print("例: python clickstream_generator_regional.py kinesis-stream-demo-stream 1 --verbose")
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

    print("\n=== データ生成開始（地方都市重視版） ===")
    print(f"対象都市数: {len(JAPAN_CITIES)}都市")
    print("地域別重み付け:")
    for region, weight in REGION_WEIGHTS.items():
        region_count = len([city for city in JAPAN_CITIES if city["region"] == region])
        print(f"  {region}: {weight*100:.1f}% ({region_count}都市)")
    print("Ctrl+C で停止")
    
    try:
        while True:
            # ランダムな間隔で待機
            delay = random.randint(1, max_interval)
            time.sleep(delay)
            
            # ランダムな日本の都市を選択（地方都市重視）
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
