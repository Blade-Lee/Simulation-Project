from scrapy.contrib.spiders import CrawlSpider, Rule
from doubanmusic.items import DoubanmusicItem
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
import re

class MusicSpider(CrawlSpider):
    name = "Music"
    allowed_domains = ["music.douban.com"]
    start_urls = [
        "http://music.douban.com/programmes/"
    ]

    rules = [
        #Rule(SgmlLinkExtractor(allow=('/programme/\d+', )), callback='parse_music_home_page', process_request='add_cookie'),
        Rule(SgmlLinkExtractor(allow=('/programme/\d+', )), callback='parse_music_home_page', follow=True, process_request='add_cookie'),
    ]

    def add_cookie(self, request):
        request.replace(cookies=[{'name': 'COOKIE_NAME', 'value': 'VAULE', 'domain': '.douban.com', 'path': '/'},])
        return request

    def __get_id_from_music_url(self, url):
        m = re.search("^http://music.douban.com/programme/(\d+)", url)
        if m:
            return m.groups(1)
        else:
            return 0

    def parse_music_home_page(self, response):
        self.log("Fetch douban homepage page: %s" % response.url)

        hxs = HtmlXPathSelector(response)
        item = DoubanmusicItem()

        item['music_list_id'] = self.__get_id_from_music_url(response.url)[0]

        item['music_list'] = []

        music_list = hxs.select('//div[@class="song-item"]')
        for song in music_list:
            song_item = {
                "song_id": song.select('@data-songid').extract()[0],
                "song_length": song.select('@data-plength').extract()[0]
            }
            item['music_list'].append(song_item)

        return item
