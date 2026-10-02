from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


# 그래프 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# 사용할 파일 경로
json_path = Path("data/region_analysis_2023.json")
map_path = Path("data/ctprvn.geojson")


# JSON 파일 불러오기
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        accident_data = json.load(f)
else:
    print("region_analysis_2023.json 파일이 없습니다.")


# JSON 데이터를 데이터프레임으로 변환
data = pd.DataFrame(accident_data)


# 대한민국 지도 데이터 불러오기
if map_path.exists():
    korea = gpd.read_file(map_path)
else:
    print("지도 파일이 없습니다.")


# 지도와 JSON에서 다른 지역 이름 맞추기
korea["CTP_KOR_NM"] = korea["CTP_KOR_NM"].replace({
    "강원특별자치도": "강원도",
    "전북특별자치도": "전라북도"
})


# 지역 이름을 기준으로 지도와 사고 데이터 합치기
korea = pd.merge(
    korea,
    data,
    left_on="CTP_KOR_NM",
    right_on="지역"
)


# 1만 명당 사고건수를 기준으로 지역별 색상 표시
korea.plot(
    column="1만명당_사고건수",
    cmap="YlOrRd",
    edgecolor="black",
    legend=True
)


# 그래프 제목 설정
plt.title("2023년 지역별 고령운전자 사고 수준")

# 지도이므로 x축, y축 숨기기
plt.axis("off")
plt.tight_layout()


# 그래프 저장
Path("output").mkdir(exist_ok=True)
plt.savefig("output/03_accident_heatmap.png", dpi=300)
