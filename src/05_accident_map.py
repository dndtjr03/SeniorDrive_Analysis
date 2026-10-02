from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt


# 그래프 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# JSON 파일 경로
json_path = Path("data/region_analysis_2023.json")


# JSON 파일 불러오기
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        accident_data = json.load(f)
else:
    print("region_analysis_2023.json 파일이 없습니다.")


# JSON 데이터를 데이터프레임으로 변환
data = pd.DataFrame(accident_data)


# 반납률이 높은 지역부터 정렬
data = data.sort_values("반납률", ascending=False)


# 지역 개수만큼 숫자 만들기
x = range(len(data))


# 두 막대가 겹치지 않도록 위치 만들기
left_x = []
right_x = []

for i in x:
    left_x.append(i - 0.2)
    right_x.append(i + 0.2)


# 그래프와 왼쪽 Y축 만들기
fig, ax1 = plt.subplots(figsize=(13, 6))

# 오른쪽 Y축 추가
ax2 = ax1.twinx()


# 면허 자진반납률 막대그래프
ax1.bar(
    left_x,
    data["반납률"],
    width=0.4,
    label="면허 자진반납률"
)


# 1만 명당 사고건수 막대그래프
ax2.bar(
    right_x,
    data["1만명당_사고건수"],
    width=0.4,
    label="1만 명당 사고건수",
    alpha=0.6
)


# 그래프 제목과 축 이름
plt.title("2023년 지역별 면허 자진반납률과 고령운전자 사고 수준 비교")

ax1.set_xlabel("지역")
ax1.set_ylabel("면허 자진반납률 (%)")
ax2.set_ylabel("고령 면허소지자 1만 명당 사고건수")


# X축에 지역 이름 표시
ax1.set_xticks(list(x))
ax1.set_xticklabels(data["지역"], rotation=45)


# 범례 표시
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")


plt.tight_layout()


# 그래프 저장
Path("output").mkdir(exist_ok=True)
plt.savefig("output/05_license_return_accident.png", dpi=300)
