from kino_api_client import KinoAPIClient
from kino_data_processor import KinoDataProcessor


class KinoDataExtractor:

    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def extract(self):
        movieClient = KinoAPIClient("contents")
        staffClient = KinoAPIClient("staff")
        processor = KinoDataProcessor()

        data = {}

        for i in range(self.lower_bound, self.upper_bound + 1):
            movieInfo = movieClient.make_request(i)
            staffInfo = staffClient.make_request(i)
            result = processor.process(movieInfo=movieInfo, staffInfo=staffInfo)

            if result is None:
                continue

            content_name = result["id"]
            data[content_name] = result

        return data
