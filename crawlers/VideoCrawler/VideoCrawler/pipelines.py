# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib
import urllib2
import json

class VideocrawlerPipeline(object):

    def process_item(self, item, spider):
        if item['video_url']:
                values = {
                    'client_id': '67a5c2fe0ac1c936',
                    'video_url': item['video_url']
                }
                data = urllib.urlencode(values)
                url = "https://openapi.youku.com/v2/videos/show_basic.json"
                request = urllib2.Request(url, data)
                response = urllib2.urlopen(request)
                json_load = json.load(response)
                item['video_len'] = json_load['duration']
                return item

class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open('Video.json', 'w')

    def process_item(self, item, spider):

        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
