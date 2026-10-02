"""
data/processed/*.csv → MongoDB

컬렉션 3개로 분리 (README.md 2번 참고):
  - lgstat_raw               : API 원본 (raw json 그대로)
  - license_holders          : KOSIS 운전면허소지자현황 원본 (2019~2023)
  - elderly_accident_summary : 분석용 집계 (yearly_trend / region / license_ratio)

전부 upsert 방식이라 여러 번 실행해도 중복 안 생깁니다.
"""

import json
import csv
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# 환경변수 불러오기
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGO_URI = "mongodb://localhost:27017/Traffic"  # Atlas 쓰면 여기 연결 문자열 교체
DB_NAME = "elderly_traffic_db"

DATA_DIR = Path(__file__).parent.parent / "data"


def load_lgstat_raw(db):
    raw_path = DATA_DIR / "raw" / "lgstat_raw.json"
    if not raw_path.exists():
        print(f"[SKIP] {raw_path} 없음")
        return

    items = json.loads(raw_path.read_text(encoding="utf-8"))
    col = db["lgstat_raw"]
    for it in items:
        year = it["std_year"]
        # sido_sgg_nm 예: "서울특별시 강남구" -> 코드가 없으면 이름 그대로 키에 사용
        region_key = it["sido_sgg_nm"].replace(" ", "_")
        cls = it["acc_cl_nm"]
        doc_id = f"{year}_{region_key}_{cls}"

        col.update_one({"_id": doc_id}, {"$set": {**it, "_id": doc_id}}, upsert=True)

    print(f"lgstat_raw: {len(items)}건 upsert 완료")


def load_license_holders(db):
    """KOSIS 운전면허소지자현황(연령대별, 2019~2023) → 연령 x 연도별 문서.
    기존 경찰청 단일연도(2020) CSV는 이 파일에 포함되는 값과 정확히 일치함을 확인해 대체했습니다.
    """
    raw_path = DATA_DIR / "raw" / "운전면허소지자현황_연령대별_2019_2023.csv"
    if not raw_path.exists():
        print(f"[SKIP] {raw_path} 없음")
        return

    years = [2019, 2020, 2021, 2022, 2023]
    cols_per_year = 12

    with raw_path.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))
    data_rows = rows[4:]  # 0~2행 헤더, 3행 "계"(전국합계), 4행부터 연령별

    col = db["license_holders"]
    count = 0
    for row in data_rows:
        label = row[0].strip('"')
        if "세" not in label:
            continue
        age = 99 if "이상" in label else int(label.replace("세", ""))

        for i, year in enumerate(years):
            base = 1 + i * cols_per_year

            def val(offset):
                v = row[base + offset]
                return 0 if v in ("-", "") else int(v)

            doc = {
                "_id": f"{year}_{age}",
                "std_year": year,
                "age": age,
                "total": val(0),
                "license_1jong_subtotal": val(1),
                "license_1jong_large": val(2),
                "license_1jong_normal": val(3),
                "license_1jong_small": val(4),
                "license_1jong_trailer_large": val(5),
                "license_1jong_trailer_small": val(6),
                "license_1jong_rescue": val(7),
                "license_2jong_subtotal": val(8),
                "license_2jong_normal": val(9),
                "license_2jong_small": val(10),
                "license_moped": val(11),
            }
            col.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
            count += 1

    print(f"license_holders: {count}건 upsert 완료 (KOSIS 2019~2023)")


def load_summary_csv(db, filename: str, metric: str, id_prefix: str, key_field: str):
    """processed/*.csv 공통 로더. key_field 컬럼값을 _id의 일부로 사용."""
    path = DATA_DIR / "processed" / filename
    if not path.exists():
        print(f"[SKIP] {path} 없음 (아직 출처 미확인이면 정상)")
        return

    col = db["elderly_accident_summary"]
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            key_val = str(row[key_field]).replace(" ", "_")
            doc_id = f"{id_prefix}_{key_val}"
            doc = {"_id": doc_id, "metric": metric, **row}
            col.update_one({"_id": doc_id}, {"$set": doc}, upsert=True)
            count += 1
    print(f"elderly_accident_summary [{metric}]: {count}건 upsert 완료")


if __name__ == "__main__":
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    load_lgstat_raw(db)
    load_license_holders(db)

    # 검증된 것만 우선 적재. time_comparison은 출처 확인 후 같은 패턴으로 추가.
    load_summary_csv(db, "yearly_trend.csv", metric="yearly_trend",
                      id_prefix="yearly", key_field="연도")
    load_summary_csv(db, "region_2023.csv", metric="region_2023",
                      id_prefix="region_2023", key_field="지역")
    load_summary_csv(db, "license_ratio.csv", metric="license_ratio",
                      id_prefix="license_ratio", key_field="연도")
    load_summary_csv(db, "time_comparison.csv", metric="time_comparison",
                      id_prefix="time_comparison", key_field="시간대")

    print("\n전체 적재 완료.")
