from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

from backend.REST_API.dtt_class import *

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
        pass

    def search_movie(self, id):
        response = self.opensearch_client.get(index="movies", id=id)
        return response

    def process_search_page(self, item):
        result = []

        movie = ReturnMovie()
        response = self.search_movie(item.searchString)  # todo = 반복문 순회해서 상위 ~개로 만들기

        movie.title = response['_source']['content_name']
        movie.genre = response['_source']['genre']
        movie.age_rating = response['_source']['age_rating']
        movie.country = response['_source']['country']
        movie.year = response['_source']['year']
        movie.running_time = response['_source']['running_time']
        movie.description = response['_source']['plot']
        movie.actor = response['_source']['actor']
        movie.staff = response['_source']['staff']
        movie.poster_url = ""  # todo
        movie.ott_provider = []  # todo

        result.append(movie)

        return result

    def process_main_page(self, item):
        pass
