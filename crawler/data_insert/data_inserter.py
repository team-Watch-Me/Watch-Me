from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

host = 'search-watch-me-opensearch-zsvsvo2lqm56sz2pnirhero2pe.aos.ap-southeast-2.on.aws'
region = 'ap-southeast-2'
service = 'es'


class DataInserter:
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

    def insert_data(self, index_name, documents):
        for doc_id, doc_data in documents.items():
            try:
                response = self.opensearch_client.index(
                    index=index_name,
                    id=doc_id,
                    body=doc_data
                )
            except Exception as e:
                print(f"Error inserting document {doc_id}: {e}")
