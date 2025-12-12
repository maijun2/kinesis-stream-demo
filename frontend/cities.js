// 日本の主要都市データ
const JAPAN_CITIES = [
    // 北海道・東北
    {name: "札幌", lat: 43.0642, lng: 141.3469, region: "北海道"},
    {name: "仙台", lat: 38.2682, lng: 140.8694, region: "東北"},
    {name: "青森", lat: 40.8244, lng: 140.7400, region: "東北"},
    {name: "盛岡", lat: 39.7036, lng: 141.1527, region: "東北"},
    {name: "秋田", lat: 39.7186, lng: 140.1024, region: "東北"},
    {name: "山形", lat: 38.2404, lng: 140.3633, region: "東北"},
    {name: "福島", lat: 37.7503, lng: 140.4676, region: "東北"},
    
    // 関東
    {name: "東京", lat: 35.6762, lng: 139.6503, region: "関東"},
    {name: "横浜", lat: 35.4437, lng: 139.6380, region: "関東"},
    {name: "千葉", lat: 35.6074, lng: 140.1065, region: "関東"},
    {name: "さいたま", lat: 35.8617, lng: 139.6455, region: "関東"},
    {name: "宇都宮", lat: 36.5658, lng: 139.8836, region: "関東"},
    {name: "前橋", lat: 36.3911, lng: 139.0608, region: "関東"},
    {name: "水戸", lat: 36.3418, lng: 140.4468, region: "関東"},
    
    // 中部
    {name: "名古屋", lat: 35.1815, lng: 136.9066, region: "中部"},
    {name: "静岡", lat: 34.9756, lng: 138.3828, region: "中部"},
    {name: "新潟", lat: 37.9026, lng: 139.0232, region: "中部"},
    {name: "富山", lat: 36.6959, lng: 137.2139, region: "中部"},
    {name: "金沢", lat: 36.5944, lng: 136.6256, region: "中部"},
    {name: "福井", lat: 36.0652, lng: 136.2217, region: "中部"},
    {name: "甲府", lat: 35.6642, lng: 138.5684, region: "中部"},
    {name: "長野", lat: 36.6513, lng: 138.1810, region: "中部"},
    {name: "岐阜", lat: 35.3912, lng: 136.7223, region: "中部"},
    
    // 関西
    {name: "大阪", lat: 34.6937, lng: 135.5023, region: "関西"},
    {name: "京都", lat: 35.0116, lng: 135.7681, region: "関西"},
    {name: "神戸", lat: 34.6901, lng: 135.1956, region: "関西"},
    {name: "奈良", lat: 34.6851, lng: 135.8048, region: "関西"},
    {name: "大津", lat: 35.0045, lng: 135.8686, region: "関西"},
    {name: "和歌山", lat: 34.2261, lng: 135.1675, region: "関西"},
    
    // 中国・四国
    {name: "広島", lat: 34.3853, lng: 132.4553, region: "中国"},
    {name: "岡山", lat: 34.6617, lng: 133.9341, region: "中国"},
    {name: "山口", lat: 34.1858, lng: 131.4706, region: "中国"},
    {name: "鳥取", lat: 35.5038, lng: 134.2380, region: "中国"},
    {name: "松江", lat: 35.4723, lng: 133.0505, region: "中国"},
    {name: "高松", lat: 34.3402, lng: 134.0434, region: "四国"},
    {name: "松山", lat: 33.8416, lng: 132.7657, region: "四国"},
    {name: "高知", lat: 33.5597, lng: 133.5311, region: "四国"},
    {name: "徳島", lat: 34.0658, lng: 134.5594, region: "四国"},
    
    // 九州・沖縄
    {name: "福岡", lat: 33.5904, lng: 130.4017, region: "九州"},
    {name: "北九州", lat: 33.8834, lng: 130.8751, region: "九州"},
    {name: "佐賀", lat: 33.2494, lng: 130.2989, region: "九州"},
    {name: "長崎", lat: 32.7503, lng: 129.8779, region: "九州"},
    {name: "熊本", lat: 32.7898, lng: 130.7417, region: "九州"},
    {name: "大分", lat: 33.2382, lng: 131.6126, region: "九州"},
    {name: "宮崎", lat: 31.9077, lng: 131.4202, region: "九州"},
    {name: "鹿児島", lat: 31.5966, lng: 130.5571, region: "九州"},
    {name: "那覇", lat: 26.2124, lng: 127.6792, region: "沖縄"}
];

// ランダムな都市を選択する関数
function getRandomJapaneseCity() {
    const randomIndex = Math.floor(Math.random() * JAPAN_CITIES.length);
    return JAPAN_CITIES[randomIndex];
}

// 地域別の重み付け（人口密度を考慮）
const REGION_WEIGHTS = {
    "関東": 0.35,    // 35%
    "関西": 0.20,    // 20%
    "中部": 0.15,    // 15%
    "九州": 0.12,    // 12%
    "東北": 0.08,    // 8%
    "中国": 0.05,    // 5%
    "四国": 0.03,    // 3%
    "北海道": 0.02   // 2%
};

// 重み付きランダム選択
function getWeightedRandomCity() {
    const random = Math.random();
    let cumulativeWeight = 0;
    
    for (const [region, weight] of Object.entries(REGION_WEIGHTS)) {
        cumulativeWeight += weight;
        if (random <= cumulativeWeight) {
            const regionCities = JAPAN_CITIES.filter(city => city.region === region);
            const randomIndex = Math.floor(Math.random() * regionCities.length);
            return regionCities[randomIndex];
        }
    }
    
    // フォールバック
    return getRandomJapaneseCity();
}
