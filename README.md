# 🚗 SeniorDrive_Analysis

**고령운전자 교통사고, 숫자로 보면 정말 위험한가?**
SK쉴더스 35기 Python 팀 프로젝트 — 공공데이터 기반 고령운전자 교통사고 분석

---

## 📌 프로젝트 소개

최근 고령 운전자의 사고 수가 증가하고 있습니다.
이 프로젝트는 **공공데이터로** 직접 검증하여 고령 운전자의 면허 반납룰과 사고의 상관관계를 분석합니다.

- 단순히 사고 건수가 늘었는가, 아니면 고령 인구·면허 소지자가 늘어난 만큼만
  늘었는가?
- 지역별로 사고가 어디에 몰리는가?
- 면허를 자진반납하는 지역일수록 실제로 사고가 적은가?

한국도로교통공단 공공API, KOSIS, 경찰청 공공데이터를 MongoDB에 적재하고,
연도별·지역별로 교차 분석한 결과를 시각화로 정리했습니다.

## 🔑 핵심 인사이트

| 질문 | 결과 |
|---|---|
| 사고가 늘고 있나? | 2019→2023년 고령운전자사고 33,239건 → 39,614건 (+19.2%). 같은 기간 전체사고는 229,600건 → 198,296건 (-13.6%)**로 줄어 대조적 |
| 단순히 고령 인구가 늘어서인가? | 아니다. 65세 이상 면허비율은 10.22%→13.79% 늘었는데, 사고비중은 14.48%→19.98*로 더 가파르게 늚. 사고 위험도 지수(사고비중÷면허비중)가 5년 내내 **1.3~1.45**로, 비고령(약 0.93~0.95)보다 뚜렷하게 높음 |
| 어디에 몰려있나? | 2023년 기준 경기(9,170)·서울(6,864)·경북(2,754) 상위 3개 지역이 전체의 **48.1%** |
| 면허 자진반납이 사고를 줄이나? | 도심 반납률(2.7%)이 지방(1.8%)보다 높음 — 다만 **같은 해 기준의 지역별 상관 데이터일 뿐, 인과관계를 증명하진 않음** (아래 한계 참고) |

## 🗂 데이터 출처

| 데이터 | 출처 | 비고 |
|---|---|---|
| 지자체별 교통사고 통계 | 한국도로교통공단 lgStat API | 2019~2023, 시군구 230개 전수 수집 |
| 운전면허 소지자 현황 | KOSIS (연령대별, 2019~2023) | 2020년 값이 경찰청 원본과 교차검증됨 |
| 고령운전자 법규위반·시간대별 사고 | 한국도로교통공단 통계 | |
| 고령운전자 면허 자진반납 현황 | 2023회계연도 결산 위원회별 분석(행정안전위원회), 자료: 경찰청 | 전국 합계가 KOSIS 65세 이상 면허소지자수(4,747,426명)와 일치 확인 |
| 시도 경계 지도 | ctprvn.geojson | 지역별 히트맵용 |

상세한 검증 방법과 상태는 [`data/source_log.md`](data/source_log.md)에 전부
기록되어 있습니다.

## 📁 프로젝트 구조

```
SeniorDrive_Analysis/
├── data/
│   ├── raw/              # API·CSV 원본 (수정 안 함)
│   ├── processed/        # 연도별/지역별/면허비율 등 집계본
│   ├── regional_license_return.json   # 지역별 면허 자진반납 현황
│   ├── region_analysis_2023.json      # 사고+반납률 병합 결과
│   └── source_log.md     # 데이터 출처·검증 기록
│
├── src/
│   ├── data_processed/   # 수집 → 전처리 → MongoDB 적재
│   │   ├── 1_data_collect.py
│   │   ├── 2_accident_lgstat.py
│   │   ├── 3_license.py
│   │   ├── 4_analyze.py
│   │   └── build_mongo.py
│   └── visualize/        # 시각화
│       ├── merge_data.py           # 사고+반납률 데이터 병합
│       ├── 03_accident_heatmap.py  # 지역별 사고 히트맵(지도)
│       ├── 04_license_return.py    # 지역별 반납률 막대그래프
│       ├── 05_accident_map.py      # 반납률×사고율 비교
│       ├── src/
│       │   ├── visualize_1.py      # 연도별 추세·위험도 지수
│       │   └── matplotlib2.py      # 면허비율 vs 사고비율 격차
│       └── output/                 # 위 스크립트들의 결과 이미지
│
├── output/                # 지도·반납률 관련 결과 이미지
├── db/
├── requirements.txt
└── .env                   # MongoDB 연결정보, API 키 (git 제외)
```

## ▶️ 실행 방법

```bash
pip install -r requirements.txt
```

**1. 데이터 수집 → DB 적재**
```bash
cd src/data_processed
python 1_data_collect.py      # lgStat API 수집 (시군구 230개 × 5개년)
python 2_accident_lgstat.py   # 연도별/지역별 집계
python 3_license.py           # KOSIS 면허비율 집계
python build_mongo.py         # MongoDB 적재
python 4_analyze.py           # 분석 결과 생성 (analysis_result.json)
```

**2. 시각화**
```bash
cd ../visualize
python merge_data.py              # 사고+반납률 데이터 병합
python 03_accident_heatmap.py     # 지역별 히트맵
python 04_license_return.py       # 반납률 막대그래프
python 05_accident_map.py         # 반납률×사고율 비교
python src/visualize_1.py         # 연도별 추세·위험도 지수
python src/matplotlib2.py         # 면허비율 vs 사고비율 격차
```

MongoDB 연결 정보와 API 키는 `.env`에 둡니다(저장소에는 포함되지 않음).

## 📊 시각화 결과

**연도별 추세 & 위험도 지수** (`src/visualize/output/`)
- `1_elderly_accident_trend.png` — 고령운전자 교통사고 발생 건수 추이
- `2_elderly_accident_ratio.png` — 전체 사고 중 고령운전자 사고 비중 추이
- `3_risk_index_comparison.png` — 고령 vs 비고령 사고 위험도 지수 비교

**지역 분석** (`output/`)
- `03_accident_heatmap.png` — 2023년 지역별 고령운전자 사고 수준 (지도)
- `04_license_return_rate.png` — 2023년 지역별 면허 자진반납률
- `05_license_return_accident.png` — 반납률과 사고 수준 비교

## ⚠️ 한계 및 주의사항

- **면허 자진반납 데이터는 사고 데이터와 출처·집계 기준이 다릅니다.** 반납률이
  높은 지역일수록 사고가 적게 나타나는 경향이 있지만, 이는 상관관계이며
  정책의 인과효과를 증명하지 않습니다.
- 반납 데이터 원문에서 전국 합계(4,747,426명)와 지역별 합계(4,693,426명) 사이
  약 54,000명 차이가 있는데, 원문 수치를 그대로 보존했습니다.
- 대구 군위군은 2023.7.1 경북→대구 편입으로 2019~2022년 데이터가 코드상
  존재하지 않는 게 정상입니다.

자세한 내용은 `data/regional_license_return.json`의 `metadata` 필드와
`data/source_log.md`를 참고하세요.
