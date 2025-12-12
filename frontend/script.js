// グローバル変数
let chart;
let websocket;
let map;
let salesData = {
    kinoko: 0,
    takenoko: 0
};

// API設定
const API_ENDPOINT = 'https://v04tokbw1g.execute-api.ap-northeast-1.amazonaws.com/prod';
const WEBSOCKET_ENDPOINT = 'wss://svo2gfv6ml.execute-api.ap-northeast-1.amazonaws.com/prod';

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    initChart();
    initMap();
    initWebSocket();
    initEventListeners();
    loadInitialData();
});

// 地図の初期化
function initMap() {
    // 日本中心の地図を作成
    map = L.map('map').setView([36.2048, 138.2529], 6);
    
    // OpenStreetMapタイルを追加
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    console.log('地図が初期化されました');
}

// 地図にマーカーを追加
function addMarkerToMap(product, location) {
    if (!map || !location) return;
    
    // 商品に応じた色を設定
    const color = product === 'kinoko' ? '#D2691E' : '#32CD32';
    const borderColor = product === 'kinoko' ? '#8B4513' : '#228B22';
    
    // カスタムアイコンを作成
    const customIcon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            width: 12px;
            height: 12px;
            background-color: ${color};
            border: 2px solid ${borderColor};
            border-radius: 50%;
            box-shadow: 0 0 4px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });
    
    // マーカーを地図に追加
    const marker = L.marker([location.lat, location.lng], {
        icon: customIcon
    }).addTo(map);
    
    // ポップアップを追加
    const productName = product === 'kinoko' ? 'きのこの山' : 'たけのこの里';
    marker.bindPopup(`
        <div style="text-align: center;">
            <strong>${productName}</strong><br>
            📍 ${location.name}<br>
            <small>${location.region}</small>
        </div>
    `);
    
    // マーカーにアニメーション効果を追加
    setTimeout(() => {
        marker.getElement().style.animation = 'bounce 0.6s ease-out';
    }, 100);
    
    console.log(`マーカー追加: ${productName} at ${location.name}`);
}

// チャートの初期化
function initChart() {
    const ctx = document.getElementById('salesChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['きのこの山', 'たけのこの里'],
            datasets: [{
                data: [salesData.kinoko, salesData.takenoko],
                backgroundColor: ['#D2691E', '#32CD32'],
                borderColor: ['#8B4513', '#228B22'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// WebSocket接続の初期化
function initWebSocket() {
    console.log('WebSocket接続を開始します:', WEBSOCKET_ENDPOINT);
    websocket = new WebSocket(WEBSOCKET_ENDPOINT);
    
    websocket.onopen = function(event) {
        console.log('WebSocket接続が確立されました');
        console.log('Calling updateConnectionStatus with connected');
        updateConnectionStatus('connected');
    };
    
    websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('WebSocketメッセージ受信:', data);
        
        if (data.type === 'update') {
            updateDisplay(data.data);
            
            // 地図にマーカーを追加（新しい購入があった場合）
            if (data.data.newOrder) {
                const order = data.data.newOrder;
                if (order.location) {
                    addMarkerToMap(order.product, order.location);
                }
            }
        }
    };
    
    websocket.onclose = function(event) {
        console.log('WebSocket接続が閉じられました', event);
        updateConnectionStatus('disconnected');
        // 再接続を試行
        setTimeout(initWebSocket, 3000);
    };
    
    websocket.onerror = function(error) {
        console.error('WebSocketエラー:', error);
        updateConnectionStatus('error');
    };
}

// 接続状況の表示更新
function updateConnectionStatus(status) {
    console.log('updateConnectionStatus called with status:', status);
    
    const statusElement = document.getElementById('connection-status');
    console.log('Existing status element:', statusElement);
    
    if (!statusElement) {
        // 接続状況表示要素を作成
        console.log('Creating new status element');
        const statusDiv = document.createElement('div');
        statusDiv.id = 'connection-status';
        statusDiv.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            z-index: 1000;
        `;
        document.body.appendChild(statusDiv);
        console.log('Status element created and appended to body');
    }
    
    const statusEl = document.getElementById('connection-status');
    console.log('Status element after creation/retrieval:', statusEl);
    
    switch(status) {
        case 'connected':
            statusEl.textContent = '🟢 接続済み';
            statusEl.style.backgroundColor = '#d4edda';
            statusEl.style.color = '#155724';
            break;
        case 'disconnected':
            statusEl.textContent = '🔴 切断中';
            statusEl.style.backgroundColor = '#f8d7da';
            statusEl.style.color = '#721c24';
            break;
        case 'error':
            statusEl.textContent = '⚠️ エラー';
            statusEl.style.backgroundColor = '#fff3cd';
            statusEl.style.color = '#856404';
            break;
        default:
            statusEl.textContent = '🟡 接続中...';
            statusEl.style.backgroundColor = '#fff3cd';
            statusEl.style.color = '#856404';
    }
    
    console.log('Status element updated:', statusEl.textContent, statusEl.style.backgroundColor);
}

// イベントリスナーの初期化
function initEventListeners() {
    document.getElementById('kinoko-btn').addEventListener('click', () => {
        purchaseProduct('kinoko');
    });
    
    document.getElementById('takenoko-btn').addEventListener('click', () => {
        purchaseProduct('takenoko');
    });
}

// 商品購入処理
async function purchaseProduct(product) {
    try {
        // ランダムな日本の都市を選択
        const location = getWeightedRandomCity();
        
        const response = await fetch(`${API_ENDPOINT}/purchase`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product: product,
                timestamp: new Date().toISOString(),
                location: location
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('購入成功:', result);
            
            // 即座に地図にマーカーを追加
            addMarkerToMap(product, location);
        } else {
            console.error('購入エラー:', response.statusText);
        }
    } catch (error) {
        console.error('購入処理でエラーが発生しました:', error);
    }
}

// 表示の更新
function updateDisplay(data) {
    console.log('表示更新データ:', data);
    
    // 売上データを更新
    salesData.kinoko = data.kinoko || 0;
    salesData.takenoko = data.takenoko || 0;
    
    // チャートを更新
    chart.data.datasets[0].data = [salesData.kinoko, salesData.takenoko];
    chart.update();
    
    // 統計表示を更新
    document.getElementById('kinoko-count').textContent = salesData.kinoko;
    document.getElementById('takenoko-count').textContent = salesData.takenoko;
    
    console.log('表示更新完了:', salesData);
}

// 初期データの読み込み
async function loadInitialData() {
    try {
        // WebSocket接続時に初期データを送信するよう修正予定
        console.log('初期データ読み込み完了');
    } catch (error) {
        console.error('初期データ読み込みエラー:', error);
    }
}

// CSSアニメーションを追加
const style = document.createElement('style');
style.textContent = `
    @keyframes bounce {
        0%, 20%, 60%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        80% {
            transform: translateY(-5px);
        }
    }
`;
document.head.appendChild(style);
