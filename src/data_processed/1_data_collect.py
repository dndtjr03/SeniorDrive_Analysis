"""
lgStat API에서 연도 x 시군구를 루프 돌면서 수집.

실제 서버 동작 확인 결과 (문서와 다른 부분):
1. JSON 응답은 "response" 래퍼 없이 최상위에 resultCode/items가 바로 옵니다.
2. guGun을 생략하면(siDo만 보내면) INVALID_REQUEST_PARAMETER_ERROR가 납니다.
   문서는 "미입력 시 시도 전체"라고 되어 있지만 실제로는 구군 단위로
   하나씩 요청해야 합니다. 그래서 시도 단위가 아니라 구군 단위로 수집하고,
   시도 합계는 2_accident_lgstat.py에서 sido_sgg_nm 첫 단어로 묶어서 냅니다.
"""
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# 환경변수 경로 받아오기
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

CALL_BACK_URL = os.environ.get("CALL_BACK_URL")
SERVICEKEY = os.environ.get("SERVICEKEY")

if not CALL_BACK_URL or not SERVICEKEY:
    raise RuntimeError(
        f"환경변수를 못 읽었습니다. env_path={env_path} 존재여부={env_path.exists()} "
        f"CALL_BACK_URL={'있음' if CALL_BACK_URL else '없음'} "
        f"SERVICEKEY={'있음' if SERVICEKEY else '없음'}"
    )

# 기술문서 부록 "3.3 guGun 요청값" 표 기준.
# 날짜 제한이 있는 과거 코드(2010년/2010~14년 값만 존재 등)는 2019~2023 수집
# 범위와 안 맞아서 제외했습니다. 군위군은 2023.7.1 경북→대구 편입이라
# 둘 다 넣고, 실패하는 연도는 collect_all()에서 [FAIL]로 자동 건너뜁니다.
GU_GUN_CODES = {
    "서울특별시": {
        "강남구": 1116, "강동구": 1117, "강북구": 1124, "강서구": 1111,
        "관악구": 1115, "광진구": 1123, "구로구": 1112, "금천구": 1125,
        "노원구": 1122, "도봉구": 1107, "동대문구": 1105, "동작구": 1114,
        "마포구": 1110, "서대문구": 1109, "서초구": 1119, "성동구": 1104,
        "성북구": 1106, "송파구": 1118, "양천구": 1120, "영등포구": 1113,
        "용산구": 1103, "은평구": 1108, "종로구": 1101, "중구": 1102,
        "중랑구": 1121,
    },
    "부산광역시": {
        "강서구": 1212, "금정구": 1211, "기장군": 1216, "남구": 1207,
        "동구": 1203, "동래구": 1206, "북구": 1208, "사상구": 1215,
        "사하구": 1210, "서구": 1202, "수영구": 1214, "연제구": 1213,
        "영도구": 1204, "중구": 1201, "진구": 1205, "해운대구": 1209,
    },
    "대구광역시": {
        "남구": 2204, "달서구": 2207, "달성군": 2208, "동구": 2202,
        "북구": 2205, "서구": 2203, "수성구": 2206, "중구": 2201,
        "군위군": 2235,  # 2023.7.1 경북에서 편입
    },
    "인천광역시": {
        "강화군": 2309, "계양구": 2308, "미추홀구": 2303, "남동구": 2305,
        "동구": 2302, "부평구": 2304, "서구": 2306, "연수구": 2307,
        "옹진군": 2310, "중구": 2301,
    },
    "광주광역시": {
        "광산구": 2404, "남구": 2405, "동구": 2401, "북구": 2403, "서구": 2402,
    },
    "대전광역시": {
        "대덕구": 2505, "동구": 2501, "서구": 2503, "유성구": 2504, "중구": 2502,
    },
    "울산광역시": {
        "남구": 2602, "동구": 2603, "북구": 2604, "울주군": 2605, "중구": 2601,
    },
    "세종특별자치시": {
        "세종특별자치시": 2701,
    },
    "경기도": {
        "가평군": 1322, "고양시": 1318, "과천시": 1332, "광명시": 1309,
        "광주시": 1319, "구리시": 1310, "군포시": 1333, "김포시": 1327,
        "남양주시": 1334, "동두천시": 1330, "부천시": 1306, "성남시": 1303,
        "수원시": 1302, "시흥시": 1316, "안산시": 1307, "안성시": 1326,
        "안양시": 1305, "양주시": 1311, "양평군": 1323, "여주시": 1313,
        "연천군": 1320, "오산시": 1335, "용인시": 1325, "의왕시": 1336,
        "의정부시": 1304, "이천시": 1324, "파주시": 1317, "평택시": 1308,
        "포천시": 1321, "하남시": 1337, "화성시": 1315,
    },
    "강원특별자치도": {
        "강릉시": 1404, "고성군": 1422, "동해시": 1403, "삼척시": 1407,
        "속초시": 1405, "양구군": 1420, "양양군": 1423, "영월군": 1415,
        "원주시": 1402, "인제군": 1421, "정선군": 1417, "철원군": 1418,
        "춘천시": 1401, "태백시": 1406, "평창군": 1416, "홍천군": 1412,
        "화천군": 1419, "횡성군": 1413,
    },
    "충청북도": {
        "괴산군": 1516, "단양군": 1520, "보은군": 1512, "영동군": 1514,
        "옥천군": 1513, "음성군": 1517, "제천시": 1503, "증평군": 1521,
        "진천군": 1515, "청주시": 1501, "충주시": 1502,
    },
    "충청남도": {
        "계룡시": 1624, "공주시": 1605, "금산군": 1611, "논산시": 1615,
        "당진시": 1623, "보령시": 1604, "부여군": 1616, "서산시": 1606,
        "서천군": 1617, "아산시": 1603, "예산군": 1621, "천안시": 1602,
        "청양군": 1619, "태안군": 1612, "홍성군": 1620,
    },
    "전북특별자치도": {
        "고창군": 1719, "군산시": 1702, "김제시": 1706, "남원시": 1705,
        "무주군": 1713, "부안군": 1720, "순창군": 1717, "완주군": 1711,
        "익산시": 1723, "임실군": 1715, "장수군": 1714, "전주시": 1701,
        "정읍시": 1704, "진안군": 1712,
    },
    "전라남도": {
        "강진군": 1822, "고흥군": 1818, "곡성군": 1813, "광양시": 1808,
        "구례군": 1814, "나주시": 1806, "담양군": 1812, "목포시": 1802,
        "무안군": 1825, "보성군": 1819, "순천시": 1804, "신안군": 1832,
        "여수시": 1803, "영광군": 1828, "영암군": 1824, "완도군": 1830,
        "장성군": 1829, "장흥군": 1821, "진도군": 1831, "함평군": 1827,
        "해남군": 1823, "화순군": 1820,
    },
    "경상북도": {
        "경산시": 1935, "경주시": 1903, "고령군": 1923, "구미시": 1906,
        "김천시": 1904, "문경시": 1909, "봉화군": 1932, "상주시": 1910,
        "성주군": 1924, "안동시": 1905, "영덕군": 1917, "영양군": 1916,
        "영주시": 1907, "영천시": 1908, "예천군": 1930, "울릉군": 1934,
        "울진군": 1933, "의성군": 1913, "청도군": 1922, "청송군": 1915,
        "칠곡군": 1925, "포항시": 1902,
        # 군위군(구)은 2023.6월까지만 경북 소속(2023.7.1 대구로 편입)
        "군위군(구)": 1912,
    },
    "경상남도": {
        "거제시": 2010, "거창군": 2028, "고성군": 2022, "김해시": 2008,
        "남해군": 2024, "밀양시": 2009, "사천시": 2023, "산청군": 2026,
        "양산시": 2016, "의령군": 2012, "진주시": 2003, "창녕군": 2014,
        "창원시(통합)": 2030, "통영시": 2006, "하동군": 2025, "함안군": 2013,
        "함양군": 2027, "합천군": 2029,
    },
    "제주특별자치도": {
        "서귀포시": 2102, "제주시": 2101,
    },
}

YEARS = range(2019, 2024)  # 2019~2023

RAW_OUTPUT = Path(__file__).parent.parent / "data" / "raw" / "lgstat_raw.json"


def fetch_one(year: int, sido_code: int, gu_gun_code: int, num_of_rows: int = 20) -> list[dict]:
    """연도 x 시군구 하나에 대한 응답(13개 사고분류 항목)을 받아온다."""
    params = {
        "ServiceKey": SERVICEKEY,
        "searchYearCd": year,
        "siDo": sido_code,
        "guGun": gu_gun_code,
        "type": "json",
        "numOfRows": num_of_rows,
        "pageNo": 1,
    }
    resp = requests.get(CALL_BACK_URL, params=params, timeout=10)
    resp.raise_for_status()

    try:
        data = resp.json()
    except ValueError:
        raise RuntimeError(
            "API가 JSON이 아닌 응답을 돌려줬습니다.\n"
            f"  원본 응답(앞 500자): {resp.text[:500]}"
        )

    # 실제 응답은 "response" 래퍼 없이 최상위에 바로 옵니다. 혹시 모를 경우를
    # 대비해 중첩 구조도 같이 확인합니다.
    if "response" in data:
        header = data.get("response", {}).get("header", {})
        result_code = header.get("resultCode")
        msg = header.get("resultMsg")
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    else:
        result_code = data.get("resultCode")
        msg = data.get("resultMsg")
        items = data.get("items", {}).get("item", [])

    if result_code != "00":
        raise RuntimeError(f"API 오류 [{result_code}] {msg} (year={year}, sido={sido_code}, guGun={gu_gun_code})")

    if isinstance(items, dict):  # 결과가 1건이면 dict로 오는 경우 대비
        items = [items]
    return items


def collect_all() -> list[dict]:
    all_items = []
    total_calls = len(YEARS) * sum(len(v) for v in GU_GUN_CODES.values())
    done = 0
    for year in YEARS:
        for sido_name, gugun_map in GU_GUN_CODES.items():
            sido_code = None
            for gugun_name, gugun_code in gugun_map.items():
                # siDo 코드는 guGun 코드의 앞 2자리로 역산 가능하지만, 안전하게
                # SIDO_CODE_PREFIX에서 가져온다.
                sido_code = SIDO_CODE_BY_NAME[sido_name]
                done += 1
                try:
                    items = fetch_one(year, sido_code, gugun_code)
                    all_items.extend(items)
                    print(f"[OK {done}/{total_calls}] {year} {sido_name} {gugun_name}: {len(items)}건")
                except Exception as e:
                    print(f"[FAIL {done}/{total_calls}] {year} {sido_name} {gugun_name}: {e}")
                time.sleep(0.2)
    return all_items


SIDO_CODE_BY_NAME = {
    "서울특별시": 1100, "부산광역시": 1200, "대구광역시": 2200, "인천광역시": 2300,
    "광주광역시": 2400, "대전광역시": 2500, "울산광역시": 2600, "세종특별자치시": 2700,
    "경기도": 1300, "강원특별자치도": 1400, "충청북도": 1500, "충청남도": 1600,
    "전북특별자치도": 1700, "전라남도": 1800, "경상북도": 1900, "경상남도": 2000,
    "제주특별자치도": 2100,
}


if __name__ == "__main__":
    # 본 수집 전에 구군 단위 조합으로 1건만 먼저 확인
    print("=== 사전 테스트: 2023년 강남구(1116) ===")
    try:
        test_items = fetch_one(2023, 1100, 1116)
        print(f"[사전 테스트 성공] {len(test_items)}건 수신 → 본 수집을 시작합니다.\n")
    except Exception as e:
        print(f"[사전 테스트 실패] {e}")
        raise SystemExit(1)

    RAW_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    items = collect_all()
    RAW_OUTPUT.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n총 {len(items)}건 저장 완료 → {RAW_OUTPUT}")
