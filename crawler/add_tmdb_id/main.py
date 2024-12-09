import pandas as pd
import os
import json
import search_from_tmdb
from search_from_tmdb import get_tmdb_id, get_movie_details
import time  # 딜레이를 위해 추가

# JSON 파일 경로
file_paths = ['data/result_80000_to_100000.json']

# 최대 재시도 횟수 설정
MAX_RETRIES = 30

# 저장 경로 설정
output_dir = 'output_with_tmdb'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_num = 1
for file_path in file_paths:
    # 결과를 저장할 파일 이름
    file_name = os.path.basename(file_path).replace('.json', '_processed.json')
    output_file = os.path.join(output_dir, file_name)

    # 기존 데이터 로드 (파일이 있으면)
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            combined_data = json.load(f)
        # 기존 데이터로부터 DataFrame 생성
        combined_df = pd.DataFrame(combined_data)
        combined_df = combined_df.T
    else:
        combined_df = pd.DataFrame()



    # 이미 처리된 tmdb_id를 기록
    processed_tmdb_ids = set(combined_df['kino_id']) if 'kino_id' in combined_df else set()

    # JSON 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as file:
        md_dict = json.load(file)

    # DataFrame으로 변환
    md = pd.DataFrame(md_dict)

    # 행 열 뒤집기
    md = md.T

    md.rename(columns={'id': 'kino_id'}, inplace=True)


    for row in md.itertuples():
        # 이미 처리된 경우 건너뛰기
        if len(combined_df) != 0 and row.Index in combined_df['kino_id']:
            print(f"already: {row.Index}")
            continue
        # if hasattr(row, 'tmdb_id') and pd.notna(row.tmdb_id) and int(row.Index) in processed_tmdb_ids:
        #     continue

        retry_count = 0  # 재시도 횟수 초기화

        while retry_count < MAX_RETRIES:
            try:
                # tmdb_id 가져오기
                tmdb_id = get_tmdb_id(row)
                if tmdb_id is None or tmdb_id in processed_tmdb_ids:
                    item_data = row._asdict()
                    item_data.update({
                        'tmdb_id': "",
                        'tmdb_poster_img': "",
                        'tmdb_release_date': "",
                        'vote_count': 0,
                        'vote_average': 0,
                        'popularity': 0,
                    })
                    # combined_df = pd.concat([combined_df, pd.DataFrame([row._asdict()])], ignore_index=True)
                else:
                    # tmdb_id로 상세 정보 가져오기
                    movie_details = get_movie_details(tmdb_id)

                    # 기존 데이터와 상세 정보를 병합
                    item_data = row._asdict()

                    # 상세 정보 추가
                    poster_path = movie_details.get('poster_path')[0]
                    release_date = movie_details.get('release_date')[0]
                    vote_count = movie_details.get('vote_count')[0]
                    vote_average = movie_details.get('vote_average')[0]
                    popularity = movie_details.get('popularity')[0]

                    item_data.update({
                        'tmdb_id': tmdb_id,
                        'tmdb_poster_img': f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else None,
                        'tmdb_release_date': release_date if release_date else None,
                        'vote_count': vote_count if vote_count is not None else None,
                        'vote_average': vote_average if vote_average is not None else None,
                        'popularity': popularity if popularity is not None else None,
                    })

                    print(f"{file_num} - {len(combined_df)}: {row.Index} {row.titleKr}'s tmdb_id: {tmdb_id}")

                # DataFrame에 행 추가
                combined_df = pd.concat([combined_df, pd.DataFrame([item_data])], ignore_index=True)

                processed_tmdb_ids.add(row.Index)  # 기록

                # 25개마다 저장
                if len(combined_df) % 25 == 0:
                    # 'Index' 열을 'kino_id'로 변경
                    # if 'id' in combined_df.columns:
                    #     combined_df.rename(columns={'id': 'kino_id'}, inplace=True)
                    # 삭제된 데이터와 유지된 데이터 분리
                    combined_df['Index'] = combined_df['kino_id']  # 'Index' 칼럼 복사

                    combined_df = combined_df.drop_duplicates(subset=['Index'], keep='first')
                    # removed_duplicates = combined_df[combined_df.duplicated(subset=['Index'], keep='first')]


                    # 'kino_id'를 기준으로 JSON 변환
                    try:
                        final_data = combined_df.set_index('Index').to_dict(orient='index')
                    except KeyError as e:
                        print("KeyError: ", e)
                        print("Available columns: ", combined_df.columns)
                        raise e

                    # JSON 파일로 저장
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(final_data, f, ensure_ascii=False, indent=4)

                break  # 성공 시 루프 탈출

            except Exception as e:
                retry_count += 1
                print(f"Error processing row {row.Index} in {file_name} (Retry {retry_count}/{MAX_RETRIES}): {e}")
                time.sleep(2)  # 재시도 전에 딜레이 추가
        # 최대 재시도 초과 시 건너뛰기
        if retry_count == MAX_RETRIES:
            print(f"Skipping row {row.Index} in {file_name} after {MAX_RETRIES} retries.")

    # 'Index' 열을 'kino_id'로 변경
    if 'Index' in combined_df.columns:
        combined_df.rename(columns={'Index': 'kino_id'}, inplace=True)

    # 최종 저장: Kino ID를 키로 사용하여 딕셔너리 형태로 변환
    final_data = combined_df.set_index('kino_id').T.to_dict('index')

    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"Final data for {file_name} saved to {output_file}")

    file_num += 1
