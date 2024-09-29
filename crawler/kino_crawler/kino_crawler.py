import json

from selenium import webdriver
from selenium.webdriver.common.by import By

class KinoCrawler:

    def __init__(self, page_size):
        self.driver = webdriver.Chrome()
        self.kino_json = open('./kino.json', 'r', encoding='utf-8')
        self.kino = json.load(self.kino_json)
        self.page_size = page_size
        self.crawl_dict = []

    def __del__(self):
        self.driver.quit()

    def crawl(self):
        data = {}

        for i in range(1, self.page_size):
            url = 'https://m.kinolights.com/title/' + str(i)
            self.driver.get(url)

            if not self.verify_url():
                continue

            content_name = self.driver.find_elements(By.CSS_SELECTOR, self.kino["css_selector"]["content_name"])[0].text
            contents = {}

            for field in self.crawl_dict:
                elements = self.driver.find_elements(By.CSS_SELECTOR, self.kino["css_selector"][field])
                contents[field] = []
                for element in elements:
                    contents[field].append(element.text)

            data[content_name] = contents

        return data

    def verify_url(self):
        content_name = self.driver.find_elements(By.CSS_SELECTOR, self.kino["css_selector"]["content_name"])
        if not content_name:
            return False
        else:
            return True

    def add_field(self, field):
        self.crawl_dict.append(field)