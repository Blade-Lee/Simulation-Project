from scrapy.contrib.spiders import CrawlSpider, Rule
from VideoCrawler.items import VideocrawlerItem
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy import log
import urllib
import urllib2
import json
import re

class VideoSpider(CrawlSpider):
    name = "Video"
    allowed_domains = ["v.youku.com"]
    start_urls = [
        "http://v.youku.com/v_show/id_XMTMxOTM2NTg4MA==.html?f=26028008&from=y1.3-ent-grid-196-10080.88558.1-1"
    ]

    rules = [
        Rule(SgmlLinkExtractor(allow=('/v_show/id_', )), follow=True, callback='parse_single_video', process_request='add_cookie')
    ]

    def add_cookie(self, request):
        request.replace(cookies=[{'name': 'COOKIE_NAME', 'value': 'VAULE', 'domain': 'v.youku.com', 'path': '/'},])
        return request

    def parse_single_video(self, response):

        item = VideocrawlerItem()

        video_url = response.url

        '''
        values = {
            'client_id': '67a5c2fe0ac1c936',
            'video_url': video_url
        }
        data = urllib.urlencode(values)
        url = "https://openapi.youku.com/v2/videos/show_basic.json"
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        json_load = json.load(response)
        '''

        item['video_url'] = video_url
        #item['video_len'] = json_load['duration']

        return item