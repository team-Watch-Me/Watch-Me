from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

from REST_API.dtt_class import *

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

    def create_search_page_query(self, key, OTT):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {"match": {"titleKr": key}},
                                    {"match": {"titleEn": key}},
                                    {"match": {"titleOri": key}},
                                    {"terms": {"genres": [key]}},
                                    {"terms": {"actor": [key]}},
                                    {"terms": {"staff": [key]}}
                                ],
                                "minimum_should_match": 1
                            }
                        }
                    ],
                    "filter": [
                        {"terms": {"streaming_provider": OTT}}
                    ]
                }
            }
        }

        return query


    def create_main_page_query(self, key, OTT):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"terms": {"genres": [key]}}
                    ],
                    "filter": [
                        {"terms": {"streaming_provider": OTT}}
                    ]
                }
            }
        }
        return query

    def search_movie(self, index, query):
        response = self.opensearch_client.search(index=index, body=query)
        return response

    def process_response(self, response):
        result = []
        for hit in response['hits']['hits']:  # todo = 반복문 순회해서 상위 ~개로 만들기
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

            if len(result) >= 10:
                break

            result.append(movie)

        return result

    def process_search_page(self, item):
        filter = []

        if item.netflix_selected is True:
            filter.append("넷플릭스")
        if item.tving_selected is True:
            filter.append("티빙")
        if item.coupang_selected is True:
            filter.append("쿠팡플레이")
        if item.watcha_selected is True:
            filter.append("왓챠")
        if item.wavve_selected is True:
            filter.append("웨이브")

        query = self.create_search_page_query(item.searchString, filter)
        response = self.search_movie("movies", query)
        return self.process_response(response)

    def process_main_page(self, item):
        filter = []

        if item.netflix_selected is True:
            filter.append("넷플릭스")
        if item.tving_selected is True:
            filter.append("티빙")
        if item.coupang_selected is True:
            filter.append("쿠팡플레이")
        if item.watcha_selected is True:
            filter.append("왓챠")
        if item.wavve_selected is True:
            filter.append("웨이브")

        query = self.create_main_page_query(item.genre, filter)
        response = self.search_movie("movies", query)
        return self.process_response(response)
