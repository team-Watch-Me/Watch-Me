import json
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
kino_json = open('./kino.json', 'r', encoding='utf-8')
kino = json.load(kino_json)

page_size = 10

for i in range(1, page_size):
    url = 'https://m.kinolights.com/title/' + str(i)
    driver.get(url)

    content_name = driver.find_elements(By.CSS_SELECTOR, kino["css_selector"]["content_name"])
    streaming_providers = driver.find_elements(By.CSS_SELECTOR, kino["css_selector"]["streaming_provider"])

    if not content_name:
        continue

    print(content_name[0].text + ":")
    for streaming_provider in streaming_providers:
        print(streaming_provider.text)

    print()

driver.quit()
