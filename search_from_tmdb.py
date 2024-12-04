import json
import os
import requests
import pandas as pd
import time  # time 모듈을 추가하여 대기 시간 추가

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_URL = "https://api.themoviedb.org/3"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzY2JlN2Q1ZWRkMjk0MDVlNmJmZmU4NjRjMmQ1MTc3NCIsIm5iZiI6MTczMTgzMzcyNS45MzE5MzAzLCJzdWIiOiI2NmQ2NmNmODczOTg5ZTk5YTA5NGIxNDAiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.iusuq7CPQbgNdWm6gBl1Fp3oNSLPYxd6bNoFesp2V8g"


def search_movie_by_title(title):
    """영화 제목으로 TMDB에서 검색합니다."""
    url = f"{BASE_URL}/search/movie"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    params = {
        "query": title,  # 검색할 영화 제목
        "language": "ko",  # 한국어 응답 (영어 제목)
    }

    while True:  # 무한 루프를 사용하여 SSLError 발생 시 재시도
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return pd.DataFrame(response.json()['results'])
            else:
                print(f"Error at search_movie_by_title\n")
                print(f"Title:{title}\nError: {response.status_code}")
                print(response.text)
                print("\n\n")
                return None
        except requests.exceptions.SSLError as e:
            print(f"SSLError occurred while searching for movie: {title}. Retrying in 5 seconds...")
            time.sleep(5)  # 5초 대기 후 재시도


def search_movie_by_title_eng(title):
    """영화 제목으로 TMDB에서 검색합니다."""
    url = f"{BASE_URL}/search/movie"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    params = {
        "query": title,  # 검색할 영화 제목
        "language": "en: US",  # 영어 응답 (영어 제목)
    }

    while True:  # 무한 루프를 사용하여 SSLError 발생 시 재시도
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return pd.DataFrame(response.json()['results'])
            else:
                print(f"Error at search_movie_by_title_eng\n")
                print(f"Title:{title}\nError: {response.status_code}")
                print(response.text)
                print("\n\n")
                return None
        except requests.exceptions.SSLError as e:
            print(f"SSLError occurred while searching for movie (English): {title}. Retrying in 5 seconds...")
            time.sleep(5)  # 5초 대기 후 재시도


def get_movie_details(movie_id):
    """영화 ID를 사용하여 TMDB에서 영화의 상세 정보를 가져옵니다 (한국어 포스터 포함)."""
    url = f"{BASE_URL}/movie/{movie_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    params = {
        "language": "ko",  # 한국어로 요청하여 한국어 포스터 포함
    }

    while True:  # 무한 루프를 사용하여 SSLError 발생 시 재시도
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()

                # 리스트 데이터를 문자열로 변환 (필요시 더 세분화 가능)
                data['genres'] = ', '.join([genre['name'] for genre in data['genres']])
                data['production_companies'] = ', '.join([company['name'] for company in data['production_companies']])
                data['production_countries'] = ', '.join([country['name'] for country in data['production_countries']])
                data['spoken_languages'] = ', '.join([language['name'] for language in data['spoken_languages']])

                # 데이터프레임 변환
                df = pd.DataFrame([data])
                return df
            else:
                print(f"Error at get_movie_details\n")
                print(f"Movie_Id:{movie_id}\nError: {response.status_code}")
                print(response.text)
                print("\n\n")
                return None
        except requests.exceptions.SSLError as e:
            print(f"SSLError occurred while fetching movie details (ID: {movie_id}). Retrying in 5 seconds...")
            time.sleep(5)  # 5초 대기 후 재시도


def filter_by_overview(movies_id, target_overview, target_year):
    """
    주어진 결과에서 overview로 특정 영화 필터링
    """

    if len(movies_id) == 0:
        print("title로 검색된 결과자체가 없음!\n")
        return None
    all_overviews = [target_overview]
    id_list = []

    all_overviews2 = []
    id_list2 = []
    for id in movies_id:
        # 영화의 상세 정보를 가져오기
        movie_details = get_movie_details(id)

        if movie_details is None:
            continue;

        overview = movie_details.get('overview')[0]
        if len(overview) == 0:
            # print("overview no")
            continue
        release_date = movie_details.get('release_date')[0]
        if release_date is None:
            continue
        year = release_date.split("-")[0]
        if year is None or year == "":
            continue

        if abs(int(year) - int(target_year)) > 2:
            # print(f"year difference: year({year}), target_year({target_year})")
            all_overviews2.append(overview)
            id_list2.append(id)
            continue
        # print(f"id:{id}\noverview: {overview}\ntarget_overview: {target_overview}\n")
        # print(f"overview == target_overview 결과 : {overview[:min(len(overview), len(target_overview))] == target_overview[:min(len(overview), len(target_overview))]}\n\n")

        # 유사도 검사해보기
        all_overviews.append(overview)
        id_list.append(id)

    if len(id_list) == 0:

        all_overviews += all_overviews2
        id_list += id_list2
        if len(id_list) == 0:
            print(f"id_list is empty len(id_list2): {len(id_list2)}\n")
            return None

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_overviews)

    # 타겟 줄거리와 나머지 영화들의 유사도 계산
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # 가장 유사한 영화 찾기
    most_similar_index = similarity_scores.argmax()
    most_similar_score = similarity_scores[most_similar_index]

    # result = [(id_list[i], similarity_scores[i]) for i in range(len(id_list))]
    # print(f"result:\n{result}\n\n")

    return id_list[most_similar_index]


def get_tmdb_id(content):
    """
    content를 itertuples()로 받아서 tmdb의 id를 반환해주는 함수
    """
    # movies_id = search_tmdb_movie(content.content_name)
    movies_id = set()

    # 영화 검색
    movies = search_movie_by_title(content.content_name)
    if movies is not None:
        if 'id' in movies.columns:  # 'id' 컬럼이 있는지 확인
            for id in movies['id']:
                movies_id.add(id)

    # 영어 제목 검색
    movies_eng = search_movie_by_title_eng(content.english_name)
    if movies_eng is not None:
        if 'id' in movies_eng.columns:  # 'id' 컬럼이 있는지 확인
            for id in movies_eng['id']:
                movies_id.add(id)


    movie = filter_by_overview(movies_id, content.plot, content.year)

    if movie is None:
        print(f"{content.content_name} is None\n")
        return None

    return movie

