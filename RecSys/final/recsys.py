import numpy as np
import pandas as pd
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from itertools import combinations
import os


class RecommendationSystem:
    """
    유저에 대한 개인 정보가 아니라 추천시스템 하나에 대해서만 저장
    """
    def __init__(self):
        self.cosine_sim_metadata = None      # metadata의 코사인 유사도
        self.tmdbId_to_matIdx = None         # title → index 로의 매핑
        self.matIdx_to_tmdbId = None
        
        self.svd = None                      # movielens_1m_data 기준으로 학습한 svd 모델
        self.ratings = None                  # (userid, movieid, ratings)으로 저장되어 있음
        
        self.md_original = None               # original data

        self.m = {}
        self.C = {}

        self.quailfied_md = {}

    def load(self):
        """
        초기 load
        """
        # ToDo: load하는 주소들 변경
        self.cosine_sim_metadata = np.load(
            'final/data/cosine_sim_metadata.npy')
        # ToDo: load하는 주소들 변경
        with open('final/data/matIdx_to_tmdbId.pkl', 'rb') as f:
            self.matIdx_to_tmdbId = pickle.load(f)

        # ToDo: load하는 주소 변경
        with open('final/data/tmdbId_to_matIdx.pkl', 'rb') as f:
            self.tmdbId_to_matIdx = pickle.load(f)

        # ToDo: load하는 주소들 변경
        self.ratings = pd.read_csv('final/data/ratings.csv')

        # ToDo: load하는 주소들 변경
        with open('final/data/svd_model.pkl', 'rb') as f:
            self.svd = pickle.load(f)
        
        # ToDo: load하는 주소들 변경
        self.md_original = pd.read_pickle('final/data/md.pkl')
        
        
        # self.md_original 정렬 미리하기
        
        # OTT 플랫폼 리스트
        every_ott_list = ['넷플릭스', '웨이브', '티빙', '디즈니+', '쿠팡플레이', '왓챠']

        # 모든 조합 생성
        for r in range(1, len(every_ott_list) + 1):  # r은 조합의 길이 (1개부터 전체까지)
            for combo in combinations(every_ott_list, r):
                combo_list = list(combo)
                combo_sorted = tuple(sorted(combo_list))
                md = self.get_md_filtered_by_ott_list(self.md_original, combo_list)
                # self.md에 대해서 self.C, self.m 업데이트
                vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
                vote_averages = md[md['vote_average'].notnull()]['vote_average'].astype('float')

                self.C[combo_sorted] = vote_averages.mean()
                # vote_counts를 내림차순으로 정렬
                vote_counts.sort_values(ascending=False)

                # quantile는 데이터를 크기대로 정렬하였을 때 분위수를 구하는 함수. quantile(0.95)는 상위 5%에 해당하는 값을 찾는 것
                self.m[combo_sorted] = vote_counts.quantile(0.95)
                m = self.m[combo_sorted]
                C = self.C[combo_sorted]
                def weighted_rating(x):
                    v = x['vote_count']
                    R = x['vote_average']
                    return (v/(v+m) * R) + (m/(m+v) * C)
                
                # 평가 수가 상위 5%인 데이터 추출
                md = md[(md['vote_count'] >= m) & (md['vote_count'].notnull()) & (md['vote_average'].notnull())]
                
                # 가중치 점수 계산 → 'wr' 행에 넣기
                md['wr'] = md.apply(weighted_rating, axis=1)

                # Weighted Rating 기준으로 정렬
                md = md.sort_values('wr', ascending=False)

                self.quailfied_md[combo_sorted] = md




    def get_md_filtered_by_ott_list(self, df, ott_list):
        """
        사용자의 ott list로 필터링해서 반환
        """
        def filter_streaming_providers(df, providers):
            # 복사본 생성
            filtered_df = df.copy()

            # 각 행의 streaming_provider에서 원하는 제공자만 필터링
            def filter_providers(providers_list):
                # 각 provider가 문자열이거나 리스트인 경우를 처리
                if isinstance(providers_list, list):
                    return [
                        provider for provider in providers_list
                        if any(desired in provider for desired in providers)
                    ]
                else:
                    # provider가 문자열일 경우
                    return [provider for provider in [providers_list] if any(desired in provider for desired in providers)]

            # 'streaming_provider' 열 필터링
            filtered_df["streaming_provider"] = filtered_df["streaming_provider"].apply(filter_providers)
            # 원하는 제공자가 포함된 행만 유지
            return filtered_df[filtered_df["streaming_provider"].map(len) > 0]
            
        # md를 해당 ott_list에 알맞게 변경
        md = filter_streaming_providers(df, ott_list)
        return md

    
    
    def get_md_filtered_by_genre_list(self, df, genre_list):
        """
        장르 리스트로 필터링해서 반환
        """
        md = df.copy()
        if len(genre_list) != 0:
            """
            장르를 필터링 할 경우
            """
            def filter_genre(df, genres):
                # 여러 장르 중 하나라도 포함된 행 필터링 (원본 df는 변경되지 않음)
                return df[df['genres'].apply(
                    lambda x: any(genre in x for genre in genres)
                )]
            
            qualified_genre = filter_genre(md, genre_list)
            return qualified_genre
        else:
            return md
       

    def get_qualified_md(self, ott_list):
        """
        인기가 좋은 movie_list 순으로 정렬
        """
        ott_tuple = tuple(sorted(ott_list))
        if self.quailfied_md[ott_tuple] is not None:
            return self.quailfied_md[ott_tuple]

        md = self.get_md_filtered_by_ott_list(self.md_original, ott_list)
        
        
        m = self.m[ott_tuple]
        C = self.C[ott_tuple]

        def weighted_rating(x):
            v = x['vote_count']
            R = x['vote_average']
            return (v/(v+m) * R) + (m/(m+v) * C)
        
        # 평가 수가 상위 5%인 데이터 추출
        md = md[(md['vote_count'] >= m) & (md['vote_count'].notnull()) & (md['vote_average'].notnull())]
        
        # 가중치 점수 계산 → 'wr' 행에 넣기
        md['wr'] = md.apply(weighted_rating, axis=1)

        # Weighted Rating 기준으로 정렬
        md = md.sort_values('wr', ascending=False)

        self.quailfied_md[ott_tuple] = md

        return md
    
    def update_ratings_and_svd(self, new_ratings):
        """
        새로운 rating이 들어왔을 때, 해당 평점을 바탕으로 rating을 업데이트 시켜주고 svd를 다시 업데이트 시켜준다.

        new_ratings : 새로운 rating 데이터프레임 (userId, movieId, rating, timestamp)
        """
        # 기존 ratings와 새로운 ratings를 합침
        combined_ratings = pd.concat([self.ratings, new_ratings], ignore_index=True)

        # 중복된 userId와 movieId에서 timestamp가 가장 큰 값만 유지
        combined_ratings = combined_ratings.loc[
            combined_ratings.groupby(['userId', 'movieId'])['timestamp'].idxmax()
        ]

        # 기존의 ratings를 업데이트
        self.ratings = combined_ratings

        # ratings 파일 업데이트
        # ToDo: 저장하는 주소들 변경
        self.ratings.to_csv("final/data/ratings.csv", index=False)

        # SVD 재학습
        self.svd.fit(self.ratings[['userId', 'movieId']], self.ratings['rating'])

        # SVD 파일 업데이트
        # ToDo: 저장하는 주소들 변경
        with open('final/data/svd_model.pkl', 'wb') as f:
            pickle.dump(self.svd, f)


    def recommend_simple(self, ott_list, genre_list, top_n=20):
        """
        단순 추천 시스템: 인기 순으로 상위 number 개의 작품을 반환

        genre_filter: 보고 싶은 장르
        """

        md = self.get_qualified_md(ott_list)

        md = self.get_md_filtered_by_genre_list(md, genre_list)
        
        return md[:top_n]


    def recommend_search(self, query, ott_list, genre_list, top_n=10):
        """
        주어진 query에 대해 가장 유사한 영화 정보를 반환하는 함수
        
        Parameters:
            query (str): 검색할 텍스트 (예: "영화 감독 배우")
            top_n (int): 반환할 결과의 수 (기본값: 10)
        
        Returns:
            pd.DataFrame: 유사도 높은 순서대로 상위 N개 결과를 담은 DataFrame
        """
        md = self.get_md_filtered_by_ott_list(self.md_original, ott_list)
        md = self.get_md_filtered_by_genre_list(md, genre_list)

        # 한국어 불용어 리스트 (예시)
        stop_words_ko = ['이', '그', '저', '것', '들', '과', '에', '의', '는', '가', '이랑', '하고', '도', '에서', '을', '를']

        # TF-IDF 벡터화
        tfidf = TfidfVectorizer(stop_words=stop_words_ko)

        # soup_search 컬럼과 search_query를 벡터화
        md['soup_search_tfidf'] = md['soup_search'].apply(lambda x: str(x))  # soup_search가 문자열로 처리되도록 보장
        md_tfidf_matrix = tfidf.fit_transform(md['soup_search_tfidf'])
        search_query_tfidf = tfidf.transform([query])

        # 코사인 유사도 계산
        cosine_similarities = cosine_similarity(search_query_tfidf, md_tfidf_matrix).flatten()

        # 유사도가 높은 순서대로 인덱스를 정렬
        related_docs_indices = cosine_similarities.argsort()[::-1]

        # 상위 N개의 결과를 반환
        top_results = md.iloc[related_docs_indices[:top_n]]

        return top_results # ['tmdb_id'] <- id만 반환 하고 싶으면 이걸 이어붙이면 됨
    
    def recommend_hybrid_one(self, user_id, tmdb_id, ott_list):
        """
        사용자에 알맞는 맞춤 추천을 제공

        input: user_id, title
        """

        md = self.get_md_filtered_by_ott_list(self.md_original, ott_list)
        # md = self.md_original.copy()

        # 영화 제목을 통해 인덱스 가져오기
        idx = self.tmdbId_to_matIdx[tmdb_id]
    

        # 영화 설명 유사도 (TF-IDF)와 메타데이터 유사도 (감독, 배우, 장르) 가져오기
        sim_scores = list(enumerate(self.cosine_sim_metadata[int(idx)]))

        # self.indices가 titleKr을 키로 하고 해당 tmdb_id나 다른 값들을 매핑한 pd.Series라고 가정
        valid_indices = []

        # md['titleKr']을 기준으로 self.indices에서 해당 값들을 찾아 valid_indices에 저장
        for tmdbId in md['tmdb_id']:
            if tmdbId != tmdb_id:
                valid_indices.append(self.tmdbId_to_matIdx[tmdbId])  # 존재하면 해당 값을 valid_indices에 추가

        # sim_scores에서 md에 포함된 인덱스만 남기도록 필터링
        sim_scores_filtered = [score for score in sim_scores if score[0] in valid_indices]

        # 유사도 순으로 정렬 (가장 유사한 것부터)
        sim_scores = sorted(sim_scores_filtered, key=lambda x: x[1], reverse=True)

        # 상위 25개 영화 선택 (자기 자신 제외)
        sim_scores = sim_scores[1:26]
        movie_indices = [str(self.matIdx_to_tmdbId[i[0]]) for i in sim_scores]

        movies = md.loc[movie_indices]

        # 최소 vote_count를 기준으로 필터링 (예: 100 이상)
        min_vote_count = 1
        movies = movies[movies['vote_count'] >= min_vote_count]

        # SVD를 통해 예측된 평점 계산
        movies['est'] = movies['tmdb_id'].apply(lambda x: self.svd.predict(user_id, x).est)

        # # 예측된 평점 기준으로 상위 10개 영화 추천
        movies = movies.sort_values('est', ascending=False)

        return movies[:10]

    def recommend_hybrid_multiple(self, user_id, tmdb_ids, ott_list):
        """
        여러 개의 tmdb_id에 대해 추천을 제공하는 함수

        input: user_id, tmdb_ids (리스트), ott_list
        """
        # 영화 데이터 필터링
        md = self.get_md_filtered_by_ott_list(self.md_original, ott_list)

        

        # 여러 tmdb_id에 대해 유사도 계산 후 합산
        combined_sim_scores = {}

        for tmdb_id in tmdb_ids:
            # tmdb_id를 통해 인덱스 가져오기
            idx = self.tmdbId_to_matIdx[tmdb_id]

            # 영화 설명 유사도 (TF-IDF)와 메타데이터 유사도 (감독, 배우, 장르) 가져오기
            sim_scores = list(enumerate(self.cosine_sim_metadata[int(idx)]))

            # 유사도를 합산
            for i, score in sim_scores:
                if i not in combined_sim_scores:
                    combined_sim_scores[i] = score
                else:
                    combined_sim_scores[i] += score

        # 유효한 인덱스 찾기 (md에 있는 tmdb_id만)
        valid_indices = []
        for tmdb_id in md['tmdb_id']:
            if tmdb_id in self.tmdbId_to_matIdx:
                if tmdb_id not in tmdb_ids:
                    valid_indices.append(self.tmdbId_to_matIdx[tmdb_id])

        sim_scores_filtered = [score for score in combined_sim_scores.items() if score[0] in valid_indices]
        # 유사도 순으로 정렬 (가장 유사한 것부터)
        sorted_sim_scores = sorted(sim_scores_filtered, key=lambda x: x[1], reverse=True)

        # 상위 25개 영화 선택 (자기 자신 제외)
        sorted_sim_scores = sorted_sim_scores[1:26]
        movie_indices = [str(self.matIdx_to_tmdbId[i[0]]) for i in sorted_sim_scores]

        # 영화 데이터에서 인덱스를 사용하여 영화 선택
        movies = md.loc[movie_indices]

        # 최소 vote_count를 기준으로 필터링 (예: 100 이상)
        min_vote_count = 1
        movies = movies[movies['vote_count'] >= min_vote_count]

        # SVD를 통해 예측된 평점 계산
        movies['est'] = movies['tmdb_id'].apply(lambda x: self.svd.predict(user_id, x).est)

        # 예측된 평점 기준으로 상위 10개 영화 추천
        movies = movies.sort_values('est', ascending=False)

        return movies[:10]
    



# # 인스턴스 생성
# rec_sys = RecommendationSystem()

# # 데이터를 로드
# try:
#     rec_sys.load()
# except FileNotFoundError:
#     print("필요한 데이터 파일이 없습니다. 샘플 데이터를 사용하세요.")


# ott_list = ['넷플릭스', '티빙', '웨이브', '디즈니+', '왓챠']
# genre_list = []

# result = rec_sys.recommend_simple(ott_list=ott_list, genre_list=genre_list)
# print(result[['titleKr', 'vote_average', 'vote_count']])

# OTT 플랫폼 리스트
# every_ott_list = ['넷플릭스', '웨이브', '티빙', '디즈니+', '쿠팡플레이', '왓챠']
# # 모든 조합 생성
# for r in range(1, len(every_ott_list) + 1):  # r은 조합의 길이 (1개부터 전체까지)
#     for combo in combinations(every_ott_list, r):
#         combo_list = list(combo)
#         result = rec_sys.recommend_simple(ott_list=combo_list, genre_list=genre_list)
#         print(result[['titleKr', 'vote_average', 'vote_count']])


# query = "과속스캔들"
# result = rec_sys.recommend_search(query=query, ott_list=every_ott_list, genre_list=genre_list)
# print(result[['titleKr', 'actor', 'vote_average', 'vote_count',  'genres']])

# for r in range(1, len(every_ott_list) + 1):  # r은 조합의 길이 (1개부터 전체까지)
#     for combo in combinations(every_ott_list, r):
#         combo_list = list(combo)
#         query = "과속스캔들"
#         result = rec_sys.recommend_search(query=query, ott_list=combo_list, genre_list=genre_list)
#         print(result[['titleKr', 'actor', 'vote_average', 'vote_count',  'genres']])
    
# title = "범죄도시 2" #, "범죄도시 2"]
# result = rec_sys.recommend_hybrid_one(user_id="se1", tmdb_id=619803, ott_list=ott_list)
# print(result[['titleKr', 'vote_average', 'vote_count',  'genres', 'streaming_provider']])
# print("---------------------------------------------------------")
# title = [18384, 729854, 252067]
# result = rec_sys.recommend_hybrid_multiple(user_id="se1", tmdb_ids=title, ott_list=ott_list)
# print(result[['titleKr', 'vote_average', 'vote_count',  'genres', 'streaming_provider']])
