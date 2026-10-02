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
        return_data = json.load(f)
else:
    print("region_analysis_2023.json 파일이 없습니다.")


# JSON 데이터를 데이터프레임으로 변환
data = pd.DataFrame(return_data)


# 반납률이 높은 지역부터 정렬
data = data.sort_values("반납률", ascending=False)


# 그래프 크기 설정
plt.figure(figsize=(12, 6))


# 지역별 면허 자진반납률 막대그래프
plt.bar(data["지역"], data["반납률"])


# 그래프 제목과 축 이름
plt.title("2023년 지역별 고령운전자 면허 자진반납률")
plt.xlabel("지역")
plt.ylabel("자진반납률 (%)")


# 지역 이름이 겹치지 않도록 45도 회전
plt.xticks(rotation=45)

# 그래프 요소가 잘리지 않도록 정리
plt.tight_layout()


# 그래프 저장
Path("output").mkdir(exist_ok=True)
plt.savefig("output/04_license_return_rate.png", dpi=300)
