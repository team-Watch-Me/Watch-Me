class KinoDataProcessor:

    def __init__(self):
        self.provider_mapping = {
            18: 'U+모바일tv',
            17: '디즈니+',
            14: '쿠팡플레이',
            10: '티빙',
            8: '웨이브',
            5: '왓챠',
            4: '넷플릭스',
            2: '씨네폭스',
            1: '네이버 시리즈온'
        }
        pass

    def process(self, movieInfo, staffInfo):

        if movieInfo['data']['movie'] is None:
            return None

        if movieInfo['data']['movie']['mediaType'] != "MOVIE":
            return None

        data = {}

        data['content_name'] = movieInfo['data']['movie']['titleKr']
        data['english_name'] = movieInfo['data']['movie']['titleEn']
        data['plot'] = movieInfo['data']['movie']['synopsis']
        data['genre'] = movieInfo['data']['movie']['genres']
        data['age_rating'] = movieInfo['data']['movie']['rating']
        data['year'] = movieInfo['data']['movie']['openYear']
        data['running_time'] = movieInfo['data']['movie']['showTime']

        data['streaming_provider'] = []
        for provider in movieInfo['data']['movie']['vodOfferItems']:
            if provider['monetizationType'] != 'streaming':
                continue
            if provider['providerId'] in self.provider_mapping:
                data['streaming_provider'].append(self.provider_mapping[provider['providerId']])

        data['country'] = []
        for country in movieInfo['data']['movie']['nations']:
            data['country'].append(country['name'])

        data['staff'] = []
        for staff in staffInfo['data']['directors']:
            data['staff'].append(staff['person']['nameKr'])

        data['actor'] = []
        for actor in staffInfo['data']['actors']:
            data['actor'].append(actor['person']['nameKr'])

        for key, value in data.items():
            if not value:
                return None

        return data
