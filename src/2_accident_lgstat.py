"""
data/raw/lgstat_raw.json → data/processed/{yearly_trend, region_2023}.csv

이미 검증된 두 산출물(연도별 추이, 지역별 2023)을 lgStat 원본에서
직접 재생성합니다. 업로드해주신 csv.zip의 값과 대조해서 일치하는지
확인하는 용도로도 쓰세요.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "lgstat_raw.json"
OUT_DIR = Path(__file__).parent.parent / "data" / "processed"


def load_raw() -> list[dict]:
    return json.loads(RAW_PATH.read_text(encoding="utf-8"))


def build_yearly_trend(items: list[dict]):
    """연도별: 고령운전자사고 건수/사망자, 전체사고 건수, 비중, 치사율"""
    by_year = defaultdict(lambda: {"elderly_acc": 0, "elderly_dth": 0, "total_acc": 0})

    for it in items:
        year = int(it["std_year"])
        if it["acc_cl_nm"] == "고령운전자사고":
            by_year[year]["elderly_acc"] += int(it["acc_cnt"])
            by_year[year]["elderly_dth"] += int(it["dth_dnv_cnt"])
        elif it["acc_cl_nm"] == "전체사고":
            # tot_acc_cnt는 지역별로 반복되는 "전국 총계"이므로 합산하면 안 되고,
            # 지역 1건당 한 번만 반영되도록 acc_cnt(해당 지역 건수)를 더해야 함
            by_year[year]["total_acc"] += int(it["acc_cnt"])

    out_path = OUT_DIR / "yearly_trend_regenerated.csv"
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["연도", "고령운전자사고_건수", "고령운전자사고_사망자",
                     "전체사고_건수", "전체대비_고령운전자사고_비중(%)", "치사율"])
        for year in sorted(by_year):
            d = by_year[year]
            share = round(d["elderly_acc"] / d["total_acc"] * 100, 2) if d["total_acc"] else 0
            fatality = round(d["elderly_dth"] / d["elderly_acc"] * 100, 2) if d["elderly_acc"] else 0
            w.writerow([year, d["elderly_acc"], d["elderly_dth"], d["total_acc"], share, fatality])

    print(f"저장 완료 → {out_path}")


def build_region_summary(items: list[dict], target_year: int = 2023):
    """특정 연도의 지역별 고령운전자사고 건수"""
    by_region = defaultdict(int)

    for it in items:
        if int(it["std_year"]) == target_year and it["acc_cl_nm"] == "고령운전자사고":
            # sido_sgg_nm은 "서울특별시 강남구"처럼 시군구까지 나오므로,
            # 시도 단위로만 집계하려면 앞 단어만 잘라서 씀
            sido = it["sido_sgg_nm"].split()[0]
            by_region[sido] += int(it["acc_cnt"])

    out_path = OUT_DIR / f"region_{target_year}_regenerated.csv"
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["지역", "사고건수"])
        for region, cnt in sorted(by_region.items(), key=lambda x: -x[1]):
            w.writerow([region, cnt])

    print(f"저장 완료 → {out_path}")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = load_raw()
    build_yearly_trend(items)
    build_region_summary(items, target_year=2023)
