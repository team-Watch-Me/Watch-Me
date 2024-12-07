import pandas as pd  # pandas를 import
import os
import json  # json을 import
import search_from_tmdb
from search_from_tmdb import get_tmdb_id
from search_from_tmdb import get_movie_details

# JSON 파일 경로
file_num = 1
file_paths = ['data/result_100000_to_140000.json']

for file_path in file_paths:
    # JSON 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as file:
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
        print(f"{file_num} - {idx}) {row.titleKr}'s tmdb_id: {tmdb_id}")
        idx = idx + 1

    # tmdb_id가 NaN인 행 제거
    md = md.dropna(subset=['tmdb_id'])

    # tmdb_id를 int로 변환
    md['tmdb_id'] = md['tmdb_id'].astype(int)

    """
    tmdb에서 갖고 오는 내용
    1. poster image
    2. release date
    3. vote count
    4. vote average
    5. popularity
    """
    for row in md.itertuples():
        movie_details = get_movie_details(row.tmdb_id)

        # 포스터 이미지
        poster_path = movie_details.get('poster_path')[0]
        if poster_path is not None:
            md.loc[row.Index, 'tmdb_poster_img'] = "https://image.tmdb.org/t/p/original" + poster_path

        # release_date
        release_date = movie_details.get('release_date')[0]
        if release_date is not None:
            md.loc[row.Index, 'tmdb_release_date'] = release_date

        # vote_count
        vote_count = movie_details.get('vote_count')[0]
        if vote_count is not None:
            md.loc[row.Index, 'vote_count'] = vote_count

        # vote_avearge
        vote_average = movie_details.get('vote_average')[0]
        if vote_average is not None:
            md.loc[row.Index, 'vote_average'] = vote_average

        # popularity
        popularity = movie_details.get('popularity')[0]
        if popularity is not None:
            md.loc[row.Index, 'popularity'] = popularity

    # 키노 id의 속성 이름을 'id'에서 'kino_id'로 변경
    md.rename(columns={'id': 'kino_id'}, inplace=True)

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

    file_num = file_num + 1
