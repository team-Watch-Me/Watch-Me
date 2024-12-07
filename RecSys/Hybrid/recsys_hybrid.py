import numpy as np
import pandas as pd
import pickle

# cosine 유사도 행렬
tmp2_cosine_sim_description = np.load('cosine_sim_description.npy')
tmp2_cosine_sim_metadata = np.load('cosine_sim_metadata.npy')


# indices
with open('indices.pkl', 'rb') as f:
    tmp_indices = pickle.load(f)

# 모델 불러오기
with open('svd_model.pkl', 'rb') as f:
    tmp_svd = pickle.load(f)

# DataFrame 불러오기
tmp_pmd = pd.read_pickle('pmd.pkl')

"""

필요한 것
1. pmd: soup 있던 md
2. svd: 협업 필터링
3. cosine_sim_description, cosine_sim_meta
4. indices: title → id(tmdb)
"""

def hybrid(userId, title, weight_description=0.1, weight_metadata=0.9):
    # 영화 제목을 통해 인덱스 가져오기
    idx = tmp_indices[title]
    
    # 영화 설명 유사도 (TF-IDF)와 메타데이터 유사도 (감독, 배우, 장르) 가져오기
    sim_scores_description = list(enumerate(tmp2_cosine_sim_description[int(idx)]))
    sim_scores_metadata = list(enumerate(tmp2_cosine_sim_metadata[int(idx)]))
    
    # 두 유사도 행렬을 결합 (가중합)
    sim_scores = [
        (i[0], weight_description * i[1] + weight_metadata * j[1])
        for i, j in zip(sim_scores_description, sim_scores_metadata)
    ]
    
    # 유사도 순으로 정렬 (가장 유사한 것부터)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # 상위 25개 영화 선택 (자기 자신 제외)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]
    
    # 영화 데이터 가져오기 (제목, 투표수, 평균 평점, 년도, id)
    movies = tmp_pmd.iloc[movie_indices][['name_kr', 'vote_count', 'vote_average', 'year', 'tmdb_id']]

    # SVD를 통해 예측된 평점 계산
    movies['est'] = movies['tmdb_id'].apply(lambda x: tmp_svd.predict(userId, x).est)
    
    # 예측된 평점 기준으로 상위 10개 영화 추천
    movies = movies.sort_values('est', ascending=False)
    
    return movies.head(10)


print(hybrid(123, '아마존의 눈물'))