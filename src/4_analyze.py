"""
MongoDB에서 꺼내서 지금까지 세운 스토리에 맞게 계산.
1) 연도별 추세  2) 면허비율 vs 사고비율 격차  3) 고령운전자 vs 고령보행자 / 치사율
4) 지역 TOP5  5) 주/야간 비교
결과를 data/processed/analysis_result.json으로 저장 (4단계 시각화에서 바로 씀).
"""

import json
from pathlib import Path
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/Traffic"
DB_NAME = "elderly_traffic_db"
OUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "analysis_result.json"


def main():
    db = MongoClient(MONGO_URI)[DB_NAME]
    summary = db["elderly_accident_summary"]
    raw = db["lgstat_raw"]
    result = {}

    # 1) 연도별 추세
    yearly = list(summary.find({"metric": "yearly_trend"}, {"_id": 0}).sort("연도", 1))
    result["연도별_추세"] = yearly

    # 2) 면허비율 vs 사고비율 격차 (같은 연도끼리 짝지어서 계산)
    license_ratio = {r["연도"]: float(r["65세이상_면허비율(%)"]) for r in
                      summary.find({"metric": "license_ratio"})}
    gap = []
    for y in yearly:
        year = y["연도"]
        if year in license_ratio:
            share = float(y["전체대비_고령운전자사고_비중(%)"])
            gap.append({
                "연도": year,
                "사고비중(%)": share,
                "면허비중(%)": license_ratio[year],
                "격차(%p)": round(share - license_ratio[year], 2),
            })
    result["면허비율_대비_사고비율_격차"] = gap

    # 3) 고령운전자 vs 고령보행자 (전국 합계, 연도별) + 전체사고 대비 치사율 비교
    pipeline = [
        {"$match": {"acc_cl_nm": {"$in": ["고령운전자사고", "고령보행자사고", "전체사고"]}}},
        {"$group": {
            "_id": {"year": "$std_year", "cls": "$acc_cl_nm"},
            "acc_cnt": {"$sum": {"$toInt": "$acc_cnt"}},
            "dth_cnt": {"$sum": {"$toInt": "$dth_dnv_cnt"}},
        }},
    ]
    rows = list(raw.aggregate(pipeline))
    by_class = {}
    for r in rows:
        year, cls = r["_id"]["year"], r["_id"]["cls"]
        by_class.setdefault(cls, {})[year] = {
            "사고건수": r["acc_cnt"],
            "치사율": round(r["dth_cnt"] / r["acc_cnt"] * 100, 2) if r["acc_cnt"] else 0,
        }
    result["가해자_vs_보행자_연도별"] = by_class

    # 4) 2023 지역 TOP5
    top5 = list(summary.find({"metric": "region_2023"}, {"_id": 0})
                .sort("사고건수", -1).limit(5))
    result["2023_지역_TOP5"] = top5

    # 5) 주/야간 비교 (이미 processed에 있는 값)
    time_cmp = list(summary.find({"metric": "time_comparison"}, {"_id": 0}))
    result["시간대별_비교"] = time_cmp

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장 완료 → {OUT_PATH}")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:1000], "...")


if __name__ == "__main__":
    main()
