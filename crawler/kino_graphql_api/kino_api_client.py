import requests
import json


class KinoAPIClient:

    def __init__(self, type):
        self.kino_json = open('kino_query.json', 'r', encoding='utf-8')
        self.kino = json.load(self.kino_json)
        self.url = self.kino[type]['url']
        self.headers = self.kino[type]["headers"]
        self.data = self.kino[type]["data"]

    def make_request(self, movie_id):
        self.data["variables"]["movieId"] = movie_id
        response = requests.post(self.url, headers=self.headers, json=self.data)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"fail: {response.status_code}")
            print(response.text)
