import json
from data_inserter import DataInserter


def main():
    file_path = './result.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    data_inserter = DataInserter()
    data_inserter.insert_data('movies', data)


main()
