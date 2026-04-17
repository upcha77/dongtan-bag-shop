#!/usr/bin/env python3
import requests
import urllib3
import re
import json
import sys
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://61.251.29.212/Gbms_Map"

dong_codes = {
    "동탄1동": "20310023",
    "동탄2동": "20310024",
    "동탄3동": "20310025",
    "동탄4동": "20310026",
    "동탄5동": "20310027",
    "동탄6동": "20310028",
    "동탄7동": "20310029",
    "동탄8동": "20310030",
    "동탄9동": "20310031",
}

bag_codes = {
    "소각용 50L": "10172",
    "소각용 75L": "10192",
}

def parse_shops_response(content):
    data_match = re.search(r'<data>.*?<!\[CDATA\[(.*?)\]\]>.*?</data>', content, re.DOTALL)
    if not data_match:
        return []
    json_str = data_match.group(1).strip()
    if not json_str or json_str == '[]':
        return []
    json_str = re.sub(r"([\w_]+)\s*:\s*'([^']*)'", r'"\1": "\2"', json_str)
    json_str = json_str.replace("'", '"')
    try:
        return json.loads(json_str)
    except:
        return []

def fetch_shops(dong_name, dong_code, bag_name, bag_code):
    params = {
        "dong": dong_code,
        "bag": bag_code,
        "shop": "",
        "attr": "hwasung"
    }
    try:
        response = requests.get(
            f"{base_url}/proc/getsale_list.jsp",
            params=params,
            verify=False,
            timeout=10
        )
        shops = parse_shops_response(response.text)
        for shop in shops:
            shop['DONG'] = dong_name
            shop['BAG_TYPE'] = bag_name
            sale_date = shop.get('SALE_DATE', '')
            if sale_date and len(sale_date) == 8:
                shop['SALE_DATE_FMT'] = f"{sale_date[:4]}-{sale_date[4:6]}-{sale_date[6:]}"
            else:
                shop['SALE_DATE_FMT'] = '-'
            # 좌표 정제
            wedo = float(shop.get('WEDO', 0))
            kgdo = float(shop.get('KGDO', 0))
            if 33 <= wedo <= 38 and 126 <= kgdo <= 129:
                shop['LAT'] = wedo
                shop['LNG'] = kgdo
            else:
                shop['LAT'] = kgdo
                shop['LNG'] = wedo
        return shops
    except Exception as e:
        print(f"Error fetching {dong_name}/{bag_name}: {e}")
        return []

def main():
    # 데이터 수집
    all_shops = []
    for dong_name, dong_code in dong_codes.items():
        for bag_name, bag_code in bag_codes.items():
            shops = fetch_shops(dong_name, dong_code, bag_name, bag_code)
            print(f"{dong_name} + {bag_name}: {len(shops)}개")
            all_shops.extend(shops)

    # 중복 제거 - 상점명+주소+봉투타입으로 유니크 (방식 A: 봉투 타입별 분리)
    seen = set()
    unique_shops = []
    for shop in all_shops:
        key = f"{shop.get('SHOP_NAME', '')}_{shop.get('SAUP_ADDR', '')}_{shop.get('BAG_TYPE', '')}"
        if key not in seen:
            seen.add(key)
            unique_shops.append(shop)

    # JSON 저장
    shops_data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target_areas": list(dong_codes.keys()),
        "target_bags": list(bag_codes.keys()),
        "total_count": len(unique_shops),
        "shops": unique_shops
    }

    with open('shops.json', 'w', encoding='utf-8') as f:
        json.dump(shops_data, f, ensure_ascii=False, indent=2)

    print(f"\n총 {len(unique_shops)}개 판매점 저장 완료")
    return 0

if __name__ == "__main__":
    sys.exit(main())
