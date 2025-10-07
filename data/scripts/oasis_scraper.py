# oasis_scraper.py
import requests
from bs4 import BeautifulSoup
import json
import time
import os

# ===============================
# 🌿 약재 데이터 수집 (Herb)
# ===============================
def scrape_herbs(start=1, end=30):
    """
    OASIS 한약재 상세 페이지 (monoDetailView_M01.jsp)에서 약재 데이터 수집
    """
    base_url = "https://oasis.kiom.re.kr/oasis/herb/monoDetailView_M01.jsp?idx="
    all_herbs = []

    for herb_id in range(start, end + 1):
        url = base_url + str(herb_id)
        print(f"[HERB] {url}")

        try:
            res = requests.get(url, timeout=10)
            if res.status_code != 200:
                print(f"⚠️ 접근 불가 ({res.status_code})")
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            # ✅ 제목 (약재명) — .cont_view 내부의 h2만 선택
            title_tag = soup.select_one(".cont_view h2")
            title = title_tag.get_text(strip=True) if title_tag else f"Unknown_{herb_id}"

            herb_data = {"id": herb_id, "name": title, "url": url}

            # ✅ 표(table) 안의 데이터 추출
            for table in soup.select(".cont_view table"):
                for tr in table.select("tr"):
                    ths = tr.find_all("th")
                    tds = tr.find_all("td")
                    for th, td in zip(ths, tds):
                        key = th.get_text(strip=True)
                        val = td.get_text(strip=True)
                        herb_data[key] = val

            # ✅ 본문 내 텍스트 블록 저장
            desc_blocks = soup.select(".cont_view, .view_con, .view_cont")
            if desc_blocks:
                herb_data["설명"] = " ".join([d.get_text(" ", strip=True) for d in desc_blocks])

            if len(herb_data) > 2:
                all_herbs.append(herb_data)
                print("✅ 수집:", title)
            else:
                print("⚠️ 데이터 없음:", title)

            time.sleep(0.2)

        except Exception as e:
            print("❌ Error:", e)

    os.makedirs("../raw", exist_ok=True)
    with open("../raw/oasis_herbs_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_herbs, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_herbs)} herb entries")
    return all_herbs


# ===============================
# 💊 처방 데이터 수집 (Prescription)
# ===============================
def scrape_prescriptions(start=1, end=30):
    """
    OASIS 처방 상세 페이지 (view01~view03)를 순회하며
    처방명 / 구성 / 효능 및 주치 데이터를 구조적으로 수집
    """
    base_url = "https://oasis.kiom.re.kr/oasis/pres/prdetailView.jsp"
    all_pres = []

    for idx in range(start, end + 1):
        print(f"\n[PRES] idx={idx}")
        pres_data = {"id": idx, "url": f"{base_url}?idx={idx}"}

        try:
            # -----------------------------
            # 🔹 view01 : 처방명 (기본정보)
            # -----------------------------
            url1 = f"{base_url}?idx={idx}#view01"
            res1 = requests.get(url1, timeout=10)
            if res1.status_code == 200:
                soup1 = BeautifulSoup(res1.text, "html.parser")

                # ✅ 제목: .cont_view 내부의 h2만 선택
                title_tag = soup1.select_one(".cont_view h2")
                if title_tag:
                    title_text = title_tag.get_text(" ", strip=True)
                    pres_data["처방명"] = title_text.split(",")[0].strip()
                else:
                    print("⚠️ 제목 태그 없음")

                # ✅ 표 파싱 (본문 내부)
                for tr in soup1.select(".cont_view table tr"):
                    ths = tr.find_all("th")
                    tds = tr.find_all("td")
                    for th, td in zip(ths, tds):
                        key = th.get_text(strip=True)
                        val = td.get_text(strip=True)
                        if key and val:
                            pres_data[key] = val

            # -----------------------------
            # 🔹 view02 : 구성 (시대별 구성 포함)
            # -----------------------------
            url2 = f"{base_url}?idx={idx}#view02"
            res2 = requests.get(url2, timeout=10)
            if res2.status_code == 200:
                soup2 = BeautifulSoup(res2.text, "html.parser")
                composition_texts = []
                for block in soup2.select(".cont_view, .view_con, .view_cont"):
                    composition_texts.append(block.get_text(" ", strip=True))
                if composition_texts:
                    pres_data["구성"] = " ".join(composition_texts)

            # -----------------------------
            # 🔹 view03 : 효능 및 주치
            # -----------------------------
            url3 = f"{base_url}?idx={idx}#view03"
            res3 = requests.get(url3, timeout=10)
            if res3.status_code == 200:
                soup3 = BeautifulSoup(res3.text, "html.parser")

                efficacy = {}
                for tr in soup3.select(".cont_view table tr"):
                    tds = tr.find_all("td")
                    ths = tr.find_all("th")
                    for th, td in zip(ths, tds):
                        key = th.get_text(strip=True)
                        val = td.get_text(strip=True)
                        if key and val:
                            efficacy[key] = val

                if efficacy:
                    pres_data["효능 및 주치"] = efficacy

                extra_blocks = soup3.select(".cont_view, .view_con, .view_cont")
                texts = [b.get_text(" ", strip=True) for b in extra_blocks]
                if texts:
                    pres_data["효능설명"] = " ".join(texts)

            # -----------------------------
            # ✅ 저장 조건
            # -----------------------------
            if "처방명" in pres_data and pres_data["처방명"] != "주 메뉴":
                all_pres.append(pres_data)
                print(f"✅ 수집: {pres_data['처방명']}")
            else:
                print("⚠️ 처방명 없음 또는 무효, skip")

            time.sleep(0.3)

        except Exception as e:
            print("❌ Error:", e)

    os.makedirs("../raw", exist_ok=True)
    with open("../raw/oasis_pres_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_pres, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(all_pres)} prescription entries")
    return all_pres


# ===============================
# 🚀 메인 실행
# ===============================
if __name__ == "__main__":
    print("🩺 OASIS Data Scraper Starting...")

    herbs = scrape_herbs(start=1, end=30)
    pres = scrape_prescriptions(start=1, end=30)

    print("✅ All done!")
