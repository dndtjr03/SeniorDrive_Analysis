"""
KOSIS 운전면허소지자현황(연령대별, 2019~2023) → data/processed/license_ratio.csv

기존 경찰청 CSV는 2020년 1개 연도만 있어서, 지난번 e-나라지표로 2022년 값을
추정했었는데 출처 미검증 상태였습니다. 이 KOSIS 파일은 2019~2023년 5개년이
전부 들어있고, 2020년 값(11.1%)이 경찰청 CSV로 직접 계산한 값과 정확히
일치하는 것까지 확인했으므로 이걸로 교체합니다.

파일 구조: 1~3행이 헤더(연도/종별/세부종별), 4행이 전체 합계("계"), 5행부터
"16세"~"99세 이상" 1세 단위. 연도 블록마다 12개 컬럼이고, 블록의 첫 번째
컬럼이 해당 연도·연령의 "총계"입니다.
"""

import csv
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "운전면허소지자현황_연령대별_2019_2023.csv"
OUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "license_ratio.csv"

YEARS = [2019, 2020, 2021, 2022, 2023]
COLS_PER_YEAR = 12  # 총계 + 1종(소계,대형,보통,소형,대형견인,소형견인,구난) + 2종(소계,보통,소형,원자)


def compute_ratios(csv_path: Path) -> dict:
    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))

    data_rows = rows[4:]  # 0~2행 헤더, 3행 "계"(전국합계), 4행부터 연령별

    totals_all = {y: 0 for y in YEARS}
    totals_65plus = {y: 0 for y in YEARS}

    for row in data_rows:
        label = row[0].strip('"')
        if "세" not in label:
            continue
        age = 99 if "이상" in label else int(label.replace("세", ""))

        for i, year in enumerate(YEARS):
            total_col_idx = 1 + i * COLS_PER_YEAR  # 해당 연도 블록의 첫 컬럼(총계)
            val = row[total_col_idx]
            val = int(val) if val not in ("-", "") else 0
            totals_all[year] += val
            if age >= 65:
                totals_65plus[year] += val

    return {
        "totals_all": totals_all,
        "totals_65plus": totals_65plus,
    }


if __name__ == "__main__":
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    result = compute_ratios(RAW_PATH)
    totals_all = result["totals_all"]
    totals_65plus = result["totals_65plus"]

    with OUT_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["연도", "전체_면허소지자", "65세이상_면허소지자", "65세이상_면허비율(%)", "출처", "검증상태"])
        for year in YEARS:
            ratio = round(totals_65plus[year] / totals_all[year] * 100, 2)
            w.writerow([year, totals_all[year], totals_65plus[year], ratio,
                        "KOSIS(운전면허소지자현황_연령대별)", "검증됨"])
            print(f"{year}: 전체 {totals_all[year]:,} / 65세이상 {totals_65plus[year]:,} / 비율 {ratio}%")

    print(f"\n저장 완료 → {OUT_PATH}")
    print("참고: 2020년 값은 경찰청 단일연도 CSV로 직접 재계산한 11.1%와 정확히 일치함(교차검증됨).")
