import json
from kino_data_extractor import KinoDataExtractor


def main():
    lower_bound = 0
    upper_bound = -1

    dataExtractor = KinoDataExtractor(lower_bound, upper_bound)
    data = dataExtractor.extract()

    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


main()
