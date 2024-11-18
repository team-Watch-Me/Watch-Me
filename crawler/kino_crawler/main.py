from kino_crawler import KinoCrawler

import json

def main():
    crawler = KinoCrawler(20)
    crawler.add_all_fields()
    
    data = crawler.crawl()
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

main()