import requests
import json


class KinoAPIClient:

    def __init__(self):
        self.kino_json = open('./kino.json', 'r', encoding='utf-8')
        self.kino = json.load(self.kino_json)
        self.url = self.kino["url"]
        self.headers = self.kino["headers"]
        self.data = self.kino["data"]

    def make_request(self, movie_id):
        self.data["variables"]["movieId"] = movie_id
        response = requests.post(self.url, headers=self.headers, json=self.data)

        if response.status_code == 200:
            print(response.json())
        else:
            print(f"fail: {response.status_code}")
            print(response.text)
