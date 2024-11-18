from kino_crawler import KinoCrawler

import json

def main():
    crawler = KinoCrawler(20)
    crawler.add_all_fields()

    # 필수 필드 정의 (가변적)
    
    required_fields = ["content_name", "streaming_provider", "plot", "genre", "age_rating", "country", "release_date", "running_time", "year" ]
    data = crawler.crawl()

    # 필터링: 모든 필수 필드가 있는 데이터만 추출
    filtered_data = {
        key: value
        for key, value in data.items()
        if all(field in value and value[field] for field in required_fields)
    }
    #filtered_data = [item for item in data if all(field in item for field in required_fields)]
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(filtered_data, file, ensure_ascii=False, indent=4)

main()