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

        data['id'] = movieInfo['data']['movie']['id']
        data['titleKr'] = movieInfo['data']['movie']['titleKr']
        data['titleEn'] = movieInfo['data']['movie']['titleEn']
        data['titleOri'] = movieInfo['data']['movie']['titleOri']
        data['synopsis'] = movieInfo['data']['movie']['synopsis']
        data['genres'] = movieInfo['data']['movie']['genres']
        data['productionYear'] = movieInfo['data']['movie']['productionYear']
        data['posterImage'] = movieInfo['data']['movie']['posterImage']['pathUrl']
        data['age_rating'] = movieInfo['data']['movie']['rating']
        data['openYear'] = movieInfo['data']['movie']['openYear']
        data['running_time'] = movieInfo['data']['movie']['showTime']

        data['streaming_provider'] = []
        for provider in movieInfo['data']['movie']['vodOfferItems']:
            if provider['monetizationType'] != 'streaming':
                continue
            if provider['providerId'] in self.provider_mapping:
                data['streaming_provider'].append((self.provider_mapping[provider['providerId']], provider['url']))

        data['country'] = []
        for country in movieInfo['data']['movie']['nations']:
            data['country'].append(country['name'])

        data['releases'] = []
        for release in movieInfo['data']['movie']['releases']:
            data['releases'].append(release)

        data['staff'] = []
        for staff in staffInfo['data']['directors']:
            data['staff'].append(staff['person']['nameKr'])

        data['actor'] = []
        for actor in staffInfo['data']['actors']:
            data['actor'].append(actor['person']['nameKr'])

        return data
