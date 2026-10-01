# 데이터 출처 로그

| 파일 | 출처 | 검증 방법 | 상태 |
|---|---|---|---|
| processed/yearly_trend.csv | lgStat API (시군구 230개 전수) | 재생성값이 뉴스기사(TAAS 기준: 2019년 229,600건 / 2023년 고령운전자 39,614건)와 일치 | ✅ 검증됨 |
| processed/region_2023.csv | lgStat API | 17개 지역 합계(39,614)가 yearly_trend 2023값과 정확히 일치. 기존 버전에 경상남도가 누락되어 있던 것을 발견, 수정함 | ✅ 검증됨 |
| processed/license_ratio.csv | KOSIS 운전면허소지자현황(연령대별, 2019~2023) | 2020년 값(11.1%)이 경찰청 단일연도 CSV로 직접 재계산한 값과 정확히 일치 | ✅ 검증됨 |
| processed/time_comparison.csv | 한국도로교통공단_가해운전자 연령층별 시간대별 교통사고 통계 | 팀원 확인 | ✅ 검증됨 |
| raw/license_holders_2020.csv | 경찰청 CSV | KOSIS 값과 교차검증용으로 보관 (더 이상 단독 출처로 사용 안 함) | 보관용 |

## 처리 완료
- [x] time_comparison 출처 확인 → 한국도로교통공단_가해운전자 연령층별 시간대별 교통사고 통계로 확인, processed/로 이동
- [x] license_ratio 2022년 e-나라지표 추정값 → KOSIS 5개년(2019~2023) 원자료로 교체, 전부 직접 계산
- [x] yearly_trend / region_2023 실제 API 수집 완료, 기존 팀원 추정치와 대조 → 경상남도 누락 발견 후 수정

## 다음 확인 사항
- [ ] 시간대별 데이터(time_comparison)의 구체적 출처 URL 또는 데이터셋 ID 기록 (현재는 데이터셋명만 있음)
- [ ] 1_data_collect.py 전체 수집(230개 시군구 × 5개년) 완주 여부 최종 확인 — 군위군 관련 FAIL은 정상(2023.7.1 경북→대구 편입)이므로 무시 가능
