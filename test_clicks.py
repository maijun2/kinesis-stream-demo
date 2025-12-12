#!/usr/bin/env python3
import requests
import json
import random
import time
from datetime import datetime

# 日本の都市データ（cities.jsから抜粋）
CITIES = [
    {"name": "東京", "lat": 35.6762, "lng": 139.6503, "region": "関東", "weight": 10},
    {"name": "大阪", "lat": 34.6937, "lng": 135.5023, "region": "関西", "weight": 8},
    {"name": "横浜", "lat": 35.4437, "lng": 139.6380, "region": "関東", "weight": 7},
    {"name": "名古屋", "lat": 35.1815, "lng": 136.9066, "region": "中部", "weight": 6},
    {"name": "札幌", "lat": 43.0642, "lng": 141.3469, "region": "北海道", "weight": 5},
    {"name": "神戸", "lat": 34.6901, "lng": 135.1956, "region": "関西", "weight": 4},
    {"name": "京都", "lat": 35.0116, "lng": 135.7681, "region": "関西", "weight": 4},
    {"name": "福岡", "lat": 33.5904, "lng": 130.4017, "region": "九州", "weight": 4},
    {"name": "川崎", "lat": 35.5308, "lng": 139.7029, "region": "関東", "weight": 3},
    {"name": "さいたま", "lat": 35.8617, "lng": 139.6455, "region": "関東", "weight": 3},
    {"name": "広島", "lat": 34.3853, "lng": 132.4553, "region": "中国", "weight": 3},
    {"name": "仙台", "lat": 38.2682, "lng": 140.8694, "region": "東北", "weight": 3},
    {"name": "千葉", "lat": 35.6074, "lng": 140.1065, "region": "関東", "weight": 2},
    {"name": "北九州", "lat": 33.8834, "lng": 130.8751, "region": "九州", "weight": 2},
    {"name": "浜松", "lat": 34.7108, "lng": 137.7261, "region": "中部", "weight": 2}
]

# API Gateway URL
API_URL = "https://v04tokbw1g.execute-api.ap-northeast-1.amazonaws.com/prod/purchase"

def weighted_random_city():
    """重み付きランダムで都市を選択"""
    weights = [city["weight"] for city in CITIES]
    return random.choices(CITIES, weights=weights)[0]

def generate_order():
    """注文データを生成"""
    city = weighted_random_city()
    product = random.choice(["kinoko", "takenoko"])
    
    order_data = {
        "product": product,
        "location": {
            "name": city["name"],
            "lat": city["lat"],
            "lng": city["lng"],
            "region": city["region"]
        }
    }
    
    return order_data

def send_order(order_data):
    """注文をAPIに送信"""
    try:
        response = requests.post(
            API_URL,
            json=order_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ 注文送信成功: {order_data['product']} from {order_data['location']['name']}")
            return True
        else:
            print(f"❌ 注文送信失敗: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("🚀 きのこ vs たけのこ テストクリック生成開始")
    print(f"📡 API URL: {API_URL}")
    print("-" * 50)
    
    success_count = 0
    total_count = 20  # 20回のテスト注文を生成
    
    for i in range(total_count):
        order_data = generate_order()
        
        print(f"[{i+1:2d}/{total_count}] ", end="")
        if send_order(order_data):
            success_count += 1
        
        # 1-3秒のランダム間隔
        time.sleep(random.uniform(1, 3))
    
    print("-" * 50)
    print(f"📊 結果: {success_count}/{total_count} 件成功")
    print("🎉 テスト完了！ブラウザで結果を確認してください。")
    print(f"🌐 URL: https://d1aupd1z3alw9l.cloudfront.net")

if __name__ == "__main__":
    main()
