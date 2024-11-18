import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


class KinoCrawler:

    def __init__(self, page_size):
        self.driver = webdriver.Chrome()
        self.kino_json = open('./kino.json', 'r', encoding='utf-8')
        self.kino = json.load(self.kino_json)
        self.page_size = page_size
        self.crawl_dict = []
        self.fields = []
        for field in self.kino["css_selector"]:
            self.fields.append(field)

    def __del__(self):
        self.driver.quit()

    def crawl(self):
        data = {}

        for i in range(1, self.page_size):
            url = 'https://m.kinolights.com/title/' + str(i)
            self.driver.get(url)

            if not self.verify_url():
                continue

            self.expand_data()

            content_name = self.driver.find_elements(By.CSS_SELECTOR, self.kino["css_selector"]["content_name"])[0].text
            contents = {}

            for field in self.crawl_dict:
                elements = self.driver.find_elements(By.CSS_SELECTOR, self.kino["css_selector"][field])
                contents[field] = []
                for element in elements:
                    contents[field].append(element.text)
            
            
            data[content_name] = contents
            required_fields = self.fields
            #required_fields = ["content_name", "streaming_provider", "plot", "genre", "age_rating", "country", "release_date", "running_time", "year" ]
            filtered_data = {
                key: value
                for key, value in data.items()
                if all(field in value and value[field] for field in required_fields)
            }
        return filtered_data

    def verify_url(self):
        content_name = self.driver.find_elements(By.CSS_SELECTOR, self.kino["css_selector"]["content_name"])
        if not content_name:
            return False
        else:
            return True

    def add_field(self, field):
        self.crawl_dict.append(field)

    def add_all_fields(self):
        for field in self.fields:
            self.add_field(field)

    def expand_data(self):
        try:
            while True:
                btn = self.driver.find_element(By.CSS_SELECTOR, '#contents > div.info.tab-item > section:nth-child(1) > div > div > div > button')
                btn.click()
                time.sleep(0.2)
        except:
            return
