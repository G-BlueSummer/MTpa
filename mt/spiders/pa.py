import scrapy
import json
import base64
import zlib
from math import ceil
from datetime import datetime

# 生成一个token
def gen_token():
    ts = int(datetime.now().timestamp() * 1000)
    token_dict = {
        'rId': 100900,
        'ver': '1.0.6',
        'ts': ts,
        'cts': ts + 100 * 1000,
        'brVD': [1010, 750],
        'brR': [[1920, 1080], [1920, 1040], 24, 24],
        'bI': ['https://gz.meituan.com/meishi/', ''],
        'mT': [],
        'kT': [],
        'aT': [],
        'tT': [],
        'aM': '',
        'sign': 'eJwljU0KwjAQhe/iIrvaVmutQhbiShB3HmBMRh1skjKZCK7duPRCXkfwFgZdvY/H+xkBI2ysrpQBwT+Q3HbgUL8fz8/9pSx5j7wOyctKhHNGhUHIpbgOFnVdqcB0Ir/nXp9FhrgsS2PHDkkS+LEJrswcz1SqAU65kIUlT+p60qqhBzkGdtlmipctXrHPHAOLVini7y8lsrqZ1VVnWlMsDnVbNHaKBcwWUDQG51XX4RHmk9EXKxlILw=='
    }

    encode = str(token_dict).encode()
    compress = zlib.compress(encode)
    b_encode = base64.b64encode(compress)
    token = str(b_encode, encoding='utf-8')
    return token

# 生成一个请求参数
def gen_params(page):
    return {
        'cityName': '成都',
        'cateId': '0',
        'areaId': '0',
        'sort': '',
        'dinnerCountAttrId': '',
        'page': str(page),
        'userId': '',
        'uuid': '45108c6c-9b16-4d3e-a59a-4ce7088efa72',
        'platform': '1',
        'partner': '126',
        'originUrl': 'https://cd.meituan.com/meishi/',
        'riskLevel': '1',
        'optimusCode': '10',
        '_token': gen_token()
    }

class MTSpider(scrapy.Spider):
    name = "MT"

    def __init__(self):
        self.maxPage = 0
        self.curPage = 1

    def start_requests(self):
        # print(gen_params())
        return [
            scrapy.FormRequest(
                'https://cd.meituan.com/meishi/api/poi/getPoiList',
                method='GET', formdata=gen_params(self.curPage),
                callback=self.parse
                )
        ]

    def parse(self, response):
        data = json.loads(response.text)['data']
        # 更新最大页数
        self.maxPage = ceil(data['totalCounts'] / 15)
        for info in data['poiInfos']:
            yield {
                'title': info['title'],
                'address': info['address'],
                'avgPrice': info['avgPrice']
            }

        # 爬取下一页
        if self.curPage < self.maxPage:
            self.curPage += 1
            yield scrapy.FormRequest(
                'https://cd.meituan.com/meishi/api/poi/getPoiList',
                method='GET',
                formdata=gen_params(self.curPage),
                callback=self.parse
                )
