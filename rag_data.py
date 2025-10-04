import requests
import json
import csv

API_KEY = "9b9102e7db33f3b8c53b30b6d08cfb33f3cf819da393a689e18251dcd9eaa011"
url = "http://apis.data.go.kr/1790387/EIDAPIService/Region"
params = {
    "serviceKey": API_KEY,
    "resType": "2",         # JSON
    "searchType": "1",
    "searchYear": "2024",
    "searchSidoCd": "11",
    "pageNo": "1",
    "numOfRows": "10"
}

response = requests.get(url, params=params, verify=False)
print("응답 코드:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))  # 전체 구조 확인

    # ✅ response -> body -> items -> item
    items = data["response"]["body"]["items"]["item"]

    filtered = [
        {
            "year": item["year"],
            "sidoNm": item["sidoNm"],
            "icdNm": item["icdNm"],
            "resultVal": item["resultVal"]
        }
        for item in items
    ]

    with open("disease_region_filtered.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    with open("disease_region_filtered.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["year", "sidoNm", "icdNm", "resultVal"])
        writer.writeheader()
        writer.writerows(filtered)

    print("필요한 데이터만 저장 완료!")
else:
    print("API 호출 실패:", response.text)
