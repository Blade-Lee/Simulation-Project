from scrapy.contrib.spiders import CrawlSpider, Rule
from ImageCrawler.items import ImagecrawlerItem
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy import log
import urllib
import re

class ImageSpider(CrawlSpider):
    name = "Image"
    allowed_domains = ["movie.douban.com"]
    start_urls = [
        "http://movie.douban.com/subject/3592854/photos?type=S"
    ]

    rules = [
        Rule(SgmlLinkExtractor(allow=('/subject/\d+/photos\?type=S&start=\d+&sortby=vote', )), process_request='add_cookie'),
        Rule(SgmlLinkExtractor(allow=('/subject/\d+/photos\?size=a&sortby=vote&start', )), follow=True, process_request='add_cookie'),
        Rule(SgmlLinkExtractor(allow=('/photos/photo/\d+/', )), callback='parse_single_image', process_request='add_cookie')
    ]

    def add_cookie(self, request):
        request.replace(cookies=[{'name': 'COOKIE_NAME', 'value': 'VAULE', 'domain': '.douban.com', 'path': '/'},])
        return request

    def parse_single_image(self, response):

        item = ImagecrawlerItem()

        hxs = HtmlXPathSelector(response)
        item["image_url"] = hxs.select("//a[@class='mainphoto']/img/@src").extract()[0]

        d = urllib.urlopen(item["image_url"])

        item["image_info"] = d.info()['Content-Length']

        return item