from pathlib import Path
import json
import pandas as pd


# 사용할 파일 경로
csv_path = Path("data/region_2023.csv")
json_path = Path("data/regional_license_return.json")


# 교통사고 CSV 파일 불러오기
if csv_path.exists():
    accident = pd.read_csv(csv_path)
else:
    print("region_2023.csv 파일이 없습니다.")


# 면허 자진반납 JSON 파일 불러오기
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        return_data = json.load(f)
else:
    print("regional_license_return.json 파일이 없습니다.")


# 필요한 데이터만 리스트에 저장
license_return = []

for region in return_data["regions"]:
    license_return.append({
        "지역": region["지역"],
        "면허소지자수": region["면허소지자수_명"],
        "반납자수": region["면허반납자수_명"],
        "반납률": region["반납률_원문_퍼센트"]
    })


# 리스트를 데이터프레임으로 변환
license_return = pd.DataFrame(license_return)


# 두 데이터의 지역 이름을 같게 만들기
region_names = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전라북도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주도"
}


# 지역 이름 변경
for i in range(len(license_return)):
    old_name = license_return.loc[i, "지역"]
    license_return.loc[i, "지역"] = region_names[old_name]


# 지역을 기준으로 두 데이터 합치기
data = pd.merge(accident, license_return, on="지역")


# 고령 면허소지자 1만 명당 사고건수 계산
data["1만명당_사고건수"] = (
    data["사고건수"] / data["면허소지자수"] * 10000
)


# 결과 확인
print(data)


# 데이터프레임을 리스트 형태로 변환
result = data.to_dict(orient="records")


# 결과를 JSON 파일로 저장
with open("data/region_analysis_2023.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
    