import json
from pathlib import Path
import matplotlib.pyplot as plt

# ==========================
# 1. 파일 경로 설정 및 준비
# ==========================

# 프로젝트 최상위 경로 (SeniorDrive_Analysis)
# 현재 위치: SeniorDrive_Analysis/visualize/src/visualize_1.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# JSON 파일 경로 및 시각화 결과물(이미지) 저장 폴더 경로 설정
JSON_PATH = BASE_DIR / 'data' / 'processed' / 'analysis_result.json'
OUTPUT_DIR = BASE_DIR / 'visualize' / 'output'

# 결과물을 저장할 output 폴더가 없다면 새로 생성합니다.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================
# 2. JSON 파일 불러오기
# ==========================

# 전처리 완료된 분석 결과 JSON 파일을 불러옵니다.
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


# =========================
# 3. 데이터 추출 (연도별 추세)
# =========================

trend_data = data['연도별_추세']

# 리스트 내포(List Comprehension)를 사용하여 x축, y축 데이터 분리
years = [int(row["연도"]) for row in trend_data]
accident_num = [int(row["고령운전자사고_건수"]) for row in trend_data]
accident_ratio = [float(row["전체대비_고령운전자사고_비중(%)"]) for row in trend_data]


# =========================
# 4. 고령 vs 비고령 사고 위험도 지수 비교
# =========================

gap_data = data['면허비율_대비_사고비율_격차']

elderly_risk_index = []
non_elderly_risk_index = []

for row in gap_data:
    acc_ratio = float(row["사고비중(%)"])
    lic_ratio = float(row["면허비중(%)"])
    
    # 고령운전자 위험도
    elderly_risk_index.append(acc_ratio / lic_ratio)
    
    # 비고령운전자 위험도
    non_e_risk = (100.0 - acc_ratio) / (100.0 - lic_ratio)
    non_elderly_risk_index.append(non_e_risk)


# =========================
# 5. 시각화 기본 설정 (폰트 및 그래프 옵션)
# =========================

# Matplotlib 한글 폰트 및 마이너스 깨짐 방지 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# =========================
# 6. 시각화
# =========================

# =========================
# [그래프 1] 고령운전자 교통사고 발생 건수 추이
# =========================
plt.figure(figsize=(8, 5))

plt.plot(years, accident_num, marker="o")

for x, y in zip(years, accident_num):
    plt.text(x, y + 500, f"{y:,}", ha="center")

plt.title("고령운전자 교통사고 발생 건수 추이")
plt.xlabel("연도")
plt.ylabel("사고 건수")
plt.xticks(years)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

# 이미지 파일로 저장
save_path_1 = OUTPUT_DIR / "1_elderly_accident_trend.png"
plt.savefig(save_path_1, dpi=300, bbox_inches='tight')
print(f"저장 완료: {save_path_1}")

plt.show() # 화면에 출력


# =========================
# [그래프 2] 전체 교통사고 중 고령운전자 사고 비중 추이
# =========================
plt.figure(figsize=(8, 5))

plt.plot(years, accident_ratio, marker="o")

for x, y in zip(years, accident_ratio):
    plt.text(x, y + 0.2, f"{y:.2f}%", ha="center")

plt.title("전체 교통사고 중 고령운전자 사고 비중 추이")
plt.xlabel("연도")
plt.ylabel("고령운전자 사고 비중 (%)")
plt.xticks(years)
plt.ylim(13, 21)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

# 이미지 파일로 저장
save_path_2 = OUTPUT_DIR / "2_elderly_accident_ratio.png"
plt.savefig(save_path_2, dpi=300, bbox_inches='tight')
print(f"저장 완료: {save_path_2}")

plt.show()


# =========================
# [그래프 3] 운전면허 비중 대비 사고 발생 위험도 지수 비교
# =========================
plt.figure(figsize=(9, 6))

plt.plot(years, non_elderly_risk_index, marker="s", color="cornflowerblue", linewidth=2, label="비고령운전자 위험도")
plt.plot(years, elderly_risk_index, marker="o", color="crimson", linewidth=2, label="고령운전자 위험도")

# 기준선(y=1.0)
plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7, label='평균 위험도 (1.0)')

for x, y in zip(years, non_elderly_risk_index):
    plt.text(x, y - 0.05, f"{y:.2f}", ha="center", color="blue")
    
for x, y in zip(years, elderly_risk_index):
    plt.text(x, y + 0.03, f"{y:.2f}", ha="center", color="darkred")

plt.title("운전면허 비중 대비 사고 발생 위험도 지수 비교", fontsize=14, pad=15)
plt.xlabel("연도", fontsize=12)
plt.ylabel("사고 위험도 지수 (사고비중 ÷ 면허비중)", fontsize=12)
plt.xticks(years)
plt.ylim(0.5, 1.8)
plt.legend(loc="center right")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

# 이미지 파일로 저장
save_path_3 = OUTPUT_DIR / "3_risk_index_comparison.png"
plt.savefig(save_path_3, dpi=300, bbox_inches='tight')
print(f"저장 완료: {save_path_3}")

plt.show()