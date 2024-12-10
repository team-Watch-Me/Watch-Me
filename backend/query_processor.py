from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

from REST_API.dtt_class import *
from Recommendation_System.recommendationsystem import RecommendationSystem

host = 'search-watch-me-opensearch-zsvsvo2lqm56sz2pnirhero2pe.aos.ap-southeast-2.on.aws'
region = 'ap-southeast-2'
service = 'es'


class QueryProcessor:
    def __init__(self):
        self.IAM_credentials = boto3.Session().get_credentials()
        self.awsauth = AWS4Auth(self.IAM_credentials.access_key, self.IAM_credentials.secret_key, region, service,
                                session_token=self.IAM_credentials.token)
        self.opensearch_client = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=self.awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

    @staticmethod
    def create_id_query(key):
        query = {
            "query": {
                "term": {
                    "_id": key
                }
            }
        }
        return query

    @staticmethod
    def process_response(response):
        result = []
        for hit in response['hits']['hits']:
            movie = ReturnMovie()

            movie.title = hit['_source']['titleKr']
            movie.titleEn = hit['_source']['titleEn']
            movie.genre = hit['_source']['genres']
            movie.age_rating = hit['_source']['age_rating']
            movie.country = hit['_source']['country']
            movie.year = hit['_source']['openYear']
            movie.running_time = hit['_source']['running_time']
            movie.description = hit['_source']['synopsis']
            movie.actor = hit['_source']['actor']
            movie.staff = hit['_source']['staff']
            movie.poster_url = hit['_source']['posterImage']
            movie.ott_provider = hit['_source']['streaming_provider']
            movie.movie_id = str(hit['_source']['tmdb_id'])

            result.append(movie)

        return result

    @staticmethod
    def extract_ott_list(item):
        ott_list = []

        if item.netflix_selected is True:
            ott_list.append("넷플릭스")
        if item.tving_selected is True:
            ott_list.append("티빙")
        if item.coupang_selected is True:
            ott_list.append("쿠팡플레이")
        if item.watcha_selected is True:
            ott_list.append("왓챠")
        if item.wavve_selected is True:
            ott_list.append("웨이브")
        if item.disney_selected is True:
            ott_list.append("디즈니+")

        return ott_list

    def search_item(self, index, query):
        response = self.opensearch_client.search(index=index, body=query)
        return response

    def push_item(self, index, document):
        response = self.opensearch_client.index(index=index, id=document['id'], body=document['body'])
        return response

    def process_search_page(self, item, recommendation_system):
        genre_list = []
        ott_list = self.extract_ott_list(item)

        md = recommendation_system.recommend_search(item.searchString, ott_list, genre_list)

        return_list = []
        for elem in md.itertuples():
            query = self.create_id_query(elem.tmdb_id)
            response = self.search_item("movies", query)
            return_list += self.process_response(response)

        return return_list

    def process_main_page_genre(self, item, recommendation_system):
        genre_list = [item.genre]
        ott_list = self.extract_ott_list(item)

        md = recommendation_system.recommend_simple(ott_list, genre_list)

        return_list = []
        for elem in md.itertuples():
            query = self.create_id_query(elem.tmdb_id)
            response = self.search_item("movies", query)
            return_list += self.process_response(response)

        return return_list

    def process_main_page_personal_recommendation(self, item, recommendation_system):
        ott_list = self.extract_ott_list(item)

        md = recommendation_system.recommend_hybrid_one(user_id=item.user_id, title="범죄도시", ott_list=ott_list)
        return_list = []
        for elem in md.itertuples():
            query = self.create_id_query(elem.tmdb_id)
            response = self.search_item("movies", query)
            return_list += self.process_response(response)

        return return_list

    def process_main_page_integrated(self, item, recommendation_system):
        genre_list = []
        ott_list = self.extract_ott_list(item)

        md = recommendation_system.recommend_simple(ott_list, genre_list)
        return_list = []
        for elem in md.itertuples():
            query = self.create_id_query(elem.tmdb_id)
            response = self.search_item("movies", query)
            return_list += self.process_response(response)

        return return_list

    def process_submit(self, item):
        document = {}
        user_id = 'wm_' + item.user_id
        time = str(item.timestamp)
        document['id'] = user_id + '_' + time
        document['body'] = {
            "user_id": user_id,
            "movie_id": item.movie_id,
            "timestamp": time
        }

        return self.push_item('user_rating', document)
