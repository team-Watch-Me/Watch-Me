import pandas as pd  # pandas를 import
import os
import json  # json을 import
import search_from_tmdb  # search_from_tmdb.py 모듈을 import
from search_from_tmdb import get_tmdb_id
from search_from_tmdb import get_movie_details

# JSON 파일 경로
file_path = 'data/result 10000.json'

# JSON 파일 읽기
with open(file_path, 'r') as file:
    md_dict = json.load(file)

# DataFrame으로 변환
md = pd.DataFrame(md_dict)

# 행 열 뒤집기
md = md.T

idx = 1
for row in md.itertuples():
    if hasattr(row, 'tmdb_id') and pd.notna(row.tmdb_id):
        continue
    tmdb_id = get_tmdb_id(row)
    if tmdb_id is None:
        continue
    md.loc[row.Index, 'tmdb_id'] = tmdb_id
    print(f"{idx}) {row.content_name}'s tmdb_id: {tmdb_id}")
    idx = idx + 1



# tmdb_id가 NaN인 행 제거
md = md.dropna(subset=['tmdb_id'])

# tmdb_id를 int로 변환
md['tmdb_id'] = md['tmdb_id'].astype(int)

# 'titleId' 열이 존재하는 경우에만 제거
if 'titleId' in md.columns:
    md.drop(columns=['titleId'], inplace=True)

# 열 이름 변경
md.rename(columns={
    'content_name': 'name_kr',
    'english_name': 'name_eng'
}, inplace=True)

# poster image랑 release-date 추가
for row in md.itertuples():
    movie_details = get_movie_details(row.tmdb_id)

    md.loc[row.Index, 'poster_img'] = "https://image.tmdb.org/t/p/w500" + movie_details.get('poster_path')[0]
    md.loc[row.Index, 'release_date'] = movie_details.get('release_date')[0]



# 원하는 열 순서
column_order = ['tmdb_id', 'name_kr', 'name_eng', 'plot', 'genre', 'age_rating', 'year', 'running_time', 'streaming_provider', 'country', 'staff', 'actor', 'poster_img', 'release_date']

# 열 순서대로 데이터프레임 재배열
md = md[column_order]



# output 폴더가 없으면 생성
output_dir = 'output_with_tmdb'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 'index' 컬럼을 JSON의 키로 사용하고, 'index' 컬럼을 제거
json_data = {
    row['tmdb_id']: row.to_dict()  # 'tmdb_id' 값을 키로 사용
    for _, row in md.iterrows()
}

# JSON 파일을 output 폴더에 저장
file_name = os.path.basename(file_path)

output_file = os.path.join(output_dir, file_name)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)
