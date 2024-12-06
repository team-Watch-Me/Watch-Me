import json
import os
import time
import logging
from kino_data_extractor import KinoDataExtractor
import requests

# 로깅 설정
logging.basicConfig(filename='crawler.log', level=logging.INFO)

def main(lower_bound, upper_bound):
    try:
        dataExtractor = KinoDataExtractor(lower_bound, upper_bound)
        data = dataExtractor.extract()
        return data
    except requests.exceptions.SSLError as e:
        logging.error(f"SSLError occurred while crawling from {lower_bound} to {upper_bound}: {e}")
        raise e
    except Exception as e:
        logging.error(f"Error occurred while crawling from {lower_bound} to {upper_bound}: {e}")
        raise e

def append_to_json(file_path, new_data):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = {}  # 파일이 비어 있거나 JSON 형식이 아니면 빈 딕셔너리로 초기화
    else:
        existing_data = {}

    # 기존 데이터에 새로운 데이터 추가
    existing_data.update(new_data)

    # 업데이트된 데이터를 파일에 다시 저장
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

def get_last_successful_record(file_path):
    # 마지막 성공적인 titleId를 반환
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                existing_data = json.load(file)
                # titleId 값을 기준으로 가장 큰 값을 반환
                return max(
                    (item.get("titleId", 0) for item in existing_data.values()),
                    default=0
                )
            except json.JSONDecodeError:
                return 0  # JSON이 비어 있으면 0부터 시작
    return 0  # 파일이 없다면 0부터 시작

def crawl_with_retries(result_file, start_index, end_index, record):
    while start_index < end_index:
        try:
            # 크롤링 실행
            data = main(start_index, min(start_index + record - 1, end_index))
            if data:
                append_to_json(result_file, data)
            start_index += record  # 성공하면 다음 범위로 이동
            time.sleep(1)  # 서버에 부담을 주지 않도록 대기
        except Exception as e:
            logging.error(f"Retrying from {start_index} due to error: {e}")
            time.sleep(5)  # 잠시 대기 후 재시도

# 결과를 저장할 파일 경로
result_file = 'result_95000_to_100000.json'

# 마지막 성공적인 기록 범위 확인
start_index = 95000 + 1
end_index = 100000
record = 25  # 언제마다 기록할 것인지

# 크롤링 실행
crawl_with_retries(result_file, start_index, end_index, record)